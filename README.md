# BuildIT Connective — Website Setup Guide

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```


---

## How to update content (no HTML needed)

Open `app.py` and edit the DATA section at the top.

### Add a new event
```python
{
    "type":      "event",
    "id":        "my-event-slug",       # lowercase, no spaces, used in URL
    "title":     "Event Title",
    "subtitle":  "Optional tagline",
    "date":      "August 10, 2026",
    "time":      "6:00 PM",
    "location":  "Nairobi",
    "status":    "upcoming",            # "upcoming" or "past"
    "description": "What it's about.",
    "rsvp_link":    "https://forms.gle/...",
    "poster":       "my-poster.jpg",    # drop image in static/images/
    "gallery_link": "",                 # Google Drive link after event
    "members_only_gallery": True,       # True = login required to see photos
},
```
Drop the poster image into `static/images/` and use the filename above.

### Add a project
```python
{
    "type":      "project",
    "title":     "Project Name",
    "status":    "delivered",           # "delivered" or "in-progress"
    "anonymous": True,                  # True hides team names
    "description": "What was built.",
    "team":     ["@Alice", "@Bob"],     # ignored if anonymous=True
    "review":   "Client quote.",
    "reviewer": "— Client Name",
    "tags":     ["Web", "Nairobi"],
},
```

### Add a journal article
```python
{
    "title":   "Article Title",
    "excerpt": "One line teaser.",
    "link":    "https://builditconnective.substack.com/p/your-slug",
    "date":    "July 2026",
    "tag":     "Community",
},
```

---

## Member System

### How members get access

```
Person fills Google Form
        ↓
(With sync set up) → appears in /admin as pending automatically
        ↓
You click Approve in /admin
        ↓
A temp password is shown on screen — share it with them
        ↓
They log in at yoursite.com/login
        ↓
They change their password at /set-password
        ↓
They can now access /members and event galleries
```

### Without Google Sheets sync
Go to `/admin` → "Add member manually" → paste name + email from your Google Sheet → click Add. Same result.

---

## Google Sheets Sync Setup (5 minutes)

This makes new form submissions appear in your admin panel automatically.

### Step 1 — Set your secret key
In `app.py`, find this line:
```python
SHEETS_SECRET = os.environ.get("SHEETS_WEBHOOK_SECRET", "buildit-sheets-secret-change-me")
```
Change `"buildit-sheets-secret-change-me"` to any random string, e.g.:
```python
SHEETS_SECRET = os.environ.get("SHEETS_WEBHOOK_SECRET", "BuildIT-K3nya-2026-Xq9!")
```
Remember this string — you'll paste it into the Apps Script too.

### Step 2 — Paste the Apps Script into Google Sheets
1. Open the Google Sheet linked to your form
2. Click **Extensions → Apps Script**
3. Delete everything, paste the contents of `google_apps_script.js`
4. Update these values at the top:
   - `WEBSITE_URL` → your deployed site URL + `/api/form-submission`
   - `WEBHOOK_SECRET` → the same secret from Step 1
   - `COLUMNS` → count which column in your Sheet has name, email, etc.
5. Save (Ctrl+S)

### Step 3 — Set up the trigger
1. In Apps Script, click the **clock icon** (Triggers) in the left sidebar
2. Click **+ Add Trigger**
3. Set:
   - Function: `onFormSubmit`
   - Event source: `From spreadsheet`
   - Event type: `On form submit`
4. Click Save → approve permissions

### Step 4 — Test it
1. In Apps Script, select `testWebhook` from the function dropdown
2. Click Run
3. Click **View → Logs** — you should see `Response 201`
4. Check your `/admin` panel — "Test Member" should appear as pending
5. Delete the test member from admin

### Local testing with ngrok
If you're running locally and want to test before deploying:
```bash
# In one terminal
python app.py

# In another terminal
ngrok http 5000
# Copy the https://xxxx.ngrok.io URL
# Use that as WEBSITE_URL in the Apps Script
```

---

## Deployment (make it live on the internet)

### Railway (easiest, free tier available)
```bash
# Install Railway CLI
npm install -g @railway/cli

railway login
railway init
railway up
```
Then in Railway dashboard → Variables, add:
- `SECRET_KEY` = any long random string
- `SHEETS_WEBHOOK_SECRET` = same as your Apps Script

### Render
1. Push code to GitHub
2. Go to render.com → New Web Service → connect your repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. Add environment variables same as above

---

## File structure
```
buildit2/
├── app.py                  ← ALL content + routes (edit here)
├── requirements.txt
├── members.db              ← auto-created on first run (don't delete!)
├── google_apps_script.js   ← paste this into Google Sheets Apps Script
├── README.md               ← this file
├── templates/
│   ├── base.html           ← nav + footer
│   ├── index.html          ← homepage
│   ├── login.html          ← member login
│   ├── register.html       ← self-registration
│   ├── members.html        ← members-only hub
│   ├── gallery.html        ← event gallery (members only)
│   ├── set_password.html   ← change password
│   └── admin.html          ← admin panel
└── static/
    ├── css/main.css
    ├── js/main.js
    └── images/
        ├── patent-or-perish.jpg
        └── idea-to-prototype.jpg
```

## Columns in your Google Form Sheet

Open your Sheet and check which column (A, B, C...) has each field.
Count from left: A=1, B=2, C=3...

Example Sheet layout:
| A (1) | B (2) | C (3) | D (4) | E (5) |
|-------|-------|-------|-------|-------|
| Timestamp | Full Name | Email | Phone | About you |

Update `COLUMNS` in `google_apps_script.js` to match yours.
