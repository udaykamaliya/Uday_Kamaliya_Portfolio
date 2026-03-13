from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import re, smtplib, os, json, traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "uday-portfolio-secret-2025")

# ── Email Config ─────────────────────────────────────────────────
GMAIL_USER     = os.environ.get("GMAIL_USER",     "")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "")
NOTIFY_EMAIL   = os.environ.get("NOTIFY_EMAIL",   "udaykamaliya28@gmail.com")

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


# ── Email Sender ─────────────────────────────────────────────────
def send_email(name, sender_email, subject, message):
    """Try multiple SMTP methods to ensure delivery."""

    # Check credentials exist
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("❌ Email credentials missing — set GMAIL_USER and GMAIL_PASSWORD env vars on Render")
        return False

    print(f"📧 Attempting email send...")
    print(f"   GMAIL_USER    : {GMAIL_USER}")
    print(f"   NOTIFY_EMAIL  : {NOTIFY_EMAIL}")
    print(f"   Password set  : {'YES' if GMAIL_PASSWORD else 'NO'}")
    print(f"   Password len  : {len(GMAIL_PASSWORD)} chars")

    # Build email message
    msg = MIMEMultipart("alternative")
    msg["From"]    = GMAIL_USER
    msg["To"]      = NOTIFY_EMAIL
    msg["Reply-To"]= sender_email
    msg["Subject"] = f"Portfolio Contact: {subject or 'New Message'}"

    plain = f"""
New contact form submission!

Name    : {name}
Email   : {sender_email}
Subject : {subject or '(none)'}

Message:
{message}

Received: {datetime.now().strftime('%d %B %Y at %I:%M %p')}
    """.strip()

    html = f"""
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
    .ftr p{{color:#7a869e;font-size:12px;margin:0;}}
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
      <p style="margin-top:4px">Sent via <strong style="color:#a78bfa">uday.dev</strong> portfolio</p>
    </div>
  </div>
</body>
</html>
    """

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))

    # ── Method 1: SMTP_SSL port 465 ──
    try:
        print("🔄 Trying SMTP_SSL port 465...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent via port 465!")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Auth failed (465): {e}")
        print("   → Check your Gmail App Password is correct")
    except Exception as e:
        print(f"⚠️  Port 465 failed: {e}")

    # ── Method 2: STARTTLS port 587 ──
    try:
        print("🔄 Trying STARTTLS port 587...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent via port 587!")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Auth failed (587): {e}")
        print("   → Your App Password is wrong or expired")
        print("   → Go to myaccount.google.com → App Passwords → Create new one")
    except Exception as e:
        print(f"⚠️  Port 587 failed: {e}")
        print(f"   Full error: {traceback.format_exc()}")

    print("❌ All email methods failed")
    return False


# ── Portfolio Data ───────────────────────────────────────────────
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


# ── Routes ───────────────────────────────────────────────────────
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

    # Always log to terminal so you never miss a message
    print(f"\n{'='*50}")
    print(f"📬 NEW CONTACT FORM SUBMISSION")
    print(f"   Name    : {name}")
    print(f"   Email   : {email}")
    print(f"   Subject : {subject}")
    print(f"   Message : {message}")
    print(f"   Time    : {datetime.now().strftime('%d %B %Y at %I:%M %p')}")
    print(f"{'='*50}\n")

    email_sent = send_email(name, email, subject, message)

    if email_sent:
        return jsonify({"ok": True, "message": f"Thanks {name}! Message received. I'll reply soon! 🚀"})
    else:
        # Still show success to user — message is logged in Render logs
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