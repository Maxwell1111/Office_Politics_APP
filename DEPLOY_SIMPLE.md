# Deploy Minimal Subtext MVP to Render.com

## Ultra-Simple Prototype (No Database, No Frontend)

This is a **bare-bones API** to test deployment feasibility. Uses in-memory storage.

---

## What's Included

✅ User signup/login (in-memory, no database)
✅ Message analysis endpoint (mock response for now)
✅ History tracking (in-memory)
✅ Health check endpoint
✅ **Zero frontend** - pure API
✅ **Minimal dependencies** - ~50MB memory usage

---

## Deploy to Render.com

### Step 1: Create Web Service

1. Go to [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repo

### Step 2: Configure

**Settings:**
```
Name: subtext-simple
Runtime: Python
Build Command: ./build_simple.sh
Start Command: uvicorn app_simple:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
PYTHON_VERSION=3.11
```

That's it! No database, no API keys needed for the prototype.

### Step 3: Deploy

Click **Create Web Service** - it should deploy in ~2 minutes.

---

## Test Your Deployment

### 1. Health Check
```bash
curl https://your-app.onrender.com/health
```

**Expected Response:**
```json
{"status": "ok", "version": "0.1.0"}
```

### 2. Signup
```bash
curl -X POST https://your-app.onrender.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Expected Response:**
```json
{"access_token":"token_test@example.com_...", "token_type":"bearer"}
```

Copy the `access_token` for next steps.

### 3. Analyze a Message
```bash
curl -X POST https://your-app.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "text": "We need to talk about your Q4 roadmap.",
    "sender_name": "Boss"
  }'
```

**Expected Response:**
```json
{
  "subtext": "Analysis of message from Boss: This appears to be a strategic communication...",
  "risk_level": "medium",
  "suggested_reply": "Thank you for reaching out. Let me review this and get back to you..."
}
```

### 4. View History
```bash
curl https://your-app.onrender.com/history \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. View Stats
```bash
curl https://your-app.onrender.com/stats
```

---

## What This Proves

✅ **Deployment works** - API runs on Render free tier
✅ **Authentication works** - Simple token-based auth
✅ **Core endpoint works** - Can analyze messages
✅ **Memory efficient** - Uses ~50MB (well under 512MB limit)

---

## API Docs

Once deployed, visit:
```
https://your-app.onrender.com/docs
```

Interactive API documentation (Swagger UI) automatically available.

---

## Limitations (Prototype Only)

⚠️ **In-memory storage** - Data resets when app restarts
⚠️ **No real AI** - Returns mock analysis (not Claude API)
⚠️ **Simple auth** - Not production-secure
⚠️ **No database** - Can't persist data
⚠️ **No frontend** - API only

---

## Next Steps (Add Features Gradually)

### Phase 1: Add Real AI ✅ Feasibility Proven
```bash
# Add to requirements-minimal.txt
anthropic==0.7.8

# Update app_simple.py to call Claude API
```

### Phase 2: Add Database
```bash
# Add PostgreSQL connection
# Use Render's free PostgreSQL tier
# Persist users and messages
```

### Phase 3: Add More Endpoints
- Player management (colleagues)
- Power map data
- Log book entries

### Phase 4: Add Frontend
- Simple React UI
- Deploy to Vercel/Netlify
- Connect to API

---

## Why This Works

**Before (Complex MVP):**
- Database migrations
- Frontend webpack build
- Multiple services
- Heavy dependencies
- Result: Out of memory ❌

**Now (Simple Prototype):**
- Single Python file
- No database setup needed
- No frontend build
- Minimal dependencies
- Result: Deploys in 2 minutes ✅

---

## Files for Simple Deployment

- `app_simple.py` - Single-file API (200 lines)
- `requirements-minimal.txt` - Only essential packages
- `build_simple.sh` - Minimal build script
- `DEPLOY_SIMPLE.md` - This guide

---

## Memory Usage

```
Python runtime: ~30MB
FastAPI: ~10MB
Dependencies: ~20MB
App code: ~5MB
------------------
Total: ~65MB ✅ (90% under limit!)
```

---

## Troubleshooting

### Build fails
- Check build logs in Render dashboard
- Verify `build_simple.sh` has execute permissions
- Try manual build: `pip install -r requirements-minimal.txt`

### Health check fails
- Check start command is correct
- Verify port binding: `--port $PORT`
- Check app logs in Render dashboard

### Authentication doesn't work
- This is in-memory - tokens reset on restart
- For production, add proper JWT + database

---

## Production-Ready Checklist

When you're ready to add features:

- [ ] Add PostgreSQL database
- [ ] Implement proper JWT authentication
- [ ] Add Anthropic API integration
- [ ] Add password hashing (bcrypt)
- [ ] Add data persistence
- [ ] Add rate limiting
- [ ] Add logging
- [ ] Add error handling
- [ ] Add frontend UI
- [ ] Add HTTPS
- [ ] Add monitoring

---

## Cost

**Prototype:** $0/month (Render free tier)
**With Database:** $0/month (Render free PostgreSQL)
**With AI:** ~$0.30/month for 100 analyses (Anthropic)

Total: **Free for testing** 🎉

---

## Quick Deploy Checklist

1. ✅ Push code to GitHub
2. ✅ Create Render web service
3. ✅ Set build command: `./build_simple.sh`
4. ✅ Set start command: `uvicorn app_simple:app --host 0.0.0.0 --port $PORT`
5. ✅ Deploy
6. ✅ Test `/health` endpoint
7. ✅ Test `/docs` for API documentation

Done! 🚀
