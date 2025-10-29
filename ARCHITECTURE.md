# 🏗️ Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VERCEL CLOUD                             │
│                                                                  │
│  ┌────────────────────────┐      ┌─────────────────────────┐   │
│  │  Backend Project       │      │  Frontend Project        │   │
│  │  seo-analyzer-backend  │      │  seo-analyzer-frontend   │   │
│  │                        │      │                          │   │
│  │  ┌──────────────────┐ │      │  ┌────────────────────┐  │   │
│  │  │   FastAPI        │ │      │  │   Next.js          │  │   │
│  │  │   Python 3.10+   │ │      │  │   TypeScript       │  │   │
│  │  │                  │ │      │  │                    │  │   │
│  │  │  Endpoints:      │ │      │  │  Environment Var:  │  │   │
│  │  │  /analyze        │ │◄─────┼──┤  NEXT_PUBLIC_API_  │  │   │
│  │  │  /docs           │ │      │  │  URL               │  │   │
│  │  └──────────────────┘ │      │  └────────────────────┘  │   │
│  │                        │      │                          │   │
│  │  🌐 URL:               │      │  🌐 URL:                 │   │
│  │  seo-analyzer-backend  │      │  seo-analyzer-frontend   │   │
│  │  .vercel.app           │      │  .vercel.app             │   │
│  └────────────────────────┘      └─────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                              │
                              ▼
                        
                    ┌──────────────┐
                    │   End User   │
                    │   Browser    │
                    └──────────────┘
```

## 📊 Request Flow

1. **User visits**: `https://seo-analyzer-frontend.vercel.app`
2. **Frontend loads**: Next.js app with React UI
3. **User submits text**: Click "Analyze" button
4. **API call**: Frontend → `https://seo-analyzer-backend.vercel.app/analyze`
5. **Backend processes**: SEO analysis, keyword extraction, SERP preview
6. **Response**: JSON data back to frontend
7. **Display**: Results shown in beautiful UI

## 🔐 Environment Variables

### Backend
- **CORS origins**: Configured to accept frontend URL
- **No env variables needed**: All config in `main.py`

### Frontend
- **NEXT_PUBLIC_API_URL**: Backend URL (set in Vercel dashboard)
  - Development: `http://localhost:8000`
  - Production: `https://seo-analyzer-backend.vercel.app`

## 📁 Files Created for Deployment

### Backend
- `vercel.json` - Vercel configuration for Python
- `.vercelignore` - Files to ignore during deployment
- Updated `main.py` - CORS with Vercel URLs

### Frontend
- Updated `next.config.js` - Environment variable support
- Updated `page.tsx` - Dynamic API URL
- `.env.local.example` - Template for local env vars

### Documentation
- `DEPLOYMENT.md` - Complete deployment guide
- `deploy-vercel.sh` - Automated deployment script
- `ARCHITECTURE.md` - This file!

## 🚦 Why Separate Deployments?

✅ **Different Runtimes**: Python (FastAPI) vs Node.js (Next.js)
✅ **Independent Scaling**: Scale backend/frontend separately
✅ **Better Organization**: Clear separation of concerns
✅ **Easier Debugging**: Isolated logs and errors
✅ **Flexible Updates**: Deploy changes independently

## 🔄 CI/CD Integration (Optional)

Connect both projects to GitHub for automatic deployments:

1. **Push to GitHub**: Commit your code
2. **Import to Vercel**: Connect GitHub repo
3. **Auto-deploy**: Every push triggers deployment
4. **Preview URLs**: PRs get preview deployments

### GitHub Setup
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/seo-analyzer.git
git push -u origin main
```

Then in Vercel:
1. New Project → Import from GitHub
2. Select repository
3. Set root directory:
   - Backend: `backend/`
   - Frontend: `frontend/`
4. Add environment variables
5. Deploy!

## 🎯 Production Checklist

- [ ] Backend deployed and accessible
- [ ] `/docs` endpoint working (Swagger UI)
- [ ] Frontend deployed
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] CORS configured with frontend URL
- [ ] Test analyze functionality
- [ ] Check browser console for errors
- [ ] Verify SERP preview feature
- [ ] Test all metrics (readability, keywords, etc.)

## 🐛 Common Issues

### CORS Error
**Problem**: Frontend can't connect to backend
**Solution**: Add frontend URL to `allow_origins` in `main.py`

### 404 API Error
**Problem**: Backend not found
**Solution**: Check `NEXT_PUBLIC_API_URL` is correct

### Build Failed
**Problem**: Missing dependencies
**Solution**: Verify `requirements.txt` and `package.json`

### NLTK Data Missing
**Problem**: Backend crashes on startup
**Solution**: Ensure `download_nltk_data.py` runs during build

## 📈 Monitoring

Track your deployments in Vercel:
- **Analytics**: User traffic and performance
- **Logs**: Runtime errors and API calls
- **Metrics**: Response times and error rates
- **Bandwidth**: Data usage and limits

---

**Need help?** See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed steps!
