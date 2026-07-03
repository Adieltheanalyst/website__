"""
BuildIT Connective — Full Website + Member System
================================================
Edit the DATA section below to update content.
Run:  python app.py
Visit: http://localhost:5000
Admin: http://localhost:5000/admin  (first run creates admin user)
"""

import os, sqlite3, hashlib, secrets, hmac
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, g, jsonify)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "buildit-change-this-in-production")

DB_PATH = os.path.join(os.path.dirname(__file__), "members.db")

# ── Google Sheets webhook secret ──────────────────────────────────────────────
# This is a shared secret between your Google Sheet and Flask.
# Set the same value in both places. Change this to anything unique.
# In production set it as an environment variable: WEBHOOK_SECRET=yourvalue
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "buildit-sheets-sync-2025")
# ─────────────────────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════
#  DATA — edit this section to update content
# ══════════════════════════════════════════════

SITE = {
    "name":        "BuildIT Connective",
    "tagline":     "We don't just talk tech. We build it.",
    "description": (
        "BuildIT Connective is a community of builders, thinkers, and "
        "problem-solvers doing real work — together. From client projects "
        "to late-night build sessions, we're here for the craft."
    ),
    "email":    "builditconnective@gmail.com",
    "location": "Nairobi, Kenya 🇰🇪",
    "join_form":"https://forms.gle/iQMFzdYPJQCtHoLv8",
    "socials": {
        "substack":  "https://substack.com/@builditconnective",
        "twitter":   "https://x.com/BuildITConn",
        "instagram": "https://www.instagram.com/builditconn/",
        "linkedin":  "https://www.linkedin.com/company/105680692/",
    },
    "stats": {"members": "40+", "projects": "12", "events": "20+"},
}

# ── Real Substack articles ──
JOURNAL = [
    {
        "title":   "Stop Waiting for a Tech Co-Founder. Let's Build Your Prototype.",
        "excerpt": "You don't need a technical co-founder to start building. Here's how to go from idea to working prototype without waiting for permission.",
        "link":    "https://builditconnective.substack.com/p/stop-waiting-for-a-tech-co-founder",
        "date":    "May 6, 2026",
        "tag":     "Founders",
    },
    {
        "title":   "The Green Mirage: Why 'Climate Tech' Doesn't Scale on Good Intentions",
        "excerpt": "Impact without a business model is just charity. Why climate tech in Africa needs hard economics, not just good vibes.",
        "link":    "https://builditconnective.substack.com/p/the-green-mirage",
        "date":    "Apr 22, 2026",
        "tag":     "Climate",
    },
    {
        "title":   "Silicon Valley Blueprints vs. Nairobi Realities: The Anatomy of the Sendy Breakdown",
        "excerpt": "What the Sendy collapse actually tells us about copy-pasting Silicon Valley playbooks onto East African markets.",
        "link":    "https://builditconnective.substack.com/p/silicon-valley-blueprints-vs-nairobi",
        "date":    "Apr 15, 2026",
        "tag":     "Analysis",
    },
    {
        "title":   "The Great Re-Centralization: How AI Hijacked the Web3 Revolution",
        "excerpt": "Web3 promised decentralization. AI delivered the opposite. What this power shift means for builders in emerging markets.",
        "link":    "https://builditconnective.substack.com/p/the-great-re-centralization",
        "date":    "Apr 8, 2026",
        "tag":     "AI & Web3",
    },
    {
        "title":   "BuildIT Community Update: The IP Reality Check 🛠️",
        "excerpt": "Everything we covered at our IP session — patents, trademarks, trade secrets — and what actually matters when you're early stage.",
        "link":    "https://builditconnective.substack.com/p/buildit-community-update-the-ip-reality",
        "date":    "Mar 28, 2026",
        "tag":     "Community",
    },
    {
        "title":   "The Crowding Out Effect: Why the Government is Your Biggest Competitor for Capital",
        "excerpt": "When governments borrow aggressively, private capital dries up. Here's what that means for Kenyan startups trying to raise.",
        "link":    "https://builditconnective.substack.com/p/the-crowding-out-effect",
        "date":    "Mar 25, 2026",
        "tag":     "Finance",
    },
    {
        "title":   "The COMESA Loophole: Why Startups Should Think Like Multinationals",
        "excerpt": "Most Kenyan founders think local first. The COMESA trade bloc gives you a 21-country market from day one — if you know how to use it.",
        "link":    "https://builditconnective.substack.com/p/the-comesa-loophole",
        "date":    "Mar 18, 2026",
        "tag":     "Policy",
    },
    {
        "title":   "The Securitization Engine: How Future Cash is Building Kenya's Present",
        "excerpt": "How financial engineering is turning future receivables into present capital — and what builders can learn from structured finance.",
        "link":    "https://builditconnective.substack.com/p/the-securitization-engine",
        "date":    "Mar 4, 2026",
        "tag":     "Finance",
    },
]

