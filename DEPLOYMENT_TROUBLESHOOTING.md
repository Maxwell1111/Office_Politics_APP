# Render.com Deployment Troubleshooting Guide

## Common Error: "Exited with status 1"

### ✅ FIXES APPLIED:

#### 1. **Fixed: npm install missing devDependencies**
**Problem:** Webpack and build tools were in `devDependencies`, but Docker's `npm install` only installs `dependencies` in production.

**Solution:**
```dockerfile
# OLD (fails):
RUN npm install

# NEW (works):
RUN npm install --include=dev
```

#### 2. **Fixed: Missing build tools for cryptography**
**Problem:** Alpine Linux missing compilers needed for `cryptography` package.

**Solution:** Added build dependencies:
```dockerfile
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust
```

#### 3. **Added: Node version specification**
**Problem:** Unclear which Node version to use.

**Solution:** Added to `package.json`:
```json
"engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
}
```

---

## 🔍 HOW TO DEBUG FUTURE ISSUES

### Step 1: Check Render Build Logs

**Where to find logs:**
1. Go to Render Dashboard
2. Click on your service
3. Click "Events" tab
4. Click on the failed deployment
5. Scroll to "Build Logs"

**What to look for:**
- ❌ "npm ERR!" = Node/npm issue
- ❌ "ERROR: Command errored out with exit status 1" = Python build issue
- ❌ "ModuleNotFoundError" = Missing Python dependency
- ❌ "Cannot find module" = Missing Node dependency
- ❌ "webpack: command not found" = devDependency issue

---

### Step 2: Analyze Specific Errors

#### Error Type: "webpack: command not found"
**Cause:** Build tool in devDependencies
**Fix:** Use `npm install --include=dev` in Dockerfile

#### Error Type: "error: failed to compile `cryptography`"
**Cause:** Missing C compiler or Rust
**Fix:** Add build dependencies to Dockerfile:
```dockerfile
RUN apk add gcc musl-dev libffi-dev openssl-dev cargo rust
```

#### Error Type: "Module not found: Error: Can't resolve..."
**Cause:** Missing npm package
**Fix:** Check package.json, run `npm install <package>`

#### Error Type: "python: command not found"
**Cause:** Wrong base image
**Fix:** Use `nikolaik/python-nodejs` image

---

### Step 3: Test Locally with Docker

**Build locally to catch issues early:**
```bash
# Build the Docker image
docker build -t politico-test .

# Run it
docker run -p 8080:80 politico-test

# Test the app
curl http://localhost:8080/api/health
```

**If build fails locally, you'll see the exact error!**

---

## 📋 PRE-DEPLOYMENT CHECKLIST

Before pushing to Render, verify:

### Python (requirements.txt):
- [ ] All packages have version pins
- [ ] No conflicting versions
- [ ] Test: `pip install -r requirements.txt` locally

### Node (package.json):
- [ ] `"build"` script exists and is correct
- [ ] All build tools in package.json (even if devDependencies)
- [ ] Node version specified in `"engines"`
- [ ] Test: `npm run build` locally

### Docker (Dockerfile):
- [ ] Base image includes Python AND Node
- [ ] Build dependencies installed (gcc, rust, etc.)
- [ ] `npm install --include=dev` for build step
- [ ] PORT environment variable used (not hardcoded 80)
- [ ] Test: `docker build .` locally

### Render (render.yaml):
- [ ] Runtime set to "docker"
- [ ] Health check path is correct (`/api/health`)
- [ ] Environment variables defined if needed

---

## 🐛 DEBUGGING COMMANDS

### Check what's installed:
```bash
# In Dockerfile, add before the failing step:
RUN which webpack
RUN npm list webpack
RUN python --version
RUN node --version
```

### Verbose npm install:
```bash
RUN npm install --include=dev --loglevel=verbose
```

### Python verbose install:
```bash
RUN pip install -v -r requirements.txt
```

---

## 🔧 COMMON FIXES

### Fix 1: Dependencies in wrong section
**Move build tools from devDependencies to dependencies:**
```json
// BAD (will fail on Render):
"devDependencies": {
    "webpack": "^5.89.0"
}

// GOOD:
"dependencies": {
    "webpack": "^5.89.0"
}

// BETTER (use --include=dev):
// Keep them in devDeps but use correct install command
```

### Fix 2: Node memory issues
**Add to Dockerfile:**
```dockerfile
ENV NODE_OPTIONS="--max-old-space-size=2048"
```

### Fix 3: Python package build failures
**Use pre-built wheels:**
```dockerfile
# Add before pip install
RUN pip install --upgrade pip wheel setuptools
```

---

## 📊 RENDER SERVICE SETTINGS

### Recommended Settings:
- **Runtime:** Docker
- **Branch:** main
- **Auto-Deploy:** Yes
- **Health Check Path:** `/api/health`
- **Plan:** Free (512 MB RAM)

### Environment Variables Needed:
```
ANTHROPIC_API_KEY=sk-ant-... (optional, for AI features)
ENCRYPTION_MASTER_KEY=<generate with Fernet.generate_key()>
PORT=10000 (auto-set by Render)
```

---

## 🚨 WHEN TO CONTACT SUPPORT

If you've tried everything and still failing:

1. **Clear build cache:**
   - Render Dashboard → Settings → "Clear build cache & deploy"

2. **Check Render Status:**
   - Visit status.render.com
   - May be platform-wide issue

3. **Share these logs with support:**
   - Full build logs
   - Dockerfile
   - requirements.txt
   - package.json
   - Error message screenshot

---

## ✅ CURRENT STATUS

**Last Updated:** After fixing npm devDependencies issue

**Build Steps:**
1. ✅ Install Alpine build tools (gcc, rust, etc.)
2. ✅ Install Python packages with pip
3. ✅ Install Node packages with `--include=dev`
4. ✅ Run webpack build
5. ✅ Start uvicorn server on $PORT

**Known Working:**
- Python 3.11
- Node 20
- Alpine Linux
- Docker runtime

---

## 🎯 QUICK FIX SUMMARY

If deployment fails, 90% of time it's one of these:

1. **devDependencies not installed** → Add `--include=dev` to npm install
2. **Missing build tools** → Add gcc, rust to Dockerfile
3. **Wrong PORT** → Use `$PORT` environment variable
4. **Memory limits** → Add NODE_OPTIONS max memory
5. **Package conflicts** → Pin all versions in requirements.txt

**Test locally with Docker before pushing!**
