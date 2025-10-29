# 🔧 Troubleshooting Guide

Common issues when deploying to Vercel and how to fix them.

---

## ❌ Issue 1: CORS Error

**Error Message:**
```
Access to fetch at 'https://backend.vercel.app/analyze' from origin 'https://frontend.vercel.app' 
has been blocked by CORS policy
```

**Symptoms:**
- API call fails in browser
- Network tab shows CORS error
- Backend works in Postman/curl but not in browser

**Solution:**

1. **Update `backend/main.py`** to include your frontend URL:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-actual-frontend.vercel.app",  # ← Add this
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Redeploy backend:**
```bash
cd backend
vercel --prod
```

---

## ❌ Issue 2: API Returns 404

**Error Message:**
```
POST https://frontend.vercel.app/analyze 404 (Not Found)
```

**Symptoms:**
- Frontend calls wrong URL
- API endpoint not found
- Browser console shows 404 error

**Solution:**

**Check environment variable is set:**

1. Go to Vercel Dashboard → Your Frontend Project
2. Settings → Environment Variables
3. Verify `NEXT_PUBLIC_API_URL` exists and has correct backend URL
4. If missing or wrong, add/update it:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-backend.vercel.app` (no trailing slash)
   - Environments: All (Production, Preview, Development)

5. **Redeploy frontend:**
```bash
cd frontend
vercel --prod --force
```

**Verify in browser console:**
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
// Should output: https://your-backend.vercel.app
```

---

## ❌ Issue 3: Frontend Still Using localhost

**Symptoms:**
- Frontend tries to call `http://localhost:8000`
- Works locally but fails in production
- Network tab shows localhost URL

**Root Cause:**
Environment variable not properly set or frontend not rebuilt.

**Solution:**

1. **Check environment variable:**
```bash
vercel env ls
```

2. **If not set, add it:**
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Then paste: https://your-backend.vercel.app
```

3. **Redeploy with force flag:**
```bash
cd frontend
vercel --prod --force
```

4. **Clear browser cache:**
   - Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or use incognito mode

---

## ❌ Issue 4: Backend Build Fails

**Error Message:**
```
Error: No Python version specified
```

**Solution:**

1. **Create `backend/runtime.txt`:**
```bash
cd backend
echo "python-3.10" > runtime.txt
```

2. **Redeploy:**
```bash
vercel --prod
```

---

## ❌ Issue 5: NLTK Data Missing

**Error Message:**
```
LookupError: Resource punkt not found
```

**Symptoms:**
- Backend crashes on first request
- NLTK tokenizer fails
- 500 error from backend

**Solution:**

Backend should run `download_nltk_data.py` automatically, but if not:

1. **Check `backend/vercel.json` has build script:**
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ]
}
```

2. **Or download in `main.py` startup:**
```python
import nltk

@app.on_event("startup")
async def startup_event():
    nltk.download('punkt')
    nltk.download('stopwords')
```

3. **Redeploy:**
```bash
cd backend
vercel --prod --force
```

---

## ❌ Issue 6: Environment Variable Not Working

**Symptoms:**
- `process.env.NEXT_PUBLIC_API_URL` is undefined
- Frontend uses fallback localhost URL

**Root Causes & Solutions:**

### A. Missing NEXT_PUBLIC_ prefix
**Wrong:**
```bash
API_URL=https://backend.vercel.app
```

**Correct:**
```bash
NEXT_PUBLIC_API_URL=https://backend.vercel.app
```

### B. Not selected for environment
Check in Vercel dashboard that variable is enabled for:
- ✅ Production
- ✅ Preview  
- ✅ Development

### C. Not redeployed after adding
After adding env var, you MUST redeploy:
```bash
vercel --prod --force
```

---

## ❌ Issue 7: Module Not Found (Frontend)

**Error Message:**
```
Module not found: Can't resolve 'axios'
```

**Solution:**

1. **Check `package.json` has dependencies:**
```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "next": "14.0.0"
  }
}
```

2. **Reinstall locally:**
```bash
cd frontend
npm install
```

3. **Redeploy:**
```bash
vercel --prod
```

---

