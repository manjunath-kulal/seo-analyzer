# 🧠 Writesonic SEO Analyzer

A **FastAPI-powered SEO analysis engine** inspired by **Writesonic's AI content optimization tools**.  
It analyzes text for **readability**, **keyword density**, and **plagiarism similarity** — giving writers instant feedback to improve content quality.

---

## 🚀 Features

✅ **Readability Scoring** — Calculates Flesch Reading Ease to rate text complexity  
✅ **Keyword Analysis** — Extracts top keywords and computes density percentage  
✅ **Plagiarism Detection** — Advanced N-gram similarity matching against sample content  
✅ **Google SERP Preview** — Simulates search result appearance with CTR prediction  
✅ **AI-Powered Suggestions** — Smart recommendations to improve content quality  
✅ **Final SEO Score (0–100)** — Combines all metrics into one performance score  
✅ **Interactive API Docs** — Ready-to-use Swagger UI at `/docs`  
✅ **Modern Frontend** — Built with Next.js 14 and Tailwind CSS

---

## 🧩 Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (modern web framework)
- NLTK (natural language processing)
- TextStat (readability metrics)
- Uvicorn (ASGI server)

**Frontend:**
- Next.js 14 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Axios (HTTP client)

---

## ▶️ Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python download_nltk_data.py

# Start the server
uvicorn main:app --reload
```

Backend will be running at 👉 **http://localhost:8000**  
API Documentation at 👉 **http://localhost:8000/docs**

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at 👉 **http://localhost:3000**

### Quick Start (Both Servers)

```bash
# From project root
./start-all.sh
```

---

## 🧪 Example API Request

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Content marketing is essential for SEO success. Quality content drives organic traffic."}'
```

### ✅ Sample Output

```json
{
  "readability": 82.5,
  "top_keywords": [
    ["content", 2],
    ["marketing", 1],
    ["seo", 1],
    ["quality", 1]
  ],
  "keyword_density": {
    "content": 16.67,
    "marketing": 8.33,
    "seo": 8.33,
    "quality": 8.33
  },
  "plagiarism_score": 2.15,
  "final_score": 95.3,
  "serp_preview": {
    "meta_title": "Content Marketing Essential SEO Success Quality",
    "meta_description": "Content marketing is essential for SEO success. Quality content drives organic traffic.",
    "url_slug": "content-marketing-essential-seo",
    "ctr_score": 78.5
  },
  "suggestions": [
    "Great readability! Your content is easy to understand.",
    "Excellent! Very low plagiarism detected.",
    "Consider adding more targeted keywords for better SEO."
  ]
}
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Analyze text for SEO metrics and quality |
| GET | `/health` | Health check endpoint |
| GET | `/docs` | Interactive API documentation |

---

## 📁 Project Structure

```
writesonic-seo-analyzer/
│
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── download_nltk_data.py   # NLTK data downloader
│   └── test_main.py            # Unit tests
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main UI component
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── package.json           # Node dependencies
│   └── tailwind.config.js     # Tailwind configuration
│
├── start-all.sh               # Start both servers
├── stop-all.sh                # Stop all servers
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

---

## 🧠 Why I Built This

I built this as a demonstration of **Writesonic's AI-powered SEO optimization approach** — showing how content quality can be evaluated automatically using NLP and machine learning techniques.

This project demonstrates:
- **Product thinking** — Understanding the SEO content optimization domain
- **Full-stack development** — Modern Python backend + React frontend
- **AI/ML integration** — Real-world application of NLP algorithms
- **User-centric design** — Clean UI with actionable insights

---

## 🎯 Key Features Explained

### Readability Analysis
Uses the Flesch Reading Ease algorithm to score text from 0-100:
- **90-100**: Very Easy (5th grade)
- **60-70**: Standard (8th-9th grade)
- **0-30**: Very Difficult (College graduate)

### Plagiarism Detection
Employs three detection methods:
1. **N-gram similarity** (5-word sequences)
2. **Sentence-level matching**
3. **Overall sequence comparison**

### Google SERP Preview
Simulates how your content appears in Google search with:
- Meta title optimization
- Meta description generation
- URL slug creation
- CTR (Click-Through Rate) prediction

### AI Suggestions
Provides actionable recommendations based on:
- Readability scores
- Plagiarism levels
- Keyword optimization
- Content length
- SEO best practices

---

## 🧑‍💻 Author

**Manjunath Kulal**

Built with ❤️ to showcase full-stack development and SEO optimization capabilities.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

⭐ **If this project helped you, please give it a star!** It really helps and motivates me to build more amazing projects.

---

## 🚀 Future Enhancements

- [ ] Add user authentication
- [ ] Save analysis history
- [ ] Export reports as PDF
- [ ] Integration with Google Search Console
- [ ] Real-time collaboration features
- [ ] Multi-language support
