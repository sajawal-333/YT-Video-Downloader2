#!/usr/bin/env python3
"""
Ultimate YouTube Downloader - Main Application
A production-ready YouTube video downloader with comprehensive error handling
"""

import os
import json
import logging
import tempfile
import shutil
import time
import threading
import queue
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs
import asyncio
import aiofiles
import psutil

from flask import Flask, request, jsonify, send_file, Response, stream_template, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import yt_dlp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """Core YouTube downloader class with advanced error handling"""
    
    def __init__(self):
        self.download_queue = queue.Queue()
        self.active_downloads = {}
        self.download_history = []
        self.max_concurrent_downloads = 5
        self.download_semaphore = threading.Semaphore(self.max_concurrent_downloads)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="yt_downloader_"))
        self.session_cookies = {}
        
        # Start download worker thread
        self.worker_thread = threading.Thread(target=self._download_worker, daemon=True)
        self.worker_thread.start()
        
        logger.info("YouTube Downloader initialized")
    
    def _get_ydl_opts(self, quality: str = 'best', format_type: str = 'mp4', 
                      output_path: str = None, cookies: str = None) -> Dict[str, Any]:
        """Generate yt-dlp options with comprehensive error handling"""
        
        if output_path is None:
            output_path = str(self.temp_dir)
        
        # Base options
        opts = {
            'format': self._get_format_string(quality, format_type),
            'outtmpl': os.path.join(output_path, '%(title)s [%(id)s].%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retries': 3,
            'socket_timeout': 30,
            'extractor_timeout': 30,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'ignoreerrors': False,
            'no_check_certificate': True,
            'prefer_insecure': True,
            'http_headers': self._get_headers(),
            'cookiesfrombrowser': None,
            'cookiefile': None,
            'proxy': None,
        }
        
        # Add cookies if provided
        if cookies:
            try:
                cookie_file = self._save_cookies(cookies)
                opts['cookiefile'] = cookie_file
            except Exception as e:
                logger.warning(f"Failed to process cookies: {e}")
        
        # Post-processing options
        if format_type == 'mp3':
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif format_type == 'mp4':
            opts['merge_output_format'] = 'mp4'
            opts['postprocessors'] = [{
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4',
            }]
        
        return opts
    
    def _get_format_string(self, quality: str, format_type: str) -> str:
        """Generate format string based on quality and type"""
        if format_type == 'mp3':
            return 'bestaudio/best'
        
        if quality == 'best':
            return 'bestvideo+bestaudio/best'
        
        try:
            height = int(quality.replace('p', ''))
            return (
                f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={height}]+bestaudio/"
                f"best[height<={height}]"
            )
        except ValueError:
            return 'bestvideo+bestaudio/best'
    
    def _get_headers(self) -> Dict[str, str]:
        """Get modern headers that work with current YouTube"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        }
    
    def _save_cookies(self, cookies: str) -> str:
        """Save cookies to temporary file"""
        cookie_file = os.path.join(self.temp_dir, f"cookies_{int(time.time())}.txt")
        with open(cookie_file, 'w') as f:
            f.write(cookies)
        return cookie_file
    
    def _validate_url(self, url: str) -> bool:
        """Validate YouTube URL"""
        try:
            parsed = urlparse(url)
            return any(domain in parsed.netloc.lower() for domain in ['youtube.com', 'youtu.be'])
        except Exception:
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe download"""
        import re
        # Remove problematic characters
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        # Ensure it's not too long
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:90] + ext
        # Ensure it starts with a safe character
        if filename and not filename[0].isalnum():
            filename = 'video_' + filename
        return filename
    
    def get_video_info(self, url: str, cookies: str = None) -> Dict[str, Any]:
        """Extract video information without downloading"""
        try:
            if not self._validate_url(url):
                raise ValueError("Invalid YouTube URL")
            
            opts = self._get_ydl_opts(cookies=cookies)
            opts['quiet'] = True
            opts['no_warnings'] = True
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract relevant information
                video_info = {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', '')[:500] + '...' if info.get('description') else '',
                    'formats': self._extract_available_formats(info),
                    'webpage_url': info.get('webpage_url'),
                    'extractor': info.get('extractor'),
                }
                
                logger.info(f"Video info extracted: {video_info['title']}")
                return video_info
                
        except Exception as e:
            logger.error(f"Failed to extract video info: {e}")
            raise
    
    def _extract_available_formats(self, info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract available formats from video info"""
        formats = []
        if 'formats' in info:
            for fmt in info['formats']:
                if fmt.get('height') and fmt.get('ext'):
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'height': fmt.get('height'),
                        'width': fmt.get('width'),
                        'filesize': fmt.get('filesize'),
                        'vcodec': fmt.get('vcodec'),
                        'acodec': fmt.get('acodec'),
                        'fps': fmt.get('fps'),
                    })
        
        # Sort by height (quality)
        formats.sort(key=lambda x: x.get('height', 0), reverse=True)
        return formats[:10]  # Return top 10 formats
    
    def start_download(self, url: str, quality: str = 'best', format_type: str = 'mp4', 
                      cookies: str = None, custom_filename: str = None) -> str:
        """Start a download and return download ID"""
        
        download_id = hashlib.md5(f"{url}_{time.time()}".encode()).hexdigest()[:12]
        
        download_info = {
            'id': download_id,
            'url': url,
            'quality': quality,
            'format_type': format_type,
            'cookies': cookies,
            'custom_filename': custom_filename,
            'status': 'queued',
            'progress': 0,
            'start_time': datetime.now(),
            'error': None,
            'file_path': None,
            'file_size': 0,
        }
        
        self.active_downloads[download_id] = download_info
        self.download_queue.put(download_id)
        
        logger.info(f"Download queued: {download_id} for {url}")
        return download_id
    
    def _download_worker(self):
        """Background worker for processing downloads"""
        while True:
            try:
                download_id = self.download_queue.get(timeout=1)
                with self.download_semaphore:
                    self._process_download(download_id)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Download worker error: {e}")
    
    def _process_download(self, download_id: str):
        """Process a single download"""
        download_info = self.active_downloads.get(download_id)
        if not download_info:
            return
        
        try:
            download_info['status'] = 'downloading'
            download_info['progress'] = 0
            
            # Create progress callback
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        download_info['progress'] = min(progress, 99)
                    elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                        progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                        download_info['progress'] = min(progress, 99)
                elif d['status'] == 'finished':
                    download_info['progress'] = 100
            
            # Setup download options
            opts = self._get_ydl_opts(
                quality=download_info['quality'],
                format_type=download_info['format_type'],
                cookies=download_info['cookies']
            )
            opts['progress_hooks'] = [progress_hook]
            
            # Create output directory
            output_dir = self.temp_dir / download_id
            output_dir.mkdir(exist_ok=True)
            opts['outtmpl'] = str(output_dir / '%(title)s [%(id)s].%(ext)s')
            
            # Download the video
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([download_info['url']])
            
            # Find downloaded file
            downloaded_files = list(output_dir.glob('*'))
            if not downloaded_files:
                raise Exception("No file was downloaded")
            
            file_path = downloaded_files[0]
            file_size = file_path.stat().st_size
            
            if file_size == 0:
                raise Exception("Downloaded file is empty")
            
            # Update download info
            download_info['status'] = 'completed'
            download_info['progress'] = 100
            download_info['file_path'] = str(file_path)
            download_info['file_size'] = file_size
            download_info['end_time'] = datetime.now()
            
            # Add to history
            self.download_history.append(download_info.copy())
            
            logger.info(f"Download completed: {download_id} - {file_path.name}")
            
        except Exception as e:
            download_info['status'] = 'error'
            download_info['error'] = str(e)
            download_info['end_time'] = datetime.now()
            logger.error(f"Download failed: {download_id} - {e}")
    
    def get_download_status(self, download_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific download"""
        return self.active_downloads.get(download_id)
    
    def get_all_downloads(self) -> List[Dict[str, Any]]:
        """Get all active downloads"""
        return list(self.active_downloads.values())
    
    def get_download_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get download history"""
        return self.download_history[-limit:]
    
    def cancel_download(self, download_id: str) -> bool:
        """Cancel a download"""
        if download_id in self.active_downloads:
            download_info = self.active_downloads[download_id]
            if download_info['status'] in ['queued', 'downloading']:
                download_info['status'] = 'cancelled'
                download_info['end_time'] = datetime.now()
                return True
        return False
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old temporary files"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for download_info in self.download_history:
            if download_info.get('end_time') and download_info['end_time'] < cutoff_time:
                file_path = download_info.get('file_path')
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up file {file_path}: {e}")

# Initialize the downloader
downloader = YouTubeDownloader()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
CORS(app)

# Rate limiting
from functools import wraps
from collections import defaultdict
import time

request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests per minute
RATE_WINDOW = 60  # seconds

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        now = time.time()
        
        # Clean old requests
        request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                   if now - req_time < RATE_WINDOW]
        
        # Check rate limit
        if len(request_counts[client_ip]) >= RATE_LIMIT:
            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
        
        request_counts[client_ip].append(now)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Serve the main web interface"""
    return send_file('static/index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'yt_dlp_available': True,
        'active_downloads': len(downloader.active_downloads),
        'queue_size': downloader.download_queue.qsize(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    })

@app.route('/api/video-info', methods=['POST'])
@rate_limit
def get_video_info():
    """Get video information without downloading"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        cookies = data.get('cookies')
        
        video_info = downloader.get_video_info(url, cookies)
        return jsonify({'success': True, 'data': video_info})
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return jsonify({'error': 'Failed to get video information'}), 500

@app.route('/api/download', methods=['POST'])
@rate_limit
def start_download():
    """Start a new download"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        quality = data.get('quality', 'best')
        format_type = data.get('format_type', 'mp4')
        cookies = data.get('cookies')
        custom_filename = data.get('custom_filename')
        
        download_id = downloader.start_download(
            url=url,
            quality=quality,
            format_type=format_type,
            cookies=cookies,
            custom_filename=custom_filename
        )
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'Download started'
        })
        
    except Exception as e:
        logger.error(f"Error starting download: {e}")
        return jsonify({'error': 'Failed to start download'}), 500

