# Render.com Setup Instructions

## CRITICAL: Use Blueprint (Not Manual Service)

Your `render.yaml` file will ONLY be used if you create a Blueprint.

## Steps

### 1. Delete Existing Service (if any)

1. Go to https://dashboard.render.com
2. Find your existing service (probably called "subtext-minimal" or similar)
3. Click on it
4. Settings → Delete Service
5. Confirm deletion

### 2. Create New Blueprint

1. Click "New +" button (top right)
2. Select "Blueprint"
3. Connect to GitHub repo: `Maxwell1111/Office_Politics_APP`
4. Click "Apply"

Render will automatically:
- Read `render.yaml`
- Run build: `pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0`
- Run start: `uvicorn app_minimal:app --host 0.0.0.0 --port $PORT`
- Bind to the PORT environment variable Render provides

### 3. Watch Deployment

You should see in logs:
```
==> Installing dependencies...
Collecting fastapi==0.104.1
Collecting uvicorn==0.24.0
...
==> Starting service...
🚀 App starting up! PORT=10000
✅ FastAPI app initialized
INFO: Uvicorn running on http://0.0.0.0:10000
```

### 4. Test Deployment

Once it says "Live", visit:
- `https://subtext-minimal.onrender.com/health` → Should return `{"status":"ok"}`
- `https://subtext-minimal.onrender.com/` → Should return API info with port

## If Still Failing

### Check These in Render Dashboard

1. **Service Type**: Must be "Web Service" (not Background Worker)
2. **Runtime**: Must be "Python"
3. **Build Command**: Should show the pip install from render.yaml
4. **Start Command**: Should show the uvicorn command from render.yaml
5. **Environment Variables**: PYTHON_VERSION should be 3.11.0

### Manual Service Configuration (If Blueprint Doesn't Work)

If Blueprint fails, create manual service with:

**Build Command:**
```
pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0
```

**Start Command:**
```
uvicorn app_minimal:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
- `PYTHON_VERSION` = `3.11.0`

## Common Issues

### "Port scan timeout"
- App isn't binding to PORT
- Check logs for the startup messages
- Verify `$PORT` is in start command (not `80` or hardcoded value)

### "Module not found"
- Build didn't run
- Check build logs
- Try "Clear build cache & deploy"

### "Out of memory"
- Shouldn't happen with just 2 packages (~40MB)
- If it does, increase to Starter plan

## Current File Structure

```
.
├── app_minimal.py       # The FastAPI app
├── requirements.txt     # fastapi + uvicorn
├── render.yaml         # Deployment config (only used by Blueprint!)
├── README.md
├── LICENSE
└── .gitignore
```

All 3 essential files are in the repo and pushed.