# ── Combined Projects + Events (Work section) ──
WORK = [
    # ── EVENTS ──
    {
        "type":      "event",
        "id":        "patent-or-perish",
        "title":     "Patent or Perish?",
        "subtitle":  "The Real Talk of IP",
        "date":      "Coming Soon",
        "time":      "",
        "location":  "Nairobi",
        "status":    "upcoming",
        "description": (
            "Everything founders get wrong about intellectual property — "
            "patents, trademarks, copyrights, and what actually matters "
            "when you're building. No legal jargon. Just real talk."
        ),
        "rsvp_link":    "https://forms.gle/iQMFzdYPJQCtHoLv8",
        "poster":       "patent-or-perish.jpg",
        "gallery_link": "",
        "members_only_gallery": False,
    },
    {
        "type":      "event",
        "id":        "idea-to-prototype",
        "title":     "From Idea to Prototype",
        "subtitle":  "In One Day",
        "date":      "June 13, 2026",
        "time":      "9AM – 5PM",
        "location":  "British Institute in Eastern Africa",
        "status":    "past",
        "description": (
            "A full-day hands-on event open to everyone regardless of tech "
            "background. Tools: Figma, Claude, N8N, Firebase Studio. "
            "Co-hosted with INKA Society, Kenya Ni Mimi, ARTS, and the "
            "British Institute in Eastern Africa."
        ),
        "rsvp_link":    "",
        "poster":       "idea-to-prototype.jpg",
        "gallery_link": "https://drive.google.com/drive/folders/11pAl--DkFaupQEp1q8hcz8etgV1QGltC",
        "members_only_gallery": True,   # ← members only
    },
    # ── PROJECTS ──
    {
        "type":      "project",
        "title":     "Restaurant Management System",
        "status":    "delivered",
        "anonymous": True,
        "description": (
            "A full restaurant management system covering table reservations, "
            "order tracking, kitchen display, and end-of-day reporting. "
            "Built for a Nairobi-based restaurant moving off manual processes."
        ),
        "team": [],
        "review":   "The system completely transformed our operations. What used to take two staff members now runs itself.",
        "reviewer": "Client (identity withheld by request)",
        "tags":     ["Web App", "Operations", "F&B"],
    },
    {
        "type":      "project",
        "title":     "NGO Volunteer Management Portal",
        "status":    "delivered",
        "anonymous": False,
        "description": (
            "Web portal for a non-profit to coordinate volunteers across "
            "multiple programs — shift booking, reporting, and messaging "
            "in one place."
        ),
        "team":     ["@David N.", "@Esther W."],
        "review":   "This cut our coordination time in half. The BuildIT team understood our constraints and worked with us.",
        "reviewer": "Programs Director, NGO",
        "tags":     ["Portal", "Non-Profit", "Web"],
    },
    {
        "type":      "project",
        "title":     "Confidential Fintech Project",
        "status":    "delivered",
        "anonymous": True,
        "description": (
            "A fintech-adjacent product built under full NDA. "
            "Involved secure data handling and a mobile-first interface."
        ),
        "team":     [],
        "review":   "Professionalism from start to finish. Would absolutely engage this team again.",
        "reviewer": "Client (identity withheld per NDA)",
        "tags":     ["Fintech", "Mobile", "NDA"],
    },
    {
        "type":      "project",
        "title":     "Community Events Platform",
        "status":    "in-progress",
        "anonymous": False,
        "description": (
            "Internal BuildIT project — our own events management system "
            "so we can move off Google Forms. Open to members who want to contribute."
        ),
        "team":     ["@Felix A.", "@Grace T."],
        "review":   "Member project — ping us in the channel if you want to contribute.",
        "reviewer": "BuildIT Team",
        "tags":     ["Internal", "Open to Contributors"],
    },
]

