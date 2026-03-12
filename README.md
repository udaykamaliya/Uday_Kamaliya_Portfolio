# 🚀 Uday Kamaliya – AI/ML Developer Portfolio

A production-ready Flask portfolio website with animated UI, particle canvas, and a Python contact API backend.

---

## 📁 Project Structure

```
uday-portfolio/
├── app.py               ← Flask backend + all portfolio data
├── requirements.txt     ← Python dependencies
├── Procfile             ← For Render / Heroku deployment
├── templates/
│   └── index.html       ← Full animated HTML template
└── README.md
```

---

## 🖥️ Run Locally

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# Open: http://localhost:5000
```

---

## ☁️ Deploy to Render (Free – Recommended)

1. Push this folder to a **GitHub repository**
2. Go to [https://render.com](https://render.com) → New → **Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
5. Click **Deploy** → Your site goes live in ~2 minutes ✅

Live URL will be: `https://your-app-name.onrender.com`

---

## ☁️ Deploy to Railway (Alternative)

1. Go to [https://railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repo → Railway auto-detects Flask
4. Done ✅

---

## ✏️ Customise Your Portfolio

All content is in `app.py` inside the `PORTFOLIO` dict.

- Update **skills**, **projects**, **experience** in `app.py`
- To add a **photo**: place `photo.jpg` in `static/` and update the avatar in `index.html`
- To enable **email sending**: update the `/api/contact` route with SMTP or SendGrid

---

## ✨ Features

- 🎇 Animated particle canvas background (WebGL-free, pure JS)
- 🖱️ Custom cursor with hover effects
- ✍️ Typewriter role animation
- 🐍 Python syntax-highlighted code cards
- 📊 Animated skill progress bars
- 📬 Working contact form via Flask `/api/contact` API
- 🎞️ Scroll-reveal animations throughout
- 📱 Fully responsive (mobile-friendly)
- ⚡ Fast load – no heavy frameworks

---

Built with ❤️ using Python + Flask
