from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# ── Email Config ────────────────────────────────────────────────
# Set these as environment variables OR replace directly below
GMAIL_USER     = os.environ.get("GMAIL_USER",     "udaykamaliya28@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "")
NOTIFY_EMAIL   = os.environ.get("NOTIFY_EMAIL",   "udaykamaliya28@gmail.com")

def send_email(name, sender_email, subject, message):
    """Send contact form submission to Uday's Gmail inbox."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = GMAIL_USER
        msg["To"]      = NOTIFY_EMAIL
        msg["Subject"] = f"Portfolio Contact: {subject or 'New Message'}"

        plain = f"""
New contact form submission from your portfolio!

Name    : {name}
Email   : {sender_email}
Subject : {subject}

Message:
{message}

Received: {datetime.now().strftime('%d %B %Y at %I:%M %p')}
        """.strip()

        html = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family:'Segoe UI',Arial,sans-serif; background:#0c0e1a; margin:0; padding:0; }}
    .wrap {{ max-width:580px; margin:40px auto; background:#111426; border-radius:16px; overflow:hidden; border:1px solid rgba(255,255,255,.08); }}
    .header {{ background:linear-gradient(135deg,#7c5cfc,#22d3ee); padding:32px 36px; }}
    .header h1 {{ color:#fff; margin:0; font-size:22px; font-weight:700; }}
    .header p  {{ color:rgba(255,255,255,.8); margin:6px 0 0; font-size:14px; }}
    .body {{ padding:32px 36px; }}
    .field {{ margin-bottom:20px; }}
    .label {{ display:block; font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#7c5cfc; margin-bottom:6px; }}
    .val {{ background:#1a1d2e; border:1px solid rgba(255,255,255,.08); border-radius:8px; padding:12px 16px; color:#dde3f0; font-size:14px; line-height:1.6; }}
    .msg-box {{ background:#1a1d2e; border:1px solid rgba(124,92,252,.3); border-radius:8px; padding:16px; color:#dde3f0; font-size:14px; line-height:1.75; white-space:pre-wrap; }}
    .footer {{ border-top:1px solid rgba(255,255,255,.06); padding:20px 36px; text-align:center; }}
    .footer p {{ color:#7a869e; font-size:12px; margin:0; }}
    .reply-btn {{ display:inline-block; margin-top:16px; background:linear-gradient(135deg,#7c5cfc,#22d3ee); color:#fff !important; text-decoration:none; padding:12px 28px; border-radius:8px; font-weight:700; font-size:14px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1>New Portfolio Message</h1>
      <p>Someone reached out via your portfolio contact form</p>
    </div>
    <div class="body">
      <div class="field"><span class="label">From</span><div class="val">{name}</div></div>
      <div class="field"><span class="label">Email</span><div class="val">{sender_email}</div></div>
      <div class="field"><span class="label">Subject</span><div class="val">{subject or '(No subject)'}</div></div>
      <div class="field"><span class="label">Message</span><div class="msg-box">{message}</div></div>
      <div style="text-align:center;margin-top:24px;">
        <a href="mailto:{sender_email}?subject=Re: {subject}" class="reply-btn">Reply to {name}</a>
      </div>
    </div>
    <div class="footer">
      <p>Received on {datetime.now().strftime('%d %B %Y at %I:%M %p')}</p>
      <p style="margin-top:4px;">Sent via <strong style="color:#a78bfa;">uday.dev</strong> portfolio</p>
    </div>
  </div>
</body>
</html>
        """

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html,  "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent for message from {name} <{sender_email}>")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail auth failed — check your App Password in app.py or env vars.")
        return False
    except Exception as ex:
        print(f"❌ Email error: {ex}")
        return False


# ── Portfolio Data ──────────────────────────────────────────────
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
            {"name": "Python", "level": 65},
            {"name": "SQL", "level": 60},
            {"name": "HTML/CSS", "level": 65},
        ]},
        {"category": "AI / ML", "icon": "🧠", "color": "cyan", "skills_list": [
            {"name": "Scikit-learn", "level": 60},
            {"name": "Pandas / NumPy", "level": 65},
            {"name": "LangChain / RAG", "level": 60},
        ]},
        {"category": "Tools", "icon": "🛠️", "color": "pink", "skills_list": [
            {"name": "Flask", "level": 60},
            {"name": "Tableau", "level": 60},
            {"name": "Jupyter / Colab", "level": 70},
            {"name": "Git / GitHub", "level": 75},
        ]},
    ],
    "projects": [
        {
            "id": 1, "num": "01", "icon": "🤖", "color": "violet",
            "title": "SmartPredict ML Pipeline", "subtitle": "RAG-based Chatbot",
            "description": "Built an AI-powered chatbot using Retrieval-Augmented Generation to answer queries from Amazon product data. Combines LLM capabilities with real-time vector search for accurate, context-aware responses.",
            "tags": [{"label": "Python","color":"v"},{"label":"LangChain","color":"c"},{"label":"RAG","color":"v"},{"label":"OpenAI","color":"p"},{"label":"FAISS","color":"g"}],
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


# ── Routes ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", data=PORTFOLIO, year=datetime.now().year)


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

    print(f"\n📬 New message from {name} <{email}>\nSubject: {subject}\n{message}\n")
    send_email(name, email, subject, message)
    return jsonify({"ok": True, "message": f"Thanks {name}! I'll get back to you soon! 🚀"})


@app.route("/api/stats")
def stats():
    return jsonify({
        "projects":  len(PORTFOLIO["projects"]),
        "skills":    sum(len(s["skills_list"]) for s in PORTFOLIO["skills"]),
        "available": PORTFOLIO["available"],
        "year":      datetime.now().year,
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
