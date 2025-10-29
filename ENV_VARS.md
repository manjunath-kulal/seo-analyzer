# 🔐 Environment Variables Reference

## Frontend (.env.local or Vercel Dashboard)

| Variable | Description | Local Value | Production Value | Required |
|----------|-------------|-------------|------------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API endpoint | `http://localhost:8000` | `https://your-backend.vercel.app` | ✅ Yes |

### Setting in Vercel Dashboard

1. Go to your frontend project in Vercel
2. Navigate to **Settings** → **Environment Variables**
3. Click **Add Variable**
4. Enter:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-backend.vercel.app` (your actual backend URL)
   - **Environments**: ✅ Production ✅ Preview ✅ Development
5. Click **Save**
6. **Redeploy** your project for changes to take effect

### Setting Locally

Create `.env.local` in frontend directory:

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

Or copy from example:
```bash
cp .env.local.example .env.local
```

## Backend (No Environment Variables Needed)

The backend doesn't require environment variables for basic deployment. CORS origins are configured directly in `main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://*.vercel.app",
    "https://seo-analyzer-frontend.vercel.app",
]
```

### To Add Custom Frontend URL

If your frontend URL is different, update `main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-custom-frontend.vercel.app",  # Add your URL
    "https://*.vercel.app",
]
```

## 🔍 Verification

### Check Frontend is Using Correct API

**In Browser Console:**
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
```

**In Network Tab:**
- Open DevTools → Network
- Submit analysis
- Check the request URL should be: `https://your-backend.vercel.app/analyze`

### Check Backend CORS

**Test CORS:**
```bash
curl -I -X OPTIONS https://your-backend.vercel.app/analyze \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST"
```

Should return:
```
Access-Control-Allow-Origin: https://your-frontend.vercel.app
Access-Control-Allow-Methods: POST
```

## 🚨 Common Mistakes

### ❌ Missing NEXT_PUBLIC_ Prefix

**Wrong:**
```bash
API_URL=https://backend.vercel.app
```

**Correct:**
```bash
NEXT_PUBLIC_API_URL=https://backend.vercel.app
```

> Environment variables without `NEXT_PUBLIC_` prefix are not exposed to the browser!

### ❌ Hardcoded localhost in Production

**Wrong:**
```typescript
const API_URL = 'http://localhost:8000/analyze';
```

**Correct:**
```typescript
const API_URL = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/analyze`;
```

### ❌ Forgetting to Redeploy After Adding Env Vars

After adding environment variables in Vercel dashboard:
1. Go to **Deployments** tab
2. Click **⋯** on latest deployment
3. Click **Redeploy**

Or use CLI:
```bash
vercel --prod --force
```

### ❌ Wrong Environment Selected

Make sure to add environment variable to **all environments**:
- ✅ Production
- ✅ Preview
- ✅ Development

## 🧪 Testing

### Local Development
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python download_nltk_data.py
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm install
npm run dev
```

### Production Testing
1. Deploy backend first
2. Copy backend URL
3. Add to Vercel frontend env vars
4. Deploy frontend
5. Test on production URL

## 📋 Quick Commands

```bash
# View current Vercel env vars
vercel env ls

# Add new env var
vercel env add NEXT_PUBLIC_API_URL

# Pull env vars to local
vercel env pull

# Remove env var
vercel env rm NEXT_PUBLIC_API_URL
```

## 🎯 Summary

**For Frontend to work in production:**
1. ✅ Deploy backend and get URL
2. ✅ Add `NEXT_PUBLIC_API_URL` in Vercel dashboard
3. ✅ Value = backend URL (e.g., `https://seo-analyzer-backend.vercel.app`)
4. ✅ Select all environments
5. ✅ Redeploy frontend

**For Backend to accept frontend requests:**
1. ✅ Update `allow_origins` in `main.py`
2. ✅ Include frontend URL
3. ✅ Redeploy backend

---

That's it! Your SEO Analyzer should now work perfectly on Vercel! 🚀
