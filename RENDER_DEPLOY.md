# Deploying Subtext to Render.com

## Memory Optimization Fixes

The "out of memory" error on Render's free tier (512MB limit) is caused by webpack building the frontend. I've created **two deployment strategies**:

---

## Strategy 1: API-Only on Render (RECOMMENDED for Free Tier)

Deploy only the backend API to Render.com and host the frontend separately on Vercel/Netlify.

### Why This Works
- Backend only uses ~200MB memory
- Frontend gets served from CDN (fast + free)
- Avoids npm build memory issues

### Steps

#### 1. Deploy API to Render.com

**Using Render Dashboard:**

1. Go to [render.com](https://render.com) and login
2. Click **New +** → **Web Service**
3. Connect your GitHub repo: `Office_Politics_APP`
4. Configure:
   - **Name:** `subtext-api`
   - **Runtime:** `Python`
   - **Build Command:** `./build_render_api_only.sh`
   - **Start Command:** `uvicorn subtext.app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

5. Add Environment Variables:
   ```
   PYTHON_VERSION=3.11
   ANTHROPIC_API_KEY=<your-key>
   JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
   DATABASE_URL=<from render database below>
   IS_TEST=0
   ```

6. Click **Create Web Service**

#### 2. Create PostgreSQL Database

1. In Render Dashboard, click **New +** → **PostgreSQL**
2. Configure:
   - **Name:** `subtext-db`
   - **Database:** `subtext`
   - **Plan:** Free
3. Click **Create Database**
4. Copy the **External Database URL**
5. Add it as `DATABASE_URL` in your web service environment variables

#### 3. Initialize Database

**SSH into Render (or use local connection to external DB):**

```bash
# From your local machine, connect to Render's database
export DATABASE_URL="<external-database-url-from-render>"

# Run migrations
python scripts/init_db.py

# Seed demo data (optional)
python scripts/seed_data.py
```

#### 4. Test API

Your API is now live at: `https://subtext-api.onrender.com`

Test it:
```bash
curl https://subtext-api.onrender.com/api/health
# Should return: OK
```

**API Docs:** `https://subtext-api.onrender.com/api`

#### 5. Deploy Frontend (Separately)

**Option A: Vercel (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd www
vercel --prod

# Set API URL environment variable
vercel env add REACT_APP_API_URL
# Value: https://subtext-api.onrender.com
```

**Option B: Netlify**
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Build and deploy
cd www
npm run build
netlify deploy --prod --dir=dist

# Set API URL in Netlify dashboard
```

**Result:**
- Backend API: `https://subtext-api.onrender.com`
- Frontend: `https://your-app.vercel.app`

---

## Strategy 2: Full Stack on Render (Requires Paid Plan)

Build and serve both backend + frontend from Render. **This requires upgrading to Starter plan ($7/month) for 512MB+ memory.**

### Steps

#### 1. Deploy with Full Build

**render.yaml** (already configured):
```yaml
services:
  - type: web
    name: subtext-api
    buildCommand: "./build_render.sh"
    startCommand: "uvicorn subtext.app:app --host 0.0.0.0 --port $PORT"
    plan: starter  # Change to 'starter' plan
```

#### 2. Upgrade Plan

In Render Dashboard:
1. Go to your web service
2. Click **Settings**
3. Under **Instance Type**, select **Starter** ($7/month)
4. This gives you 2GB RAM - enough for webpack build

#### 3. Deploy

Push to GitHub and Render will automatically rebuild with full frontend.

---

## Strategy 3: Pre-Build Frontend Locally (Free Tier Workaround)

Build the frontend locally, commit the `dist/` folder, and deploy without npm build.

### Steps

#### 1. Build Frontend Locally

```bash
cd www
export NODE_OPTIONS="--max-old-space-size=2048"
npm run build
cd ..
```

#### 2. Commit dist/ Folder

```bash
# Remove dist from .gitignore temporarily
sed -i '' '/dist/d' www/.gitignore

# Commit built frontend
git add www/dist
git commit -m "Add pre-built frontend for Render deployment"
git push
```

#### 3. Create No-Build Script

Create `build_render_prebuild.sh`:
```bash
#!/bin/bash
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir -e .
echo "✅ Using pre-built frontend from www/dist"
```

#### 4. Update Render Build Command

In Render Dashboard:
- **Build Command:** `./build_render_prebuild.sh`

**Downside:** You must rebuild frontend locally every time you change UI code.

---

## Memory Optimization Applied

I've made these optimizations to reduce memory usage:

### 1. **build_render.sh**
- Sets `NODE_OPTIONS="--max-old-space-size=400"` (limits Node to 400MB)
- Uses `npm install --prefer-offline --no-audit --progress=false`
- Reduces npm logging overhead

### 2. **webpack.prod.js**
- Changed `parallel: true` → `parallel: 2` in TerserPlugin
- Added `splitChunks` to break large bundles into smaller pieces
- Limits concurrent minification processes

### 3. **Dockerfile**
- Added same memory optimizations for Docker builds

### 4. **build_render_api_only.sh** (NEW)
- Skips frontend build entirely
- Creates minimal placeholder HTML
- Only installs Python dependencies

---

## Troubleshooting

### "Out of memory" error persists

**Solution:** Use **Strategy 1 (API-Only)** or **Strategy 3 (Pre-build)**

### Database connection fails

Check `DATABASE_URL` format:
```
postgresql://user:password@host:5432/database
```

Render provides this automatically for internal connections, but use "External Database URL" from your local machine.

### API works but no frontend

If using API-only deployment:
1. Check that `www/dist/index.html` exists
2. Deploy frontend separately to Vercel/Netlify
3. Configure CORS to allow your frontend domain

### Frontend needs API URL

Update frontend to point to Render API:
```javascript
// In your frontend config
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://subtext-api.onrender.com';
```

---

## Cost Comparison

| Strategy | Backend Cost | Frontend Cost | Total |
|----------|-------------|---------------|-------|
| API-Only (Strategy 1) | Free (Render) | Free (Vercel) | **$0/month** |
| Full Stack (Strategy 2) | $7 (Starter) | Included | **$7/month** |
| Pre-build (Strategy 3) | Free (Render) | Included | **$0/month** |

---

## Recommended Approach

**For MVP/Testing:** Use **Strategy 1 (API-Only)**
- Free hosting
- Better performance (frontend on CDN)
- Easier to scale independently

**For Production:** Use **Strategy 2 (Full Stack)** with Starter plan
- Simpler deployment (single service)
- Less configuration

---

## Environment Variables Checklist

Make sure these are set in Render dashboard:

- ✅ `PYTHON_VERSION=3.11`
- ✅ `DATABASE_URL=<from-render-postgres>`
- ✅ `ANTHROPIC_API_KEY=<your-key>`
- ✅ `JWT_SECRET_KEY=<random-32-byte-hex>`
- ✅ `IS_TEST=0`
- ✅ `NODE_OPTIONS=--max-old-space-size=400` (only if building frontend)

---

## Database Initialization

After deploying, initialize the database:

```bash
# Option 1: Connect from local machine
export DATABASE_URL="<external-database-url>"
python scripts/init_db.py
python scripts/seed_data.py

# Option 2: Use Render Shell
# In Render dashboard, go to your web service → Shell tab
python scripts/init_db.py
python scripts/seed_data.py
```

---

## Next Steps After Deployment

1. **Test API endpoints:** `https://your-app.onrender.com/api`
2. **Initialize database** (see above)
3. **Test login:** Use demo user `alex@example.com` / `password123`
4. **Deploy frontend** (if using Strategy 1)
5. **Update CORS settings** if frontend is on different domain

---

## Files Added for Render Deployment

- `build_render.sh` - Full build with memory optimization
- `build_render_api_only.sh` - API-only build (no frontend)
- `render.yaml` - Render configuration file
- `RENDER_DEPLOY.md` - This guide
- Updated `Dockerfile` - Memory optimizations
- Updated `www/webpack/webpack.prod.js` - Reduced parallelization

---

## Support

If deployment still fails:
1. Check Render logs in dashboard
2. Verify all environment variables are set
3. Try API-only deployment (Strategy 1)
4. Consider upgrading to Starter plan ($7/month)