VALUES = [
    {"icon": "⚡", "title": "Build, don't just plan",       "body": "We ship things. Real things."},
    {"icon": "🤝", "title": "Community over competition",   "body": "Everyone's welcome to contribute."},
    {"icon": "📖", "title": "Document the journey",         "body": "We write, we reflect, we share."},
    {"icon": "🔒", "title": "Respect client trust",         "body": "We protect our clients and our work."},
]

TICKER_ITEMS = [
    "Next: Patent or Perish? — Coming Soon",
    "8 articles live on Substack — go read them",
    "Open to new members — apply now",
    "We built a restaurant management system 🍽️",
    "BuildIT × INKA × Kenya Ni Mimi × ARTS",
    "Nairobi's builder community is growing",
]


# ══════════════════════════════════════════════
#  DATABASE SETUP
# ══════════════════════════════════════════════

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            role        TEXT DEFAULT 'member',   -- 'member' or 'admin'
            status      TEXT DEFAULT 'pending',  -- 'pending' | 'active' | 'suspended'
            joined_at   TEXT DEFAULT (datetime('now')),
            approved_at TEXT,
            notes       TEXT
        );
    """)
    # Create default admin if none exists
    existing = db.execute("SELECT id FROM members WHERE role='admin'").fetchone()
    if not existing:
        pw = hash_password("buildit2025admin")
        db.execute("""
            INSERT INTO members (name, email, password, role, status, approved_at)
            VALUES (?, ?, ?, 'admin', 'active', datetime('now'))
        """, ("Admin", "admin@builditconnective.com", pw))
        db.commit()
        print("✅ Default admin created: admin@builditconnective.com / buildit2025admin")
        print("   ⚠️  Change this password after first login!")
    db.close()


# ══════════════════════════════════════════════
#  AUTH HELPERS
# ══════════════════════════════════════════════

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "member_id" not in session:
            flash("Please log in to access this page.", "info")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "member_id" not in session:
            return redirect(url_for("login", next=request.path))
        db   = get_db()
        member = db.execute("SELECT * FROM members WHERE id=?",
                            (session["member_id"],)).fetchone()
        if not member or member["role"] != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

def current_member():
    if "member_id" not in session:
        return None
    return get_db().execute(
        "SELECT * FROM members WHERE id=?", (session["member_id"],)
    ).fetchone()


# ══════════════════════════════════════════════
#  PUBLIC ROUTES
# ══════════════════════════════════════════════

@app.route("/")
def index():
    member  = current_member()
    events  = [w for w in WORK if w["type"] == "event"]
    upcoming = [e for e in events if e["status"] == "upcoming"]
    return render_template("index.html",
        site=SITE, work=WORK, journal=JOURNAL[:3],
        values=VALUES, ticker=TICKER_ITEMS,
        next_event=upcoming[0] if upcoming else None,
        member=member,
    )

@app.route("/journal")
def journal():
    member = current_member()
    return render_template("journal.html", site=SITE,
                           journal=JOURNAL, member=member)

# Gallery — members only
@app.route("/gallery/<event_id>")
@login_required
def gallery(event_id):
    member = current_member()
    if member["status"] != "active":
        flash("Your account is pending approval.", "info")
        return redirect(url_for("index"))
    event = next((w for w in WORK
                  if w.get("id") == event_id and w["type"] == "event"), None)
    if not event:
        return redirect(url_for("index"))
    return render_template("gallery.html", site=SITE, event=event, member=member)


# ══════════════════════════════════════════════
#  AUTH ROUTES
# ══════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if "member_id" in session:
        return redirect(url_for("members_home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pw    = request.form.get("password", "")
        db    = get_db()
        member = db.execute(
            "SELECT * FROM members WHERE email=? AND password=?",
            (email, hash_password(pw))
        ).fetchone()
        if not member:
            flash("Incorrect email or password.", "error")
        elif member["status"] == "pending":
            flash("Your application is still under review. We'll email you when approved.", "info")
        elif member["status"] == "suspended":
            flash("Your account has been suspended. Contact us at builditconnective@gmail.com", "error")
        else:
            session["member_id"] = member["id"]
            session["member_name"] = member["name"]
            nxt = request.args.get("next", url_for("members_home"))
            return redirect(nxt)
    return render_template("login.html", site=SITE)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/set-password", methods=["GET", "POST"])
@login_required
def set_password():
    member = current_member()
    if request.method == "POST":
        current = request.form.get("current", "")
        new_pw  = request.form.get("new_password", "")
        confirm = request.form.get("confirm", "")
        if hash_password(current) != member["password"]:
            flash("Current password is incorrect.", "error")
        elif len(new_pw) < 8:
            flash("Password must be at least 8 characters.", "error")
        elif new_pw != confirm:
            flash("Passwords don't match.", "error")
        else:
            get_db().execute("UPDATE members SET password=? WHERE id=?",
                             (hash_password(new_pw), member["id"]))
            get_db().commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("members_home"))
    return render_template("set_password.html", site=SITE, member=member)


# ══════════════════════════════════════════════
#  MEMBER ROUTES
# ══════════════════════════════════════════════

@app.route("/members")
@login_required
def members_home():
    member = current_member()
    if member["status"] != "active":
        flash("Your application is pending approval.", "info")
        return redirect(url_for("index"))
    past_events = [w for w in WORK
                   if w["type"] == "event" and w["status"] == "past"]
    return render_template("members.html", site=SITE,
                           member=member, past_events=past_events)


# ══════════════════════════════════════════════
#  ADMIN ROUTES
# ══════════════════════════════════════════════

@app.route("/admin")
@admin_required
def admin():
    db      = get_db()
    member  = current_member()
    pending = db.execute(
        "SELECT * FROM members WHERE status='pending' ORDER BY joined_at DESC"
    ).fetchall()
    active  = db.execute(
        "SELECT * FROM members WHERE status='active' ORDER BY joined_at DESC"
    ).fetchall()
    all_members = db.execute(
        "SELECT * FROM members ORDER BY joined_at DESC"
    ).fetchall()
    return render_template("admin.html", site=SITE, member=member,
                           pending=pending, active=active,
                           all_members=all_members)

@app.route("/admin/add-member", methods=["POST"])
@admin_required
def add_member():
    """Add a new member manually (after Google Form approval)."""
    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip().lower()
    notes    = request.form.get("notes", "").strip()
    # Generate a temporary password they'll be asked to change
    temp_pw  = secrets.token_urlsafe(8)
    db = get_db()
    try:
        db.execute("""
            INSERT INTO members (name, email, password, role, status, approved_at, notes)
            VALUES (?, ?, ?, 'member', 'active', datetime('now'), ?)
        """, (name, email, hash_password(temp_pw), notes))
        db.commit()
        flash(
            f"✅ Member added! Share these credentials with {name}: "
            f"Email: {email} | Temp password: {temp_pw} "
            f"(they should change it after login)",
            "success"
        )
    except sqlite3.IntegrityError:
        flash(f"Email {email} already exists in the database.", "error")
    return redirect(url_for("admin"))

@app.route("/admin/approve/<int:member_id>")
@admin_required
def approve_member(member_id):
    db = get_db()
    member_row = db.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    if not member_row:
        flash("Member not found.", "error")
        return redirect(url_for("admin"))
    temp_pw = secrets.token_urlsafe(8)
    db.execute("""
        UPDATE members SET status='active', password=?, approved_at=datetime('now')
        WHERE id=?
    """, (hash_password(temp_pw), member_id))
    db.commit()
    flash(
        f"✅ {member_row['name']} approved! "
        f"Share temp password: {temp_pw}",
        "success"
    )
    return redirect(url_for("admin"))

@app.route("/admin/suspend/<int:member_id>")
@admin_required
def suspend_member(member_id):
    get_db().execute("UPDATE members SET status='suspended' WHERE id=?", (member_id,))
    get_db().commit()
    flash("Member suspended.", "info")
    return redirect(url_for("admin"))

@app.route("/admin/delete/<int:member_id>", methods=["POST"])
@admin_required
def delete_member(member_id):
    get_db().execute("DELETE FROM members WHERE id=?", (member_id,))
    get_db().commit()
    flash("Member deleted.", "info")
    return redirect(url_for("admin"))

@app.route("/admin/make-admin/<int:member_id>")
@admin_required
def make_admin(member_id):
    get_db().execute("UPDATE members SET role='admin' WHERE id=?", (member_id,))
    get_db().commit()
    flash("Member promoted to admin.", "success")
    return redirect(url_for("admin"))

# ── Quick register (for members who applied via Google Form) ──
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Members who were approved get a link to this page to set their account up.
    You can also use admin panel to add them directly with a temp password.
    """
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw    = request.form.get("password", "")
        conf  = request.form.get("confirm", "")
        if not name or not email or not pw:
            flash("All fields are required.", "error")
        elif len(pw) < 8:
            flash("Password must be at least 8 characters.", "error")
        elif pw != conf:
            flash("Passwords don't match.", "error")
        else:
            db = get_db()
            # Check if email already registered
            existing = db.execute(
                "SELECT * FROM members WHERE email=?", (email,)
            ).fetchone()
            if existing:
                flash("This email is already registered. Please log in.", "info")
                return redirect(url_for("login"))
            db.execute("""
                INSERT INTO members (name, email, password, status)
                VALUES (?, ?, ?, 'pending')
            """, (name, email, hash_password(pw)))
            db.commit()
            flash(
                "Application received! ✅ We'll review and get back to you within a week.",
                "success"
            )
            return redirect(url_for("index"))
    return render_template("register.html", site=SITE)


