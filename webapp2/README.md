# Ultimate YouTube Downloader

A professional, production-ready YouTube video downloader with comprehensive error handling, modern UI, and advanced features.

## ✨ Features

- **High-Quality Downloads**: Support for up to 4K video quality
- **Multiple Formats**: MP4, MP3, WebM, M4A with customizable quality
- **Real-time Progress**: Live download progress tracking
- **Advanced Error Handling**: Robust error recovery and user feedback
- **Modern UI**: Responsive design with dark/light mode
- **Concurrent Downloads**: Handle multiple downloads simultaneously
- **System Monitoring**: Real-time system status and resource usage
- **Download History**: Track and manage download history
- **Rate Limiting**: Built-in protection against abuse
- **Health Checks**: Production-ready monitoring endpoints

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg (for audio/video processing)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd webapp2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the web interface**
   Open http://localhost:5000 in your browser

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   Open http://localhost:5000 in your browser

### Using Docker directly

1. **Build the image**
   ```bash
   docker build -t youtube-downloader .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 youtube-downloader
   ```

## ☁️ Cloud Deployment

### Railway (Recommended)

1. **Fork this repository**
2. **Go to [Railway.app](https://railway.app)**
3. **Connect your GitHub account**
4. **Select this repository**
5. **Deploy automatically**

### Render

1. **Fork this repository**
2. **Go to [Render.com](https://render.com)**
3. **Create new Web Service**
4. **Connect your repository**
5. **Configure:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Heroku

1. **Install Heroku CLI**
2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

## 📋 API Documentation

### Endpoints

#### Health Check
```http
GET /api/health
```
Returns system health status and metrics.

#### Get Video Information
```http
POST /api/video-info
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "cookies": "optional_cookies_string"
}
```

#### Start Download
```http
POST /api/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "quality": "1080p",
  "format_type": "mp4",
  "cookies": "optional_cookies_string",
  "custom_filename": "optional_custom_name"
}
```

#### Get Download Status
```http
GET /api/download/{download_id}/status
```

#### Get All Downloads
```http
GET /api/downloads
```

#### Cancel Download
```http
POST /api/download/{download_id}/cancel
```

#### Download File
```http
GET /api/download/{download_id}/file
```

#### System Information
```http
GET /api/system/info
```

#### Cleanup Files
```http
POST /api/cleanup
Content-Type: application/json

{
  "hours": 24
}
```

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DEBUG=False

# Server Configuration
PORT=5000
HOST=0.0.0.0

# Download Configuration
MAX_CONCURRENT_DOWNLOADS=5
MAX_FILE_SIZE=4294967296
CLEANUP_INTERVAL_HOURS=24

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
```

## 🛠️ Development

### Local Development

1. **Set up development environment**
   ```bash
   export FLASK_ENV=development
   export DEBUG=True
   ```

2. **Run with auto-reload**
   ```bash
   python app.py
   ```

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

### Code Quality

- **Format code**: `black .`
- **Lint code**: `flake8 .`
- **Type checking**: `mypy .`

## 🚨 Troubleshooting

### Common Issues

#### Download Fails
- **Check URL validity**: Ensure it's a valid YouTube URL
- **Try different quality**: Some videos may not have all qualities
- **Check network**: Ensure stable internet connection
- **Review logs**: Check `youtube_downloader.log` for errors

#### Memory Issues
- **Reduce concurrent downloads**: Lower `MAX_CONCURRENT_DOWNLOADS`
- **Use lower quality**: Higher quality = larger memory usage
- **Monitor system resources**: Check `/api/system/info`

#### FFmpeg Errors
- **Install FFmpeg**: Ensure FFmpeg is properly installed
- **Check PATH**: Verify FFmpeg is in system PATH
- **Update FFmpeg**: Use latest version

#### Rate Limiting
- **Check limits**: Review rate limiting settings
- **Use proxy**: Configure proxy for IP rotation
- **Wait and retry**: Respect rate limits

### Logs

Application logs are written to:
- **Console**: Real-time output
- **File**: `youtube_downloader.log`

### Health Checks

Monitor application health:
```bash
curl http://localhost:5000/api/health
```

## 🔒 Security

### Best Practices

- **Change default secret key**: Set unique `SECRET_KEY`
- **Use HTTPS**: Enable SSL in production
- **Configure rate limiting**: Prevent abuse
- **Monitor logs**: Regular log review
- **Update dependencies**: Keep packages updated

### Rate Limiting

Built-in rate limiting protects against abuse:
- **Default**: 10 requests per minute per IP
- **Configurable**: Adjust via environment variables
- **Automatic**: No additional setup required

## 📊 Performance

### Optimization Tips

- **Concurrent downloads**: Adjust based on system resources
- **Quality selection**: Lower quality = faster downloads
- **File cleanup**: Regular cleanup prevents disk space issues
- **Memory monitoring**: Watch memory usage for large downloads

### System Requirements

- **Minimum**: 1GB RAM, 1 CPU core
- **Recommended**: 2GB RAM, 2 CPU cores
- **Storage**: 10GB+ for temporary files

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Make changes**: Follow coding standards
4. **Test thoroughly**: Ensure all tests pass
5. **Submit PR**: Create pull request with description

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .

# Type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes. Please respect YouTube's Terms of Service and only download content you have permission to download.

## 🆘 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check this README
- **API Docs**: Review API documentation above
- **Logs**: Check application logs for errors

---

**Made with ❤️ for the open source community**