@app.route('/api/download/<download_id>/status')
def get_download_status(download_id):
    """Get status of a specific download"""
    status = downloader.get_download_status(download_id)
    if not status:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify({'success': True, 'data': status})

@app.route('/api/downloads')
def get_all_downloads():
    """Get all active downloads"""
    downloads = downloader.get_all_downloads()
    return jsonify({'success': True, 'data': downloads})

@app.route('/api/downloads/history')
def get_download_history():
    """Get download history"""
    limit = request.args.get('limit', 50, type=int)
    history = downloader.get_download_history(limit)
    return jsonify({'success': True, 'data': history})

@app.route('/api/download/<download_id>/cancel', methods=['POST'])
def cancel_download(download_id):
    """Cancel a download"""
    success = downloader.cancel_download(download_id)
    if not success:
        return jsonify({'error': 'Download not found or cannot be cancelled'}), 404
    
    return jsonify({'success': True, 'message': 'Download cancelled'})

@app.route('/api/download/<download_id>/file')
def download_file(download_id):
    """Download the completed file"""
    status = downloader.get_download_status(download_id)
    if not status:
        return jsonify({'error': 'Download not found'}), 404
    
    if status['status'] != 'completed':
        return jsonify({'error': 'Download not completed'}), 400
    
    file_path = status['file_path']
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    filename = os.path.basename(file_path)
    safe_filename = downloader._sanitize_filename(filename)
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=safe_filename,
        mimetype='application/octet-stream'
    )

@app.route('/api/system/info')
def system_info():
    """Get system information"""
    return jsonify({
        'success': True,
        'data': {
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'cpu_usage': psutil.cpu_percent(),
            'active_downloads': len(downloader.active_downloads),
            'queue_size': downloader.download_queue.qsize(),
            'temp_dir_size': sum(f.stat().st_size for f in downloader.temp_dir.rglob('*') if f.is_file())
        }
    })

@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old files"""
    try:
        hours = request.json.get('hours', 24)
        downloader.cleanup_old_files(hours)
        return jsonify({'success': True, 'message': f'Cleaned up files older than {hours} hours'})
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'error': 'Cleanup failed'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting YouTube Downloader on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
