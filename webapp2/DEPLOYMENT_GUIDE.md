# Ultimate YouTube Downloader - Deployment Guide

This guide covers deploying the Ultimate YouTube Downloader to various platforms and environments.

## 🚀 Quick Deploy Options

### Railway (Recommended - Easiest)

1. **Fork the repository** to your GitHub account
2. **Go to [Railway.app](https://railway.app)**
3. **Sign in** with your GitHub account
4. **Click "New Project"** → "Deploy from GitHub repo"
5. **Select your forked repository**
6. **Wait for deployment** (usually 2-3 minutes)
7. **Your app will be live** at the provided Railway URL

**Advantages:**
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy scaling
- ✅ Built-in monitoring
- ✅ No configuration needed

### Render (Alternative)

1. **Fork the repository** to your GitHub account
2. **Go to [Render.com](https://render.com)**
3. **Create account** and connect GitHub
4. **Click "New +"** → "Web Service"
5. **Connect your repository**
6. **Configure settings:**
   - **Name**: `youtube-downloader` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (750 hours/month)
7. **Click "Create Web Service"**

## 🐳 Docker Deployment

### Local Docker

1. **Build the image:**
   ```bash
   docker build -t youtube-downloader .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 youtube-downloader
   ```

3. **Access at:** http://localhost:5000

### Docker Compose (Recommended)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access at:** http://localhost:5000

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### Docker on Cloud Platforms

#### Railway with Docker

1. **Railway automatically detects Dockerfile**
2. **No additional configuration needed**
3. **Deploy directly from GitHub**

#### Render with Docker

1. **Select "Docker" as environment**
2. **No build command needed**
3. **Start command:**
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300
   ```

## ☁️ Cloud Platform Deployment

### Heroku

1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **Open the app:**
   ```bash
   heroku open
   ```

### Google Cloud Run

1. **Install Google Cloud SDK**
2. **Enable Cloud Run API**
3. **Build and deploy:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/youtube-downloader
   gcloud run deploy --image gcr.io/PROJECT_ID/youtube-downloader --platform managed
   ```

### AWS Elastic Beanstalk

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB application:**
   ```bash
   eb init -p python-3.11 youtube-downloader
   ```

3. **Create environment:**
   ```bash
   eb create youtube-downloader-env
   ```

4. **Deploy:**
   ```bash
   eb deploy
   ```

## 🖥️ VPS Deployment

### Ubuntu/Debian Server

1. **Update system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install dependencies:**
   ```bash
   sudo apt install python3 python3-pip python3-venv nginx ffmpeg -y
   ```

3. **Clone repository:**
   ```bash
   git clone <your-repo-url>
   cd webapp2
   ```

4. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/youtube-downloader.service
   ```

   Add this content:
   ```ini
   [Unit]
   Description=YouTube Downloader
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/your/webapp2
   Environment="PATH=/path/to/your/webapp2/venv/bin"
   ExecStart=/path/to/your/webapp2/venv/bin/gunicorn app:app --bind 0.0.0.0:5000 --workers 2
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start and enable service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start youtube-downloader
   sudo systemctl enable youtube-downloader
   ```

8. **Configure Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/youtube-downloader
   ```

   Add this configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

9. **Enable site and restart Nginx:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/youtube-downloader /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

10. **Set up SSL with Let's Encrypt:**
    ```bash
    sudo apt install certbot python3-certbot-nginx -y
    sudo certbot --nginx -d your-domain.com
    ```

## 🔧 Environment Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
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

# Logging
LOG_LEVEL=INFO
LOG_FILE=youtube_downloader.log
```

### Platform-Specific Configuration

#### Railway
- Environment variables can be set in the Railway dashboard
- No additional configuration needed

#### Render
- Set environment variables in the Render dashboard
- Add build hooks if needed

#### Heroku
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] **Change default secret key**
- [ ] **Enable HTTPS/SSL**
- [ ] **Configure rate limiting**
- [ ] **Set up monitoring**
- [ ] **Regular security updates**
- [ ] **Backup strategy**
- [ ] **Log monitoring**

### SSL/HTTPS Setup

#### Let's Encrypt (Free)
```bash
sudo certbot --nginx -d your-domain.com
```

#### Cloudflare (Recommended)
1. **Add domain to Cloudflare**
2. **Update nameservers**
3. **Enable SSL/TLS encryption mode: Full**
4. **Enable Always Use HTTPS**

## 📊 Monitoring and Maintenance

### Health Checks

Monitor your application health:
```bash
curl https://your-domain.com/api/health
```

### Log Monitoring

Check application logs:
```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u youtube-downloader -f

# Direct
tail -f youtube_downloader.log
```

### Performance Monitoring

Monitor system resources:
```bash
curl https://your-domain.com/api/system/info
```

### Automated Maintenance

Set up cron jobs for cleanup:
```bash
# Add to crontab
0 2 * * * curl -X POST https://your-domain.com/api/cleanup
```

## 🚨 Troubleshooting

### Common Deployment Issues

#### Build Failures
- **Check Python version** (need 3.8+)
- **Verify requirements.txt** is complete
- **Check for missing system dependencies**

#### Runtime Errors
- **Check logs** for specific error messages
- **Verify environment variables** are set correctly
- **Test locally** before deploying

#### Performance Issues
- **Monitor resource usage**
- **Adjust worker count** based on server capacity
- **Enable caching** if needed

#### Network Issues
- **Check firewall settings**
- **Verify port configuration**
- **Test connectivity**

### Debug Commands

```bash
# Test application locally
python app.py

# Check dependencies
pip list

# Test endpoints
curl http://localhost:5000/api/health

# Check system resources
curl http://localhost:5000/api/system/info
```

## 📈 Scaling Considerations

### Horizontal Scaling

- **Load balancer** for multiple instances
- **Database** for session storage
- **Redis** for caching and queues
- **CDN** for static assets

### Vertical Scaling

- **Increase server resources**
- **Optimize application settings**
- **Use more powerful hardware**

### Auto-scaling

- **Cloud platform auto-scaling**
- **Kubernetes deployment**
- **Container orchestration**

## 🔄 Updates and Maintenance

### Updating the Application

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Update dependencies:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Restart application:**
   ```bash
   # Docker
   docker-compose down && docker-compose up -d
   
   # Systemd
   sudo systemctl restart youtube-downloader
   ```

### Backup Strategy

1. **Application code** (Git repository)
2. **Configuration files** (version controlled)
3. **Logs** (rotated and archived)
4. **Database** (if using one)

### Monitoring Strategy

1. **Application health** (health check endpoints)
2. **System resources** (CPU, memory, disk)
3. **Error rates** (log monitoring)
4. **User activity** (analytics)

---

## 🆘 Support

If you encounter issues:

1. **Check the logs** for error messages
2. **Review this deployment guide**
3. **Test locally** to isolate issues
4. **Check platform-specific documentation**
5. **Create an issue** in the GitHub repository

**Happy deploying! 🚀**
