🧠 **Writesonic SEO Analyzer** — FastAPI + Next.js

This project provides instant SEO analysis, Google SERP preview, and actionable AI-powered suggestions for your content. Built with FastAPI (Python) and Next.js (TypeScript), it’s ready for local development and Vercel deployment.

---

## 🚀 Features

- **Readability Scoring** (Flesch Reading Ease)
- **Keyword Analysis** (top keywords, density)
- **Plagiarism Detection** (N-gram, sentence similarity)
- **Google SERP Simulation** (meta title, description, URL slug, CTR prediction)
- **AI-Powered Suggestions**
- **Final SEO Score (0–100)**
- **Interactive API Docs** (`/docs`)

---

## 🧩 Tech Stack

- **Backend:** Python 3.10+, FastAPI, NLTK, TextStat
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS

---

## 🏗️ Architecture

```
┌─────────────────────────────┐
│        VERCEL CLOUD         │
│                             │
│ ┌─────────────┐ ┌──────────┐│
│ │  Backend    │ │ Frontend ││
│ │  FastAPI    │ │ Next.js  ││
│ │  /analyze   │ │ Uses     ││
│ │  /docs      │ │ NEXT_PUBLIC_API_URL │
│ └─────────────┘ └──────────┘│
└─────────────────────────────┘
```

---

## ⚡ Quick Start (Local)

**Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python download_nltk_data.py
uvicorn main:app --reload
# Docs: http://localhost:8000/docs
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:3000
```

---

## 🚀 Vercel Deployment (Production)

Deploy as **two separate Vercel projects**:

### 1. Deploy Backend
```bash
cd backend
vercel login
vercel --prod
# Copy backend URL (e.g. https://seo-analyzer-backend.vercel.app)
```

### 2. Set Frontend Environment Variable
- Go to Vercel Dashboard → Frontend Project → Settings → Environment Variables
- Add:
  - Name: `NEXT_PUBLIC_API_URL`
  - Value: `https://seo-analyzer-backend.vercel.app` (your backend URL)
  - Environments: Production, Preview, Development

### 3. Deploy Frontend
```bash
cd frontend
vercel --prod
# Visit your frontend URL
```

---

## 🔐 Environment Variables

**Frontend:**
- `NEXT_PUBLIC_API_URL` — Backend API endpoint
  - Local: `http://localhost:8000`
  - Production: `https://your-backend.vercel.app`

**Backend:**
- No environment variables needed (CORS configured in `main.py`)

---

## 🛠️ Troubleshooting

- **API 404 Error:** Make sure your frontend is calling the correct backend endpoint (e.g. `/analyze`, not `/api/analyze`).
- **CORS Issues:** Ensure your backend CORS origins include your frontend URL.
- **Missing NEXT_PUBLIC_ Prefix:** Always use `NEXT_PUBLIC_API_URL` for frontend API URL.
- **Build Errors:** Run `npm run build` before `npm start` for production.

---

## 📦 Project Structure

```
api/         # Python microservices (optional)
backend/     # FastAPI backend
frontend/    # Next.js frontend
README.md    # This file
DEPLOYMENT.md, ARCHITECTURE.md, etc. # (merged here)
```

---

## 🧑‍💻 Ownership & Innovation

- Founder-like thinking: Identified and built missing SERP feature end-to-end
- Full-stack development, testing, and deployment
- Customer obsession: Instant, actionable feedback for writers
- AI/NLP integration: SEO metrics, CTR prediction
- Data-driven: Combines all metrics into a single report

---

## 📝 Changelog & Docs

All deployment, architecture, and environment info is now in this README. For scripts and advanced troubleshooting, see project files.
⸻

📊 API Example

Request:

curl -X POST "http://localhost:8000/analyze" \
-H "Content-Type: application/json" \
-d '{"text": "Content marketing is essential for SEO success. Quality content drives organic traffic."}'

Sample Output (SERP Highlighted):

{
  "serp_preview": {
    "meta_title": "Content Marketing Essential SEO Success Quality",
    "meta_description": "Content marketing is essential for SEO success. Quality content drives organic traffic.",
    "url_slug": "content-marketing-essential-seo",
    "ctr_score": 78.5
  },
  "readability": 82.5,
  "top_keywords": [["content",2],["marketing",1],["seo",1],["quality",1]],
  "keyword_density": {"content":16.67,"marketing":8.33,"seo":8.33,"quality":8.33},
  "plagiarism_score": 2.15,
  "final_score": 95.3,
  "suggestions": [
    "Great readability! Your content is easy to understand.",
    "Excellent! Very low plagiarism detected.",
    "Consider adding more targeted keywords for better SEO."
  ]
}


⸻

##📂 Project Structure


writesonic-seo-analyzer/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── download_nltk_data.py   # NLTK data downloader
│   └── test_main.py            # Unit tests
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main UI component
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── package.json           # Node dependencies
│   └── tailwind.config.js     # Tailwind configuration
├── start-all.sh               # Start both servers
├── stop-all.sh                # Stop both servers
└── README.md                  # This file


⸻

🎯 Key Wins for Writesonic
	•	SERP Simulation — Directly improves content planning and user engagement insights.
	•	Actionable Feedback — Combines readability, plagiarism, keywords, and SERP analysis in one tool.
	•	Tech & Culture Fit — Full-stack, async-friendly, data-driven, innovative, and founder-like approach, just like Writesonic values.
	•	Remote-Ready & Self-Managed — Can run end-to-end without synchronous coordination, matching their async-first culture.

⸻

🧑‍💻 Author

Manjunath Kulal — Full-stack developer and AI enthusiast passionate about NLP-driven content optimization.

⸻

🚀 Future Enhancements
	•	Add user authentication and personalized analysis history
	•	Export reports as PDF
	•	Integrate with Google Search Console
	•	Real-time collaboration for teams
	•	Multi-language content support

⸻
