# 🚀 Railway Deployment Guide

## Quick Deploy Steps

### 1. **Deploy to Railway**
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select: `ayeankit/docx-pdf`

### 2. **Add PostgreSQL Database**
1. In your project dashboard, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically provide the connection string

### 3. **Add Redis Database**
1. Click **"New"** again
2. Select **"Database"** → **"Redis"**
3. Railway will provide the Redis connection string

### 4. **Set Environment Variables**
Go to your **API service** and add these variables:

```bash
DATABASE_URL=your_postgres_connection_string_from_railway
REDIS_URL=your_redis_connection_string_from_railway
```

### 5. **Get Connection Strings**
- **PostgreSQL**: Go to PostgreSQL service → "Connect" tab → Copy "Postgres Connection URL"
- **Redis**: Go to Redis service → "Connect" tab → Copy "Redis Connection URL"

## 🔧 Environment Variables

Set these in your Railway API service:

| Variable | Value | Source |
|----------|-------|--------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL service |
| `REDIS_URL` | `redis://...` | Redis service |

## 🧪 Test Your Deployment

### Health Check
```bash
curl https://your-app-name.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-07T...",
  "database": "connected",
  "environment": {
    "database_url_set": true,
    "redis_url_set": true,
    "database_url": "your-db-host",
    "redis_url": "your-redis-host"
  }
}
```

### API Documentation
Visit: `https://your-app-name.railway.app/docs`

## 📝 Usage Examples

### Upload Files
```bash
curl -X POST "https://your-app-name.railway.app/api/v1/jobs" \
  -F "files=@document1.docx" \
  -F "files=@document2.docx"
```

### Download Individual PDF
```bash
curl "https://your-app-name.railway.app/api/v1/jobs/JOB_ID/files/document1.docx/download" \
  -o "document1.pdf"
```

## 🆘 Troubleshooting

### Issue: "connection to server at localhost failed"
**Solution**: Make sure you've set the `DATABASE_URL` environment variable in Railway

### Issue: App not starting
**Solution**: Check Railway logs in the "Deployments" tab

### Issue: Database connection errors
**Solution**: Verify the PostgreSQL connection string format

## 📊 Expected Logs

Successful deployment should show:
```
🚀 Starting DOCX to PDF converter...
📊 Database URL set: True
🔴 Redis URL set: True
📊 Database host: your-db-host
🔴 Redis host: your-redis-host
✅ Database tables created successfully
✅ Application started successfully!
```

## 🎯 Your App URLs

After deployment:
- **Main App**: `https://your-app-name.railway.app`
- **API Docs**: `https://your-app-name.railway.app/docs`
- **Health Check**: `https://your-app-name.railway.app/health`
- **Web UI**: `https://your-app-name.railway.app/`

## ⚡ Quick Commands

```bash
# Test health
curl https://your-app-name.railway.app/health

# View API docs
open https://your-app-name.railway.app/docs

# Upload a file
curl -X POST "https://your-app-name.railway.app/api/v1/jobs" \
  -F "files=@test.docx"
```

---

**Deploy time**: ~5 minutes  
**Cost**: Free tier available  
**Auto-deploy**: Yes (from GitHub) 