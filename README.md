# HRX‑28 Mama Developer — Learning‑Companion Bookmarklet

*A one‑click bookmarklet that overlays AI study tools, webcam mood tracking, and gamified rewards onto Udemy courses.*

> ⚠️ Note: Only `verifier.js` is public in this GitHub repo.  
> Full logic and backend code are stored locally in two folders:
> - `bookmarklet-secure/` (access logic + frontend UI)
> - `sentiment-analysis/` (Python backend for affect detection)

---

## ✨ Features

| Category              | What It Does |
| --------------------- | ------------ |
| Sentiment Monitor     | Live webcam mood detection using DeepFace & MediaPipe, polled every second. |
| Course Analyzer       | Uses Cohere to summarize modules, drawbacks, and outcomes in ≤180 words. |
| Module Checklist      | Auto-detects section titles; check off and track progress via `localStorage`. |
| Project Ideas         | Suggests 3 DIY projects based on selected modules. |
| Quiz Me               | Auto-generates 5 MCQs (2 Easy, 2 Medium, 1 Hard) with scoring and tokens. |
| Daily Question        | One logical or aptitude MCQ daily; +10 tokens if answered correctly. |
| Meme Generator        | Spend 1 token to unlock a meme via Imgflip with AI-generated caption. |
| GitHub Evaluator      | Enter repo URL to get rating and improvement suggestions. |
| Gamification          | Earn tokens, spend them on memes, track via floating badge. |

---

## 🧩 How It Works

Browser Bookmarklet  
↓  
Loads verifier.js (from GitHub via jsDelivr)  
↓  
Prompts email → sends to http://localhost:3000/check-access  
→ If rejected: blocks load  
→ If approved: injects protected.js (full UI + features)

### Local Services:

- `bookmarklet-secure/`
  - `server.js` – Node.js Express email approval server
  - `protected.js` – Full front-end logic (kept private)
- `sentiment-analysis/`
  - `api.py`, `student_affect_monitor.py`, `requirements.txt` – Python-based webcam sentiment tracker

---

## 🚀 Quick Start

### 1. Access Control Server (Node.js)

    cd bookmarklet-secure
    npm install
    node server.js

- Runs at: http://localhost:3000  
- Admin panel: http://localhost:3000/admin

### 2. Sentiment Analysis API (Python ≥ 3.9)

    cd sentiment-analysis
    pip install -r requirements.txt
    uvicorn api:app --host 0.0.0.0 --port 8000

### 3. Create the Bookmarklet

Add a new browser bookmark and set the URL to:

    javascript:(async()=>{await import('https://cdn.jsdelivr.net/gh/tany109043/HRX-28-Mama-Developer@main/verifier.js?t='+Date.now())})();

---

## 🧪 How to Use

1. Open a Udemy course page.
2. Click the bookmarklet.
3. Enter your email.
4. Approve it in the admin panel.
5. Enjoy the assistant features injected on the page.

---

## ⚙️ Configuration

| Setting                     | File            | Default                | Notes |
|----------------------------|-----------------|------------------------|-------|
| Cohere API Key              | protected.js    | demo key               | Replace with real key |
| Imgflip Username / Password | protected.js    | sample credentials     | Avoid rate limits |
| Sentiment API Base URL      | protected.js    | http://localhost:8000  | Update if hosted |
| Access Control Port         | server.js       | 3000                   | Change if needed |

---

## 📁 Folder Structure

    📁 HRX-28-Mama-Developer/
    ├── verifier.js              # Public bookmarklet loader
    ├── bookmarklet-secure/
    │   ├── server.js            # Email gatekeeping
    │   └── protected.js         # All core functionality
    ├── sentiment-analysis/
    │   ├── api.py
    │   ├── student_affect_monitor.py
    │   └── requirements.txt
    └── README.md

---

## 🧑‍💻 Contributing

1. Fork the repo
2. Make a feature branch
3. Follow conventional commits
4. Open a pull request

---

## 📄 License

MIT License © 2025 Shantnu Talokar

---

## 🙏 Acknowledgements

- Cohere (https://cohere.ai)
- Imgflip (https://imgflip.com/api)
- DeepFace
- MediaPipe

> Built with 💻, ☕, and a little 🤯 to keep learning awesome.
