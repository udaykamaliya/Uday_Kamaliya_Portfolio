from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import re, os, json, urllib.request, urllib.parse, traceback

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "uday-portfolio-secret-2025")

# ── Resend API Config (FREE - 100 emails/day) ─────────────────
# Sign up at resend.com → get free API key → add to Render env vars
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
NOTIFY_EMAIL   = os.environ.get("NOTIFY_EMAIL",   "udaykamaliya28@gmail.com")
FROM_EMAIL     = os.environ.get("FROM_EMAIL",      "onboarding@resend.dev")

# ── Visitor Counter ──────────────────────────────────────────────
COUNTER_FILE = os.path.join(os.path.dirname(__file__), "visitor_count.json")

def get_visitor_count():
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r") as f:
                return json.load(f).get("total", 0)
    except:
        pass
    return 0

def increment_visitor():
    try:
        count = get_visitor_count() + 1
        with open(COUNTER_FILE, "w") as f:
            json.dump({"total": count, "updated": datetime.now().isoformat()}, f)
        return count
    except:
        return get_visitor_count()


# ── Email via Resend API ──────────────────────────────────────────
def send_email(name, sender_email, subject, message):
    """Send email using Resend API — works 100% on Render free tier."""

    print(f"\n{'='*50}")
    print(f"📧 Sending email via Resend API...")
    print(f"   RESEND_API_KEY : {'SET ✅' if RESEND_API_KEY else 'MISSING ❌'}")
    print(f"   TO             : {NOTIFY_EMAIL}")
    print(f"   FROM           : {FROM_EMAIL}")
    print(f"{'='*50}")

    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY not set in Render environment variables!")
        print("   → Go to resend.com → sign up free → get API key → add to Render")
        return False

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body{{font-family:'Segoe UI',Arial,sans-serif;background:#0c0e1a;margin:0;padding:20px;}}
    .wrap{{max-width:560px;margin:0 auto;background:#111426;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,.1);}}
    .hdr{{background:linear-gradient(135deg,#7c5cfc,#22d3ee);padding:28px 32px;}}
    .hdr h1{{color:#fff;margin:0;font-size:20px;font-weight:700;}}
    .hdr p{{color:rgba(255,255,255,.8);margin:4px 0 0;font-size:13px;}}
    .bdy{{padding:28px 32px;}}
    .row{{margin-bottom:18px;}}
    .lbl{{font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#7c5cfc;margin-bottom:5px;}}
    .val{{background:#1a1d2e;border:1px solid rgba(255,255,255,.07);border-radius:8px;padding:10px 14px;color:#dde3f0;font-size:14px;}}
    .msg{{background:#1a1d2e;border:1px solid rgba(124,92,252,.25);border-radius:8px;padding:14px;color:#dde3f0;font-size:14px;line-height:1.7;white-space:pre-wrap;}}
    .btn{{display:inline-block;margin-top:20px;background:linear-gradient(135deg,#7c5cfc,#22d3ee);color:#fff;text-decoration:none;padding:11px 26px;border-radius:8px;font-weight:700;font-size:14px;}}
    .ftr{{border-top:1px solid rgba(255,255,255,.06);padding:18px 32px;text-align:center;}}
    .ftr p{{color:#7a869e;font-size:12px;margin:3px 0;}}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <h1>💼 New Portfolio Message</h1>
      <p>Someone reached out via your portfolio contact form</p>
    </div>
    <div class="bdy">
      <div class="row"><div class="lbl">From</div><div class="val">{name}</div></div>
      <div class="row"><div class="lbl">Email</div><div class="val">{sender_email}</div></div>
      <div class="row"><div class="lbl">Subject</div><div class="val">{subject or '(No subject)'}</div></div>
      <div class="row"><div class="lbl">Message</div><div class="msg">{message}</div></div>
      <div style="text-align:center">
        <a href="mailto:{sender_email}?subject=Re: {subject}" class="btn">✉️ Reply to {name}</a>
      </div>
    </div>
    <div class="ftr">
      <p>Received on {datetime.now().strftime('%d %B %Y at %I:%M %p')}</p>
      <p>Sent via <strong style="color:#a78bfa">uday.dev</strong> portfolio</p>
    </div>
  </div>
</body>
</html>
    """

    try:
        payload = json.dumps({
            "from":    FROM_EMAIL,
            "to":      [NOTIFY_EMAIL],
            "reply_to": sender_email,
            "subject": f"Portfolio Contact: {subject or 'New Message'} — from {name}",
            "html":    html_body,
            "text":    f"From: {name} <{sender_email}>\nSubject: {subject}\n\n{message}"
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data    = payload,
            headers = {
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json"
            },
            method = "POST"
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            print(f"✅ Email sent! Resend ID: {result.get('id')}")
            return True

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ Resend API error {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"❌ Email failed: {e}")
        print(traceback.format_exc())
        return False


# ── Portfolio Data ────────────────────────────────────────────────
PORTFOLIO = {
    "name": "Uday Kamaliya",
    "title": "AI/ML Developer",
    "tagline": "Building intelligent systems that solve real-world problems.",
    "bio": "Passionate AI/ML and Data Science enthusiast exploring intelligent systems and building practical machine learning applications. Focused on solving real-world problems using data, automation, and AI technologies.",
    "email": "udaykamaliya28@gmail.com",
    "github": "https://github.com/udaykamaliya",
    "linkedin": "https://www.linkedin.com/in/uday-kamaliya-893917271/",
    "location": "Gujarat, India",
    "available": True,
    "skills": [
        {"category": "Languages", "icon": "🐍", "color": "violet", "skills_list": [
            {"name": "Python", "level": 85},
            {"name": "SQL", "level": 70},
            {"name": "HTML/CSS", "level": 65},
        ]},
        {"category": "AI / ML", "icon": "🧠", "color": "cyan", "skills_list": [
            {"name": "Scikit-learn", "level": 80},
            {"name": "Pandas / NumPy", "level": 82},
            {"name": "LangChain / RAG", "level": 65},
            {"name": "Random Forest", "level": 78},
        ]},
        {"category": "Tools", "icon": "🛠️", "color": "pink", "skills_list": [
            {"name": "Flask", "level": 72},
            {"name": "Tableau", "level": 75},
            {"name": "Jupyter / Colab", "level": 88},
            {"name": "Git / GitHub", "level": 70},
        ]},
    ],
    "projects": [
        {
            "id": 1, "num": "01", "icon": "🤖", "color": "violet",
            "title": "SmartPredict ML Pipeline", "subtitle": "RAG-based Chatbot",
            "description": "Built an AI-powered chatbot using Retrieval-Augmented Generation to answer queries from Amazon product data. Combines LLM capabilities with real-time vector search for accurate, context-aware responses.",
            "tags": [{"label":"Python","color":"v"},{"label":"LangChain","color":"c"},{"label":"RAG","color":"v"},{"label":"OpenAI","color":"p"},{"label":"FAISS","color":"g"}],
            "github": "https://github.com/udaykamaliya", "featured": True,
        },
        {
            "id": 2, "num": "02", "icon": "💧", "color": "cyan",
            "title": "Water Potability Prediction", "subtitle": "ML + Flask Web App",
            "description": "Developed a machine learning model using Random Forest and Flask to predict whether water is safe for drinking based on chemical parameters. Deployed as a web app for real-world accessibility.",
            "tags": [{"label":"Python","color":"v"},{"label":"Random Forest","color":"c"},{"label":"Flask","color":"o"},{"label":"Scikit-learn","color":"g"},{"label":"Pandas","color":"p"}],
            "github": "https://github.com/udaykamaliya", "featured": True,
        },
        {
            "id": 3, "num": "03", "icon": "🌾", "color": "green",
            "title": "Agriculture Data Dashboard", "subtitle": "EDA + Tableau Visualisation",
            "description": "Performed exploratory data analysis on farming datasets and built interactive dashboards in Tableau to extract insights on crop yield, revenue, and farming methods across regions.",
            "tags": [{"label":"Python","color":"v"},{"label":"Tableau","color":"g"},{"label":"Pandas","color":"c"},{"label":"Matplotlib","color":"p"},{"label":"EDA","color":"o"}],
            "github": "https://github.com/udaykamaliya", "featured": False,
        },
    ],
    "experience": [
        {"period":"2024 – Present","role":"AI/ML Developer","company":"Self-directed Learning & Projects","current":True,"desc":"Building AI/ML projects covering NLP, classification models, data pipelines, and RAG systems. Continuously learning from industry research, open-source communities, and hands-on experimentation."},
        {"period":"2023 – 2024","role":"Data Analysis & Visualisation","company":"Academic & Personal Projects","current":False,"desc":"Completed end-to-end data analysis projects — from data cleaning and feature engineering to building Tableau dashboards on agriculture and environmental datasets."},
        {"period":"2022 – 2023","role":"Python & ML Foundations","company":"Learning & Skill Building","current":False,"desc":"Mastered Python programming, statistics, and core ML algorithms. Built foundational projects in classification, regression, and data manipulation using Scikit-learn, Pandas, and NumPy."},
    ],
}


# ── Routes ────────────────────────────────────────────────────────
@app.route("/")
def index():
    if not session.get("visited"):
        session["visited"] = True
        count = increment_visitor()
    else:
        count = get_visitor_count()
    return render_template("index.html", data=PORTFOLIO, year=datetime.now().year, visitor_count=count)

@app.route("/api/visitors")
def visitors():
    return jsonify({"total": get_visitor_count()})

@app.route("/api/contact", methods=["POST"])
def contact():
    body    = request.get_json(silent=True) or {}
    name    = body.get("name",    "").strip()
    email   = body.get("email",   "").strip()
    subject = body.get("subject", "").strip()
    message = body.get("message", "").strip()

    if not all([name, email, message]):
        return jsonify({"ok": False, "error": "Name, email and message are required."}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"ok": False, "error": "Please enter a valid email address."}), 400

    print(f"\n📬 NEW MESSAGE from {name} <{email}> | Subject: {subject}")
    print(f"   Message: {message}")
    print(f"   Time: {datetime.now().strftime('%d %B %Y %I:%M %p')}")

    send_email(name, email, subject, message)
    return jsonify({"ok": True, "message": f"Thanks {name}! Message received. I'll reply soon! 🚀"})

@app.route("/api/stats")
def stats():
    return jsonify({
        "projects":  len(PORTFOLIO["projects"]),
        "skills":    sum(len(s["skills_list"]) for s in PORTFOLIO["skills"]),
        "available": PORTFOLIO["available"],
        "visitors":  get_visitor_count(),
        "year":      datetime.now().year,
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
