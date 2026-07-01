# BuildIT Connective — Website

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

---

## How to update content

All site content lives at the top of **`app.py`** in the `DATA` section.
You never need to touch HTML to update text, links, events, or projects.

### Update social links / join form
```python
SITE = {
    "join_form": "https://forms.gle/YOUR_FORM",
    "socials": {
        "substack":  "https://substack.com/@builditconnective",
        "twitter":   "https://x.com/BuildITConn",
        "instagram": "https://www.instagram.com/builditconn/",
        "linkedin":  "https://www.linkedin.com/company/105680692/",
    },
    ...
}
```

### Add / edit an event
```python
EVENTS = [
    {
        "id": "my-event",
        "title": "Event Title",
        "subtitle": "Optional tagline",
        "date": "August 10, 2026",
        "time": "6:00 PM",
        "location": "Nairobi",
        "status": "upcoming",   # "upcoming" or "past"
        "description": "What the event is about.",
        "rsvp_link": "https://forms.gle/...",
        "poster": "my-poster.jpg",      # place image in static/images/
        "gallery_link": "",             # Drive link for past events
    },
    ...
]
```

### Add / edit a project
```python
PROJECTS = [
    {
        "title": "Project Name",
        "status": "delivered",          # "delivered" | "in-progress"
        "anonymous": True,              # hides team names, shows 🔒
        "description": "What was built.",
        "team": ["@Alice", "@Bob"],     # ignored if anonymous=True
        "review": "Client quote here.",
        "reviewer": "— Client Name",
        "tags": ["Web", "Nairobi"],
    },
    ...
]
```

### Add a journal article
```python
JOURNAL = [
    {
        "issue": "Issue #06",
        "title": "Article title",
        "excerpt": "Short teaser.",
        "link": "https://substack.com/...",
        "date": "July 2026",
    },
    ...
]
```

### Add a poster image
Drop the image file into `static/images/` and reference the filename in the event's `"poster"` field.

---

## File structure
```
buildit/
├── app.py               ← ALL data + routes (edit here)
├── requirements.txt
├── templates/
│   ├── base.html        ← nav, footer, shared HTML
│   └── index.html       ← homepage sections
└── static/
    ├── css/main.css     ← all styles (brand colors at top)
    ├── js/main.js       ← nav scroll, hamburger, animations
    └── images/
        ├── patent-or-perish.jpg
        └── idea-to-prototype.jpg
```

## Deploy
Works on any Python host: Railway, Render, Fly.io, PythonAnywhere.
Set `debug=False` in app.py before deploying.
