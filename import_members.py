"""
BuildIT Connective - Bulk Member Import
Running it once to import existing sheet members and email them 

"""

import sys , os ,secrets ,sqlite3, hashlib,time, random
sys.path.insert(0, os.path.dirname(__file__))
from email_utils import send_welcome_email, ZOHO_EMAIL, SITE_URL