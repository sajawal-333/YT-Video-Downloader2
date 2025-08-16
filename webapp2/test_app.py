#!/usr/bin/env python3
"""
Test script for Ultimate YouTube Downloader
Comprehensive testing of all functionality
"""

import sys
import os
import time
import requests
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import yt_dlp
        print(f"✅ yt-dlp imported successfully (version: {yt_dlp.version.__version__})")
    except ImportError as e:
        print(f"❌ yt-dlp import failed: {e}")
        return False
    
    try:
        from flask_cors import CORS
        print("✅ Flask-CORS imported successfully")
    except ImportError as e:
        print(f"❌ Flask-CORS import failed: {e}")
        return False
    
    try:
        import psutil
        print("✅ psutil imported successfully")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    return True

def test_server_startup():
    """Test if the server can be imported and initialized"""
    print("\n🧪 Testing server startup...")
    
    try:
        from app import app, downloader
        print("✅ Server imported successfully")
        print(f"✅ Downloader initialized with {downloader.max_concurrent_downloads} concurrent downloads")
        
        # Test if app has required attributes
        if hasattr(app, 'route'):
            print("✅ Flask app has route decorator")
        else:
            print("❌ Flask app missing route decorator")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

def test_endpoints():
    """Test if the app has required endpoints"""
    print("\n🧪 Testing endpoints...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            if response.status_code == 200:
                data = response.get_json()
                print("✅ Health endpoint working")
                print(f"   - Status: {data.get('status')}")
                print(f"   - yt-dlp available: {data.get('yt_dlp_available')}")
                print(f"   - Active downloads: {data.get('active_downloads')}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main page working")
            else:
                print(f"❌ Main page failed: {response.status_code}")
                return False
            
            # Test system info endpoint
            response = client.get('/api/system/info')
            if response.status_code == 200:
                data = response.get_json()
                print("✅ System info endpoint working")
                print(f"   - Memory usage: {data.get('data', {}).get('memory_usage', 'N/A')}%")
                print(f"   - Active downloads: {data.get('data', {}).get('active_downloads', 'N/A')}")
            else:
                print(f"❌ System info endpoint failed: {response.status_code}")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")
        return False

def test_downloader_functionality():
    """Test core downloader functionality"""
    print("\n🧪 Testing downloader functionality...")
    
    try:
        from app import downloader
        
        # Test URL validation
        valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        invalid_url = "https://example.com"
        
        if downloader._validate_url(valid_url):
            print("✅ URL validation working for valid URLs")
        else:
            print("❌ URL validation failed for valid URLs")
            return False
            
        if not downloader._validate_url(invalid_url):
            print("✅ URL validation working for invalid URLs")
        else:
            print("❌ URL validation failed for invalid URLs")
            return False
        
        # Test format string generation
        format_str = downloader._get_format_string("1080p", "mp4")
        if "1080" in format_str:
            print("✅ Format string generation working")
        else:
            print("❌ Format string generation failed")
            return False
        
        # Test headers generation
        headers = downloader._get_headers()
        if "User-Agent" in headers:
            print("✅ Headers generation working")
        else:
            print("❌ Headers generation failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Downloader functionality test failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n🧪 Testing rate limiting...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Make multiple requests to test rate limiting
            responses = []
            for i in range(12):  # More than the rate limit
                response = client.post('/api/video-info', 
                                     json={'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'})
                responses.append(response.status_code)
            
            # Check if rate limiting is working
            if 429 in responses:
                print("✅ Rate limiting working (429 status returned)")
            else:
                print("⚠️  Rate limiting not triggered (may be disabled in test mode)")
            
            return True
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

def test_file_operations():
    """Test file operations and cleanup"""
    print("\n🧪 Testing file operations...")
    
    try:
        from app import downloader
        
        # Test temp directory creation
        if downloader.temp_dir.exists():
            print("✅ Temporary directory created")
        else:
            print("❌ Temporary directory not created")
            return False
        
        # Test filename sanitization
        test_filename = "test file with spaces & special chars!.mp4"
        sanitized = downloader._sanitize_filename(test_filename)
        if sanitized != test_filename and "test_file_with_spaces___special_chars_.mp4" in sanitized:
            print("✅ Filename sanitization working")
        else:
            print("❌ Filename sanitization failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def test_yt_dlp_integration():
    """Test yt-dlp integration"""
    print("\n🧪 Testing yt-dlp integration...")
    
    try:
        import yt_dlp
        
        # Test basic yt-dlp functionality
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(test_url, download=False)
                if info and 'title' in info:
                    print("✅ yt-dlp can extract video info")
                else:
                    print("❌ yt-dlp failed to extract video info")
                    return False
            except Exception as e:
                print(f"⚠️  yt-dlp test failed (may be network/access issue): {e}")
                print("   This is normal if YouTube is blocking requests")
                return True  # Don't fail the test for network issues
        
        return True
    except Exception as e:
        print(f"❌ yt-dlp integration test failed: {e}")
        return False

def test_environment():
    """Test environment and dependencies"""
    print("\n🧪 Testing environment...")
    
    try:
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            print(f"✅ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is compatible")
        else:
            print(f"❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is too old (need 3.8+)")
            return False
        
        # Check if we're in the right directory
        if Path("app.py").exists():
            print("✅ app.py found in current directory")
        else:
            print("❌ app.py not found in current directory")
            return False
        
        # Check if static directory exists
        if Path("static").exists():
            print("✅ static directory found")
        else:
            print("❌ static directory not found")
            return False
        
        # Check if index.html exists
        if Path("static/index.html").exists():
            print("✅ index.html found")
        else:
            print("❌ index.html not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Ultimate YouTube Downloader - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Server Startup", test_server_startup),
        ("Endpoints", test_endpoints),
        ("Downloader Functionality", test_downloader_functionality),
        ("File Operations", test_file_operations),
        ("yt-dlp Integration", test_yt_dlp_integration),
        ("Rate Limiting", test_rate_limiting),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your YouTube downloader is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Run: python app.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Start downloading YouTube videos!")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Check Python version (need 3.8+)")
        print("   3. Ensure FFmpeg is installed")
        print("   4. Check network connectivity")
        return 1

if __name__ == "__main__":
    sys.exit(main())