## ❌ Issue 8: Backend Timeout

**Error Message:**
```
504 Gateway Timeout
```

**Symptoms:**
- Long text analysis fails
- Request takes >10 seconds
- Vercel serverless function timeout

**Solution:**

Vercel free tier has 10s timeout. For longer processing:

1. **Optimize backend code** (already efficient in this project)

2. **Upgrade Vercel plan** for longer timeouts

3. **Or split analysis** into smaller chunks

---

## ❌ Issue 9: Can't Deploy - Vercel CLI Issues

**Error Message:**
```
Error: No framework detected
```

**Solution:**

1. **Make sure you're in correct directory:**
```bash
# For backend
cd backend
vercel --prod

# For frontend  
cd frontend
vercel --prod
```

2. **Explicitly set framework:**
```bash
# Backend
vercel --prod --name seo-analyzer-backend

# Frontend
vercel --prod --name seo-analyzer-frontend
```

3. **Check files exist:**
```bash
# Backend needs
ls main.py vercel.json

# Frontend needs
ls package.json next.config.js
```

---

## ❌ Issue 10: Preview Deployment Works, Production Doesn't

**Root Cause:**
Environment variables not set for production environment.

**Solution:**

1. Check environment variable settings in Vercel dashboard
2. Ensure "Production" is checked
3. Redeploy to production:
```bash
vercel --prod
```

---

## 🔍 Debugging Checklist

### ✅ Backend
- [ ] `vercel.json` exists in backend folder
- [ ] Backend deployed successfully (check Vercel dashboard)
- [ ] `/docs` endpoint accessible (visit in browser)
- [ ] CORS includes frontend URL
- [ ] No errors in Vercel logs

### ✅ Frontend  
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel dashboard
- [ ] Variable enabled for Production environment
- [ ] Frontend deployed successfully
- [ ] `process.env.NEXT_PUBLIC_API_URL` correct in console
- [ ] No errors in Vercel logs

### ✅ Integration
- [ ] Browser Network tab shows correct API URL
- [ ] API request returns 200 OK
- [ ] No CORS errors in console
- [ ] Analysis results display correctly

---

## 🛠️ Useful Commands

### View Logs
```bash
# Backend logs
cd backend
vercel logs

# Frontend logs
cd frontend
vercel logs
```

### Check Environment Variables
```bash
vercel env ls
vercel env pull  # Download to local .env
```

### Force Redeploy
```bash
vercel --prod --force
```

### Remove Deployment
```bash
vercel remove <deployment-url>
```

### Change Project Settings
```bash
vercel project ls  # List projects
vercel link        # Link to existing project
```

---

## 🆘 Still Having Issues?

### Check These:

1. **Vercel Dashboard Logs:**
   - Go to your project
   - Click on deployment
   - View "Build Logs" and "Function Logs"

2. **Browser DevTools:**
   - Console tab: Look for errors
   - Network tab: Check API calls
   - Application tab: Check environment variables

3. **Test Backend Directly:**
```bash
curl -X POST https://your-backend.vercel.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test content for SEO analysis"}'
```

4. **Test CORS:**
```bash
curl -I https://your-backend.vercel.app/analyze \
  -H "Origin: https://your-frontend.vercel.app"
```

### Get Help:

- Check [Vercel Documentation](https://vercel.com/docs)
- Visit [Vercel Community](https://github.com/vercel/vercel/discussions)
- Review [FastAPI on Vercel Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)

---

## 📋 Quick Fix Summary

| Issue | Quick Fix |
|-------|-----------|
| CORS Error | Add frontend URL to `allow_origins` in `main.py` |
| 404 Error | Check `NEXT_PUBLIC_API_URL` in Vercel dashboard |
| Using localhost | Set env var and redeploy with `--force` |
| Build fails | Check `vercel.json` and `package.json` |
| NLTK error | Run `download_nltk_data.py` or download in startup |
| Timeout | Optimize code or upgrade plan |
| Env var not working | Use `NEXT_PUBLIC_` prefix and redeploy |

---

**Most Common Fix:** Redeploy with force flag after making changes!

```bash
vercel --prod --force
```

Good luck! 🚀
