# 🚀 Deployment Guide for DOCX to PDF Converter

## 📋 Quick Deploy Options

### **Option 1: Railway (Recommended)**
**Best for:** Easy deployment with PostgreSQL and Redis included

1. **Fork/Clone this repository**
2. **Go to [Railway.app](https://railway.app)**
3. **Connect your GitHub account**
4. **Click "New Project" → "Deploy from GitHub repo"**
5. **Select your repository**
6. **Add PostgreSQL database:**
   - Go to your project
   - Click "New" → "Database" → "PostgreSQL"
7. **Add Redis:**
   - Click "New" → "Database" → "Redis"
8. **Set Environment Variables:**
   ```
   DATABASE_URL=your_postgres_connection_string
   REDIS_URL=your_redis_connection_string
   ```
9. **Deploy!** Your app will be available at `https://your-app-name.railway.app`

---

### **Option 2: Render**
**Best for:** Containerized deployment with good free tier

1. **Go to [Render.com](https://render.com)**
2. **Sign up and connect GitHub**
3. **Click "New" → "Web Service"**
4. **Connect your repository**
5. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
6. **Add PostgreSQL database**
7. **Add Redis instance**
8. **Set environment variables**
9. **Deploy!**

---

### **Option 3: Heroku**
**Best for:** Classic deployment (requires credit card for add-ons)

1. **Install Heroku CLI**
2. **Login:** `heroku login`
3. **Create app:** `heroku create your-app-name`
4. **Add PostgreSQL:** `heroku addons:create heroku-postgresql:mini`
5. **Add Redis:** `heroku addons:create heroku-redis:mini`
6. **Set config vars:**
   ```bash
   heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)
   heroku config:set REDIS_URL=$(heroku config:get REDIS_URL)
   ```
7. **Deploy:** `git push heroku main`
8. **Scale workers:** `heroku ps:scale worker=1`

---

### **Option 4: DigitalOcean App Platform**
**Best for:** Professional deployment with good scaling

1. **Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)**
2. **Connect your GitHub repository**
3. **Configure the app with the provided `render.yaml`**
4. **Add PostgreSQL and Redis databases**
5. **Deploy!**

---

## 🔧 Environment Variables

Set these in your deployment platform:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port/0
API_HOST=0.0.0.0
API_PORT=8000
```

## 📁 Required Files

The repository includes all necessary deployment files:
- ✅ `Dockerfile` - Container configuration
- ✅ `docker-compose.yml` - Local development
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Heroku deployment
- ✅ `runtime.txt` - Python version
- ✅ `railway.json` - Railway configuration
- ✅ `render.yaml` - Render configuration

## 🌐 After Deployment

Your app will be available at:
- **Main API:** `https://your-app.railway.app`
- **Health Check:** `https://your-app.railway.app/health`
- **API Docs:** `https://your-app.railway.app/docs`
- **Web UI:** `https://your-app.railway.app/`

## 📝 Usage Examples

### Upload Files:
```bash
curl -X POST "https://your-app.railway.app/api/v1/jobs" \
  -F "files=@document1.docx" \
  -F "files=@document2.docx"
```

### Download Individual PDF:
```bash
curl "https://your-app.railway.app/api/v1/jobs/JOB_ID/files/document1.docx/download" \
  -o "document1.pdf"
```

## 🆘 Troubleshooting

### Common Issues:
1. **Database connection failed** - Check DATABASE_URL
2. **Redis connection failed** - Check REDIS_URL
3. **File upload errors** - Check storage permissions
4. **Worker not processing** - Ensure Celery worker is running

### Health Check:
Visit `/health` to verify your deployment is working.

---

## 🎯 Recommended: Railway

**Why Railway is best for this app:**
- ✅ Free PostgreSQL and Redis included
- ✅ Automatic HTTPS
- ✅ Easy environment variable management
- ✅ Built-in monitoring
- ✅ Automatic deployments from GitHub
- ✅ No credit card required for basic usage

**Deploy time:** ~5 minutes
**Cost:** Free tier available 