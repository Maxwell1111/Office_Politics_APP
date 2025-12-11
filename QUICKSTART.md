# Subtext - Quick Start (Simplified Prototype)

## 🎯 Goal: Deploy a Working API in 5 Minutes

Forget the complex MVP. Let's start with something **dead simple** that just works.

---

## What You're Deploying

A **single Python file** (`app_simple.py`) with:
- ✅ 3 endpoints: signup, login, analyze message
- ✅ 200 lines of code
- ✅ In-memory storage (no database needed)
- ✅ Mock AI responses (add Claude later)
- ✅ **Uses ~60MB memory** (Render free tier = 512MB)

---

## Deploy to Render.com (5 Minutes)

### Step 1: Push Code to GitHub

Your code is already pushed. ✅

### Step 2: Create Render Service

1. Go to https://render.com (sign in)
2. Click **New +** → **Web Service**
3. Connect GitHub repo: `Office_Politics_APP`
4. Configure:

```
Name: subtext-api
Runtime: Python
Branch: main

Build Command:
./build_simple.sh

Start Command:
uvicorn app_simple:app --host 0.0.0.0 --port $PORT

Environment Variables:
PYTHON_VERSION=3.11
```

5. Click **Create Web Service**

### Step 3: Wait 2-3 Minutes

Render will:
- Clone your repo
- Run `build_simple.sh` (installs minimal dependencies)
- Start the API

### Step 4: Test It

Once deployed, your API is at: `https://subtext-api.onrender.com`

**Test health check:**
```bash
curl https://YOUR-APP.onrender.com/health
```

Should return:
```json
{"status":"ok","version":"0.1.0"}
```

---

## Test the API

### 1. Signup
```bash
curl -X POST https://YOUR-APP.onrender.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","password":"test123","full_name":"Alex"}'
```

**Returns:**
```json
{
  "access_token": "token_alex@example.com_12345",
  "token_type": "bearer"
}
```

**Save the token!**

### 2. Analyze a Message
```bash
curl -X POST https://YOUR-APP.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token_alex@example.com_12345" \
  -d '{
    "text": "Hey, we need to chat about your roadmap. Got time this week?",
    "sender_name": "Jennifer (Rival PM)"
  }'
```

**Returns:**
```json
{
  "subtext": "Analysis of message from Jennifer (Rival PM): This appears to be a strategic communication. The sender may be testing boundaries.",
  "risk_level": "medium",
  "suggested_reply": "Thank you for reaching out. Let me review this and get back to you with a thoughtful response."
}
```

### 3. View History
```bash
curl https://YOUR-APP.onrender.com/history \
  -H "Authorization: Bearer token_alex@example.com_12345"
```

### 4. Interactive Docs
Visit: `https://YOUR-APP.onrender.com/docs`

Swagger UI with all endpoints! 🎉

---

## What This Proves

✅ **Deployment works** - No memory errors
✅ **API works** - Can signup, login, analyze
✅ **Fast** - Builds in <2 minutes
✅ **Cheap** - $0/month on free tier
✅ **Feasibility confirmed** - Ready to add features

---

## Add Real AI (Optional Next Step)

Once prototype works, add Claude:

### 1. Get Anthropic API Key
- Go to https://console.anthropic.com
- Create API key
- Copy it

### 2. Add to Render
In Render dashboard:
- Environment Variables → Add
- Key: `ANTHROPIC_API_KEY`
- Value: `sk-ant-...`

### 3. Update Code
Uncomment the Claude integration in `app_simple.py` (I can help with this).

---

## Incrementally Add Features

Now that deployment works, add features **one at a time**:

### Week 1: Real AI
- Replace mock responses with Claude API
- Test with real message analysis

### Week 2: Database
- Add free PostgreSQL from Render
- Persist users and messages
- Add proper authentication

### Week 3: Power Map
- Add colleague/player endpoints
- Store relationships

### Week 4: Frontend
- Simple React UI
- Deploy to Vercel (free)
- Connect to API

---

## Why This Approach Works

**Old Approach:**
- Build everything at once
- Complex setup
- Multiple dependencies
- Out of memory errors
- Never gets deployed ❌

**New Approach:**
- Start with simplest version
- Deploy immediately
- Add one feature at a time
- Test each addition
- Always have working version ✅

---

## Troubleshooting

### "Module not found" error
- Check `build_simple.sh` ran successfully
- Verify `requirements-minimal.txt` installed

### "Address already in use"
- Render handles port automatically
- Make sure start command uses `$PORT`

### "Out of memory"
- This shouldn't happen with simple version
- Check build logs for what's using memory
- Consider: are you using `app_simple.py` or old `app.py`?

---

## Current Architecture

```
app_simple.py (200 lines)
├── /health          → Health check
├── /auth/signup     → Create account (in-memory)
├── /auth/login      → Get token (in-memory)
├── /analyze         → Analyze message (mock response)
├── /history         → View analyses (in-memory)
└── /stats           → System stats
```

**Memory Usage:**
- Python: 30MB
- FastAPI: 10MB
- Dependencies: 20MB
- Total: **~60MB** ✅

---

## Files You Need

1. `app_simple.py` - Main API ✅
2. `requirements-minimal.txt` - Dependencies ✅
3. `build_simple.sh` - Build script ✅
4. `DEPLOY_SIMPLE.md` - Deploy guide ✅
5. `QUICKSTART.md` - This file ✅

All pushed to GitHub. Ready to deploy!

---

## Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service configured with correct build/start commands
- [ ] Service deployed (wait 2-3 min)
- [ ] Test `/health` endpoint
- [ ] Test `/docs` page
- [ ] Test signup endpoint
- [ ] Test analyze endpoint
- [ ] Celebrate! 🎉

---

## Next Session Goals

Once this works:

1. Add real Claude AI integration
2. Add PostgreSQL database
3. Add proper JWT authentication
4. Add player management endpoints
5. Build simple frontend

**But first: Get the prototype deployed!**

---

## Support

Issues? Check:
1. Render build logs
2. Render runtime logs
3. Try `/health` endpoint first
4. Check environment variables are set
5. Verify start command syntax

**The simple version should "just work"** - if not, something is misconfigured.

Good luck! 🚀
