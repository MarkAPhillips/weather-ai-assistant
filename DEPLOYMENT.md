# 🚀 FastAPI Weather Assistant - Deployment Guide

## 🚀 Render Deployment (Step-by-Step - No Credit Card Required)

### Prerequisites
1. GitHub account
2. Render account (sign up at render.com)
3. Google API key
4. OpenWeatherMap API key

### Step 1: Prepare Your Repository
```bash
# Make sure your code is committed to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy to Render

#### Deploy from GitHub (No Credit Card Required)
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (no credit card required)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Select your `weather-ai-assistant` repository
6. Render will automatically detect it's a Python app

### Step 3: Configure Service Settings
- **Name**: `weather-ai-assistant`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r server/requirements.txt`
- **Start Command**: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables
In Render dashboard:
1. Go to your service
2. Click on "Environment" tab
3. Add these environment variables:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

### Step 5: Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. You'll get a URL like: `https://your-app-name.onrender.com`
4. Test your API: `https://your-app-name.onrender.com/api/health`

## 🌐 Render Deployment (Alternative)

### Step 1: Connect GitHub
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository

### Step 2: Configure Service
- **Name**: `weather-ai-assistant`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r server/requirements.txt`
- **Start Command**: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables
```
GOOGLE_API_KEY=your_google_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

## 🚀 Fly.io Deployment (Advanced)

### Step 1: Install Fly CLI
```bash
# macOS
brew install flyctl

# Linux/Windows
curl -L https://fly.io/install.sh | sh
```

### Step 2: Create fly.toml
```toml
app = "weather-ai-assistant"
primary_region = "lax"

[build]

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### Step 3: Deploy
```bash
fly auth login
fly launch
fly secrets set GOOGLE_API_KEY=your_key_here
fly secrets set OPENWEATHER_API_KEY=your_key_here
fly deploy
```

## 🔧 Production Optimizations

### 1. Update CORS Settings
```python
# In server/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Add Health Check Endpoint
Your app already has `/api/health` endpoint for monitoring.

### 3. Environment-Specific Configuration
```python
# Add to server/main.py
import os
from dotenv import load_dotenv

load_dotenv()

# Production settings
if os.getenv("ENVIRONMENT") == "production":
    # Add production-specific configurations
    pass
```

## 📊 Monitoring & Maintenance

### Health Monitoring
- Railway: Built-in monitoring dashboard
- Render: Service logs and metrics
- Fly.io: `fly logs` and `fly status`

### Logs
```bash
# Railway
railway logs

# Render
# Available in dashboard

# Fly.io
fly logs
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Configuration
- Make sure your app uses `$PORT` environment variable
- Railway/Render automatically set this

#### 2. Dependencies
- Ensure all dependencies are in `requirements.txt`
- Use specific versions for production

#### 3. Environment Variables
- Double-check API keys are set correctly
- Test locally with same environment variables

#### 4. CORS Issues
- Update CORS origins for your frontend domain
- Test API endpoints directly

### Debug Commands
```bash
# Test API locally
curl http://localhost:8000/api/health

# Test deployed API
curl https://your-app.railway.app/api/health
```

## 💰 Cost Management

### Railway
- Monitor usage in dashboard
- $5 credit usually covers small apps
- Upgrade to paid plan if needed

### Render
- Free tier has limits
- Consider paid plan for production

### Fly.io
- Monitor usage with `fly status`
- Free tier has generous limits

## 🎯 Next Steps

1. **Deploy your FastAPI backend** using one of the methods above
2. **Update your Angular frontend** to use the deployed API URL
3. **Deploy your Angular frontend** to Netlify/Vercel
4. **Test the complete application** end-to-end
5. **Set up monitoring** and alerts

## 📝 Deployment Checklist

- [ ] Code committed to GitHub
- [ ] Environment variables configured
- [ ] API keys obtained and set
- [ ] Health check endpoint working
- [ ] CORS configured for frontend
- [ ] Monitoring set up
- [ ] Domain configured (optional)

## 🆘 Support

If you encounter issues:
1. Check the platform's documentation
2. Review logs for error messages
3. Test API endpoints manually
4. Verify environment variables
5. Check CORS configuration

Happy deploying! 🚀