# ══════════════════════════════════════════════
#  GOOGLE SHEETS SYNC API
# ══════════════════════════════════════════════
#
#  This endpoint is called automatically by a Google Apps Script
#  whenever someone submits your Google Form.
#  It creates a "pending" member in the database instantly —
#  you then just click Approve in /admin.
#
#  SECURITY: Set SHEETS_WEBHOOK_SECRET in your environment,
#  and paste the same value into the Apps Script below.
#  This stops random people from hitting your endpoint.

SHEETS_SECRET = os.environ.get("SHEETS_WEBHOOK_SECRET", "buildit-sheets-secret-change-me")

@app.route("/api/form-submission", methods=["POST"])
def form_submission():
    """
    Called by Google Apps Script when a new Google Form response arrives.
    Expects JSON: { "secret": "...", "name": "...", "email": "...", "phone": "...", "about": "..." }
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"ok": False, "error": "No JSON received"}), 400

    # Verify secret token
    if data.get("secret") != SHEETS_SECRET:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    name  = (data.get("name")  or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    about = (data.get("about") or "").strip()   # "Tell us about yourself" field

    if not name or not email:
        return jsonify({"ok": False, "error": "Name and email are required"}), 400

    # Build notes from extra fields
    notes_parts = []
    if phone: notes_parts.append(f"Phone: {phone}")
    if about: notes_parts.append(f"About: {about}")
    notes = " | ".join(notes_parts) if notes_parts else "Via Google Form"

    db = get_db()

    # Check if already exists
    existing = db.execute("SELECT * FROM members WHERE email=?", (email,)).fetchone()
    if existing:
        return jsonify({
            "ok": True,
            "message": f"Email {email} already exists (status: {existing['status']})"
        }), 200

    # Insert as pending
    db.execute("""
        INSERT INTO members (name, email, password, status, notes)
        VALUES (?, ?, ?, 'pending', ?)
    """, (name, email, hash_password(secrets.token_urlsafe(16)), notes))
    db.commit()

    print(f"[FORM SYNC] New application from {name} <{email}>")
    return jsonify({"ok": True, "message": f"Member {name} added as pending"}), 201


@app.route("/api/sync-status", methods=["GET"])
def sync_status():
    """Quick health check — visit this URL to confirm your webhook is reachable."""
    secret = request.args.get("secret", "")
    if secret != SHEETS_SECRET:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    db = get_db()
    counts = db.execute("""
        SELECT status, COUNT(*) as n FROM members GROUP BY status
    """).fetchall()
    return jsonify({
        "ok": True,
        "status": "BuildIT Connective API is running",
        "members": {row["status"]: row["n"] for row in counts}
    })


# ══════════════════════════════════════════════
#  GOOGLE SHEETS WEBHOOK
# ══════════════════════════════════════════════

@app.route("/api/new-member", methods=["POST"])
def sheets_webhook():
    """
    Called automatically by Google Apps Script when someone submits the form.
    Google Sheet sends JSON:  { "secret": "...", "name": "...", "email": "..." }
    Flask saves them as pending → you approve in /admin.
    """
    data = request.get_json(silent=True)

    # ── 1. Validate secret ──────────────────────────────────────────
    if not data or data.get("secret") != WEBHOOK_SECRET:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    # ── 2. Extract fields ───────────────────────────────────────────
    name  = (data.get("name")  or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()   # optional
    role_applied = (data.get("role") or "").strip()  # e.g. "Designer", "Developer"
    notes = f"Via Google Form. Role: {role_applied}. Phone: {phone}".strip(". ")

    if not name or not email:
        return jsonify({"ok": False, "error": "name and email are required"}), 400

    # ── 3. Save to database ─────────────────────────────────────────
    db = get_db()
    existing = db.execute(
        "SELECT id, status FROM members WHERE email=?", (email,)
    ).fetchone()

    if existing:
        return jsonify({
            "ok":     True,
            "status": "already_exists",
            "member_status": existing["status"],
            "message": f"{email} is already in the database ({existing['status']})"
        })

    # Temp password — member will be asked to change it on first login
    temp_pw = secrets.token_urlsafe(8)

    db.execute("""
        INSERT INTO members (name, email, password, role, status, notes)
        VALUES (?, ?, ?, 'member', 'pending', ?)
    """, (name, email, hash_password(temp_pw), notes))
    db.commit()

    print(f"[WEBHOOK] New member from Google Form: {name} <{email}>")

    return jsonify({
        "ok":      True,
        "status":  "created",
        "message": f"{name} added as pending. Approve at /admin",
    }), 201


@app.route("/api/status", methods=["GET"])
def api_status():
    """Health check — lets you confirm the server is reachable from Google Sheets."""
    db = get_db()
    counts = db.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status='active'  THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending
        FROM members
    """).fetchone()
    return jsonify({
        "ok":      True,
        "service": "BuildIT Connective",
        "members": {
            "total":   counts["total"],
            "active":  counts["active"],
            "pending": counts["pending"],
        }
    })


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    print("\n🚀 BuildIT Connective running at http://localhost:5000")
    print("🔑 Admin panel at http://localhost:5000/admin")
    print("   Default login: admin@builditconnective.com / buildit2025admin\n")
    app.run(debug=True, port=5000)
