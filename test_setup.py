import sqlite3, hashlib

db = sqlite3.connect('members.db')
db.execute(
    "INSERT OR IGNORE INTO members (name, email, password, role, status, approved_at) "
    "VALUES (?, ?, ?, 'member', 'active', datetime('now'))",
    ('Adiel Ngugi', 'adielngugi@gmail.com', 
     hashlib.sha256('Launch@4831mq'.encode()).hexdigest())
)
db.commit()
db.close()
print('✅ Added to database!')