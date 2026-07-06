"""
BuildIT Connective - Bulk Member Import
Running it once to import existing sheet members and email them 

"""

import sys , os ,secrets ,sqlite3, hashlib,time, random
sys.path.insert(0, os.path.dirname(__file__))
from email_utils import send_welcome_email, ZOHO_EMAIL, SITE_URL

DB_PATH = os.path.join(os.path.dirname(__file__),"members.db")

TEST_EMAIL= "adielngugi@gmail.com"

MEMBERS=[
    ("Adiel Ngugi", "adielngugi@gmail.com")

]

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_password():
    words=["Build", "Code", "Tech", "Nairobi","Create",
           "Launch", "Ship", "Stack", "Design", "Hustle", "Grow",
           "Connect"]
    
    return f"{random.choice(words)}-{random.choice(words)}- {random.randint(1000,9999)}"

def import_member(db,name,email,send_now=False):
    email=email.strip().lower()
    name=name.strip()

    existing=db.execute(
        "SELECT id, status FROM members WHERE email=?",(email,)).fetchone()
    
    if existing:
        print(f" SKIP {name} <{email}> - already in DB ({existing["status"]})")
        return "exists", None
    
    temp_pw=generate_password()
    db.execute("""
        INSERT INTO MEMBERS (name, email, password,role,status, approved_at, notes)
        VALUES (?,?,?, 'member', 'active', datetime('now'), 'Imported from Google Sheets')"""
        , (name,email,hash_password(temp_pw)))
    
    db.commit()

    if send_now:
        ok,err= send_welcome_email(name,email,temp_pw)
        if ok:
            print(f" ADDED + EMAILED {name} <{email}> pw: {temp_pw}")
        else:
            print(f" Added but EMAIL FAILED {name} <{email}> pw: {temp_pw}")
            with open("import_log.txt", "a") as f:
                f.write(f"EMAIL FAILED | {name} | {email} | {temp_pw}\n")
    else:
        print(f" ADDED {name} <{email}> pw: {temp_pw}")
    
    return "created", temp_pw

def run_test():
    if TEST_EMAIL == "adielngugi@gmail.com":
        return 
    print(f" TEST - sending to {TEST_EMAIL} only\n")
    pw= generate_password()
    print(f" Test Password: {pw}")
    ok,err = send_welcome_email("Test Member", TEST_EMAIL, pw)
    if ok:
        print(f"\n Sent! Check your inbox.")
        print ("If it looks good run: python import members.py--send")
    else:
        print(f"\n Failed: {err}")
        print("Check zoho_email and zoho password in email_utils.py")


def run_import(send_emails=True):
    if not MEMBERS:
        print("Member List is empty!")
        return 
    
    db = get_db()
    created = skipped=0
    print(f"\n{'IMPORT + EMAIL' if send_emails else ' IMPORT ONLY'}")
    print(f"Processing {len(MEMBERS)} members...\n")

    with open("import_log.txt","w")as f:
        f.write("BuildIT Connective - Import Log\n" + "="*40 + "\n\n")
    
    for name, email in MEMBERS:
        status, pw = import_member(db,name,email,send_now=send_emails)
        if status == "created":
            created += 1
            with open("import_log.txt", "a") as f:
                f.write(f"{name} | {email} |{pw}\n")
            if send_emails:
                time.sleep(1.5)
            else:
                skipped += 1
            
        print(f"\n{'-'*40}")
        print(f"Added: {created}")
        print(f"Skipped: {skipped}")
        print(f" Passwords saved to import_log.txt")
        db.close()


def list_members():
    db=get_db()
    all=db.execute(
        "SELECT name, email,status, joined_at FROM members ORDER BY joined_at DESC"
    ).fetchall()
    db.close()
    print(f"\n {'NAME': <25} {'EMAIL': <30} {'STATUS'}")
    print("-"*65)
    for m in all:
        print(f"{m['name']:<25} {m['email']:<30} {m['status']}")

    print(f"\nTotal: {len(all)}\n")

if __name__=="__main__":
    arg=sys.argv[1] if len(sys.argv) > 1 else "--help"
    if arg== "--test":
        run_test()
    elif arg == "--send":
        confirm = input(
            f"\n Email {len(MEMBERS)} members from {ZOHO_EMAIL}?\n"
            "Type 'yes' to continue: "
        )
        if confirm.strip().lower() == "yes":
            run_import(send_emails=True)
        else:
            print("Cancelled")
    elif arg== "--import-only":
        run_import(send_emails=False)
    elif arg == "--list":
        list_members()
    else:
        print(__doc__)

