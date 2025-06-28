# HRX‑28 Mama Developer — Learning Companion Bookmarklet

> A single‑click bookmarklet that injects AI‑powered study aides, mood tracking, quizzes and fun incentives directly onto any Udemy course page.<br>
**Note:-** Currently working on Udemy Courses Only.
---

## ✨ Features

| Category              | What it does                                                                                                                      |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Sentiment Monitor** | Real‑time webcam‑based affect detection via a FastAPI backend; console table updates every second and pauses with <kbd>Esc</kbd>. |
| **Course Analyzer**   | Uses Cohere Llama to summarise modules, highlight drawbacks and outline learning outcomes in <180 words.                          |
| **Module Checklist**  | Auto‑detects section titles; tick completed items and persist progress in `localStorage`.                                         |
| **Project Ideas**     | Generates three DIY projects tailored to your selected modules.                                                                   |
| **Quiz Me**           | Builds 5 MCQs (2 easy / 2 medium / 1 hard) for chosen modules, auto‑grades and awards **tokens**.                                 |
| **Daily Question**    | One timed logical/quantitative aptitude MCQ per day; +10 tokens on a correct answer.                                              |
| **Meme Generator**    | Spend 1 token to unlock a fresh Imgflip meme with AI‑written captions on the course topic.                                        |
| **GitHub Evaluator**  | Paste a repo URL and receive constructive feedback plus a 1‑10 rating.                                                            |
| **Gamification**      | Earn tokens via quizzes & daily question, spend them on memes; token badge always visible.                                        |

---

## 🔧 Quick Start

1. **Clone or download** this repo (or simply reference the hosted file on jsDelivr).
2. **Install dependencies** for sentiment detection backend:

   ```bash
   pip install -r requirements.txt
   ```
3. **Start the sentiment‑analysis backend** (Python ≥ 3.9):

   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```

   This exposes `/start`, `/stop` and `/latest` endpoints that the bookmarklet polls.
4. **Create the bookmarklet**

   * Add a new bookmark in your browser.
   * Set its *URL / Location* to **one long line**:

     ```javascript
     javascript:(async()=>{await import('https://cdn.jsdelivr.net/gh/tany109043/HRX-28-Mama-Developer@main/script.js?t='+Date.now())})();
     ```
   * Give it a name like **Udemy Buddy** and save.
5. **Open any Udemy course** page, click the floating green ⬤ button (bottom‑right) and explore the panel.

---

## 🗝️ Configuration

| Setting                     | Where                        | Default                 | Notes                                              |
| --------------------------- | ---------------------------- | ----------------------- | -------------------------------------------------- |
| Cohere API Key              | `script.js` → `const apiKey` | Demo key                | Replace with your own key from Cohere dashboard.   |
| Imgflip Username / Password | `script.js` (Meme section)   | Sample creds            | Use personal Imgflip account to avoid rate limits. |
| Sentiment API Base URL      | Top of `script.js`           | `http://localhost:8000` | Change if backend is hosted elsewhere.             |

> **Security tip:** never commit real credentials to a public repo. Consider loading keys from `localStorage` or a server‑side endpoint.

---

## 📂 Project Structure

```
├─ script.js                 # main bookmarklet payload (loads dynamically)
├─ api.py                   # FastAPI backend to manage sentiment process
├─ student_affect_monitor.py# Emotion detection using DeepFace and MediaPipe
├─ requirements.txt         # Python dependencies
├─ README.md                # this file
└─ …
```

---

## 📦 Requirements (for backend)

Create a `requirements.txt` with the following:

```
fastapi
uvicorn
python-multipart
pynput
opencv-python
mediapipe
deepface
scipy
tk
```

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

1. Fork → feature branch → commit with conventional messages.
2. Add/adjust tests if you touch logic.
3. Open a Pull Request describing **what** you changed & **why**.

Bug reports & feature ideas are welcome via Issues.

---

## 📝 License

Released under the **MIT License** © 2025 Shantnu Talokar.

---

## 🙏 Acknowledgements

* [Cohere](https://cohere.ai) for text generation APIs
* [Imgflip](https://imgflip.com/api) for free meme templates
* Open‑source `student_affect_monitor` for the base affect model

> Made with ☕, 👩‍💻 and a little 🤪 to keep learning fun!
