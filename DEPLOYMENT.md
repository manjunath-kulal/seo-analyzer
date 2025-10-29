# 🚀 Vercel Deployment Guide

This guide will help you deploy the SEO Analyzer as two separate Vercel projects.

---

## 📋 Prerequisites

1. [Vercel Account](https://vercel.com/signup)
2. [Vercel CLI](https://vercel.com/cli) installed: `npm i -g vercel`
3. Git repository (optional but recommended)

---

## 🔧 Step 1: Deploy Backend (FastAPI)

### A. Navigate to Backend Directory
```bash
cd backend
```

### B. Login to Vercel (if not already)
```bash
vercel login
```

### C. Deploy Backend
```bash
vercel --prod
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Select your account
- **Link to existing project?** No
- **Project name:** `seo-analyzer-backend` (or your preferred name)
- **Directory:** `./`
- **Override settings?** No

### D. Save Your Backend URL
After deployment, you'll get a URL like:
```
https://seo-analyzer-backend.vercel.app
```
**Copy this URL!** You'll need it for the frontend.

### E. Test Backend
Visit: `https://seo-analyzer-backend.vercel.app/docs`

You should see the FastAPI Swagger documentation.

---

## 🎨 Step 2: Deploy Frontend (Next.js)

### A. Navigate to Frontend Directory
```bash
cd ../frontend
```

### B. Set Environment Variable in Vercel

**Option 1: Via Vercel Dashboard**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Create a new project or select existing
3. Go to **Settings** → **Environment Variables**
4. Add variable:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://seo-analyzer-backend.vercel.app` (your backend URL)
   - **Environments:** Production, Preview, Development (select all)
5. Click **Save**

**Option 2: Via CLI (during deployment)**
```bash
vercel --prod
```

When prompted, you can set the environment variable.

### C. Deploy Frontend
```bash
vercel --prod
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Select your account
- **Link to existing project?** No (unless you created one in dashboard)
- **Project name:** `seo-analyzer-frontend` (or your preferred name)
- **Directory:** `./`
- **Override settings?** No

### D. Add Environment Variable (if not done via dashboard)
If you didn't set the env variable via dashboard:

```bash
vercel env add NEXT_PUBLIC_API_URL production
```
Then paste your backend URL when prompted.

**Redeploy to apply changes:**
```bash
vercel --prod
```

---

## ✅ Step 3: Verify Deployment

### Backend Check
1. Visit: `https://seo-analyzer-backend.vercel.app/docs`
2. Try the `/analyze` endpoint with sample text

### Frontend Check
1. Visit your frontend URL: `https://seo-analyzer-frontend.vercel.app`
2. Enter some text and click **Analyze**
3. Verify the results appear correctly

---

## 🔧 Troubleshooting

### ❌ CORS Error
If you get CORS errors, make sure your backend's `main.py` includes your frontend URL in `allow_origins`:

```python
allow_origins=[
    "http://localhost:3000",
    "https://seo-analyzer-frontend.vercel.app",  # Your actual frontend URL
    "https://*.vercel.app",
]
```

Update and redeploy backend:
```bash
cd backend
vercel --prod
```

### ❌ API Not Found (404)
- Check that `NEXT_PUBLIC_API_URL` is set correctly in Vercel dashboard
- Verify the backend URL is accessible
- Check browser console for the actual URL being called

### ❌ Module Not Found (Backend)
Make sure `requirements.txt` includes all dependencies:
```bash
fastapi
uvicorn
pydantic
textstat
nltk
```

### 🔄 Force Redeploy
```bash
# Backend
cd backend
vercel --prod --force

# Frontend
cd frontend
vercel --prod --force
```

---

## 📊 Project URLs Summary

After deployment, you'll have:

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | `https://seo-analyzer-backend.vercel.app` | FastAPI backend |
| **API Docs** | `https://seo-analyzer-backend.vercel.app/docs` | Swagger UI |
| **Frontend** | `https://seo-analyzer-frontend.vercel.app` | Next.js UI |

---

## 🎯 Environment Variables Reference

### Frontend Environment Variables (Vercel Dashboard)
| Variable | Value | Example |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | Your backend URL | `https://seo-analyzer-backend.vercel.app` |

---

## 🔄 Updating Your Deployment

### Update Backend
```bash
cd backend
# Make your changes
vercel --prod
```

### Update Frontend
```bash
cd frontend
# Make your changes
vercel --prod
```

---

## 🌐 Custom Domain (Optional)

To add custom domains:

1. Go to Vercel Dashboard
2. Select your project
3. Go to **Settings** → **Domains**
4. Add your custom domain
5. Follow DNS configuration instructions

Example:
- Backend: `api.yourdomain.com`
- Frontend: `seo-analyzer.yourdomain.com`

Don't forget to update `NEXT_PUBLIC_API_URL` to your new backend domain!

---

## 🚀 Quick Deploy Commands

```bash
# Deploy everything (run from project root)

# Backend
cd backend && vercel --prod && cd ..

# Frontend (make sure to set NEXT_PUBLIC_API_URL in Vercel dashboard first)
cd frontend && vercel --prod && cd ..
```

---

## 📝 Notes

- **NEXT_PUBLIC_** prefix is required for environment variables accessible in browser
- Backend deployment may take 2-3 minutes for first NLTK data download
- Both projects can be managed independently in Vercel dashboard
- Preview deployments automatically created for git branches

---

## ✨ Success!

Your SEO Analyzer is now live on Vercel! 🎉

- Share your frontend URL with others
- Monitor analytics in Vercel dashboard
- Set up automatic deployments via GitHub integration
