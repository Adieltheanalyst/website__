"""
BuildIT Connective — Community Website
Flask backend. Tweak the DATA section below to update content without touching HTML.
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ─────────────────────────────────────────────
#  DATA — edit this section to update content
# ─────────────────────────────────────────────

SITE = {
    "name": "BuildIT Connective",
    "tagline": "We don't just talk tech. We build it.",
    "description": (
        "BuildIT Connective is a community of builders, thinkers, and problem-solvers "
        "doing real work — together. From client projects to late-night build sessions, "
        "we're here for the craft."
    ),
    "email": "builditconnective@gmail.com",
    "location": "Nairobi, Kenya 🇰🇪",
    "join_form": "https://forms.gle/iQMFzdYPJQCtHoLv8",
    "socials": {
        "substack": "https://substack.com/@builditconnective",
        "twitter":  "https://x.com/BuildITConn",
        "instagram":"https://www.instagram.com/builditconn/",
        "linkedin": "https://www.linkedin.com/company/105680692/",
    },
    "stats": {
        "members":  "40+",
        "projects": "12",
        "events":   "20+",
    },
}

EVENTS = [
    {
        "id": "patent-or-perish",
        "title": "Patent or Perish?",
        "subtitle": "The Real Talk of IP",
        "date": "Coming Soon",
        "time": "",
        "location": "Nairobi",
        "status": "upcoming",   # upcoming | past
        "description": (
            "Everything founders get wrong about intellectual property — patents, "
            "trademarks, copyrights, and what actually matters when you're building. "
            "No legal jargon. Just real talk."
        ),
        "rsvp_link": "https://forms.gle/iQMFzdYPJQCtHoLv8",
        "poster": "patent-or-perish.jpg",
        "gallery_link": "",
    },
    {
        "id": "idea-to-prototype",
        "title": "From Idea to Prototype",
        "subtitle": "In One Day",
        "date": "June 13, 2026",
        "time": "9AM – 5PM",
        "location": "British Institute in Eastern Africa",
        "status": "past",
        "description": (
            "A full-day hands-on event — open to everyone regardless of tech background. "
            "Tools: Figma, Claude, N8N, Firebase Studio. Co-hosted with INKA Society, "
            "Kenya Ni Mimi, ARTS, and the British Institute in Eastern Africa."
        ),
        "rsvp_link": "",
        "poster": "idea-to-prototype.jpg",
        "gallery_link": "https://drive.google.com/drive/folders/11pAl--DkFaupQEp1q8hcz8etgV1QGltC",
    },
]

PROJECTS = [
    {
        "title": "Restaurant Management System",
        "status": "delivered",
        "anonymous": True,
        "description": (
            "A full restaurant management system covering table reservations, order tracking, "
            "kitchen display, and end-of-day reporting. Built for a Nairobi-based restaurant "
            "that needed to move off manual processes. Client requested anonymity."
        ),
        "team": [],   # anonymous
        "review": (
            "The system completely transformed our operations. "
            "What used to take two staff members now runs itself."
        ),
        "reviewer": "Client (identity withheld by request)",
        "tags": ["Web App", "Operations", "F&B"],
    },
    # {
    #     "title": "NGO Volunteer Management Portal",
    #     "status": "delivered",
    #     "anonymous": False,
    #     "description": (
    #         "Web portal for a non-profit to coordinate volunteers across multiple programs — "
    #         "shift booking, reporting, and messaging in one place."
    #     ),
    #     "team": ["@David N.", "@Esther W."],
    #     "review": (
    #         "This cut our coordination time in half. "
    #         "The BuildIT team understood our constraints and worked with us."
    #     ),
    #     "reviewer": "Programs Director, NGO",
    #     "tags": ["Portal", "Non-Profit", "Web"],
    # },
    # {
    #     "title": "Confidential Fintech Project",
    #     "status": "delivered",
    #     "anonymous": True,
    #     "description": (
    #         "A fintech-adjacent product for a client who requested full NDA coverage. "
    #         "Involved secure data handling and a mobile-first interface."
    #     ),
    #     "team": [],
    #     "review": "Professionalism from start to finish. Would absolutely engage this team again.",
    #     "reviewer": "Client (identity withheld per NDA)",
    #     "tags": ["Fintech", "Mobile", "NDA"],
    # },
    # {
    #     "title": "Community Events Platform",
    #     "status": "in-progress",
    #     "anonymous": False,
    #     "description": (
    #         "An internal BuildIT project — building our own events management system "
    #         "so we can move off Google Forms. Open to members who want to contribute."
    #     ),
    #     "team": ["@Felix A.", "@Grace T."],
    #     "review": "Member project — ping us in the channel if you want to contribute.",
    #     "reviewer": "BuildIT Team",
    #     "tags": ["Internal", "Open to Contributors"],
    # },
]

JOURNAL = [
    {
        "issue": "Issue #05",
        "title": "Patent or Perish? What builders need to know about IP",
        "excerpt": (
            "Before you ship, before you pitch, before you partner — "
            "here's the IP conversation nobody's having in the Nairobi tech scene."
        ),
        "link": "https://builditconnective.substack.com/p/buildit-community-update-the-ip-reality?r=5f1xh1",
        "date": "Coming Soon",
    },
    {
        "issue": "Issue #04",
        "title": "From Idea to Prototype in a Day: What we learned",
        "excerpt": (
            "We co-hosted a full-day build event with 5 organisations. "
            "Here's what worked, what surprised us, and what we'd do differently."
        ),
        "link": "https://substack.com/@builditconnective",
        "date": "June 2026",
    },
    {
        "issue": "Issue #03",
        "title": "The case for building things that only work in your city",
        "excerpt": (
            "Global platforms aren't built for Nairobi. "
            "That's a problem — but it's also an opportunity for those willing to think local-first."
        ),
        "link": "https://substack.com/@builditconnective",
        "date": "May 2026",
    },
]

VALUES = [
    {"icon": "⚡", "title": "Build, don't just plan", "body": "We ship things. Real things."},
    {"icon": "🤝", "title": "Community over competition", "body": "Everyone's welcome to contribute."},
    {"icon": "📖", "title": "Document the journey", "body": "We write, we reflect, we share."},
    {"icon": "🔒", "title": "Respect client trust", "body": "We protect our clients and our work."},
]

TICKER_ITEMS = [
    "Next: Patent or Perish? — Coming Soon",
    "New articles dropping on Substack",
    "Open to new members — apply now",
    "We built a restaurant management system 🍽️",
    "BuildIT × INKA × Kenya Ni Mimi × ARTS — stronger together",
    "Nairobi's builder community is growing",
]

# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    upcoming = [e for e in EVENTS if e["status"] == "upcoming"]
    past     = [e for e in EVENTS if e["status"] == "past"]
    return render_template(
        "index.html",
        site=SITE,
        events=EVENTS,
        upcoming=upcoming,
        past=past,
        projects=PROJECTS,
        journal=JOURNAL,
        values=VALUES,
        ticker=TICKER_ITEMS,
        next_event=upcoming[0] if upcoming else None,
    )

@app.route("/events")
def events():
    return render_template("events.html", site=SITE, events=EVENTS)

@app.route("/projects")
def projects():
    return render_template("projects.html", site=SITE, projects=PROJECTS)

@app.route("/journal")
def journal():
    return render_template("journal.html", site=SITE, journal=JOURNAL)

# Simple contact endpoint (extend with email sending if needed)
@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.json or {}
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    message = data.get("message", "").strip()
    if not name or not email or not message:
        return jsonify({"ok": False, "error": "All fields required"}), 400
    # TODO: send email via SendGrid / SMTP
    print(f"[CONTACT] {name} <{email}>: {message}")
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
