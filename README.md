🧠 Writesonic SEO Analyzer — Enhanced with SERP Simulation

A FastAPI + Next.js SEO analyzer built to enhance Writesonic’s AI content optimization suite.

This project adds a Google SERP preview and CTR scoring module, filling a gap in Writesonic’s current SEO workflow and giving content creators actionable insights instantly.

⸻


<p align="center">
  <img src="https://github.com/manjunath-kulal/seo-analyzer/blob/main/Writesonic%20SEO%20Analyzer.png?raw=true" alt="Writesonic SEO Analyzer" width="800"/>
</p>

##🚀 Core Features

```

✅ Readability Scoring — Rates content complexity using Flesch Reading Ease.
✅ Keyword Analysis — Extracts top keywords and computes density.
✅ Plagiarism Detection — N-gram and sentence similarity checks.
✅ 🔹 Google SERP Simulation (Main Highlight) — Generates meta title, meta description, URL slug, and predicts CTR for SEO optimization.
✅ AI-Powered Suggestions — Recommendations to improve SEO and readability.
✅ Final SEO Score (0–100) — Combines all metrics for a quick content performance snapshot.
✅ Interactive API Documentation — Ready-to-use Swagger UI at /docs.

⸻

🧩 Tech Stack

Backend: Python 3.10+, FastAPI, NLTK, TextStat, Uvicorn
Frontend: Next.js 14, TypeScript, Tailwind CSS, Axios

Design Principles Inspired by Writesonic:
	•	Async-first, clean and intuitive UI
	•	Data-driven metrics and actionable insights
	•	Full-stack architecture demonstrating ownership

⸻

🎯 Why I Built This

This project demonstrates:
	•	Founder-like Thinking — Identified a missing SERP feature and implemented it end-to-end.
	•	Ownership & Initiative — Complete full-stack development, testing, and deployment.
	•	Customer Obsession — Provides writers instant, actionable feedback on their content.
	•	AI Enthusiasm & Innovation — Integrated NLP algorithms to calculate SEO metrics and predict CTR.
	•	Data-Driven Decision Making — Combines readability, keywords, plagiarism, and SERP scoring into a single, actionable report.

⸻

🧑‍💻 Quick Start

Backend

cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python download_nltk_data.py
uvicorn main:app --reload

API Docs: http://localhost:8000/docs

Frontend

cd frontend
npm install
npm run dev

App: http://localhost:3000

Quick Start (Both Servers)

./start-all.sh


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
