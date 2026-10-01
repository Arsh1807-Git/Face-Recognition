"""
firebase_config.py
-------------------
Handles the one-time initialization of the Firebase Admin SDK and
gives the rest of the project a ready-to-use Firestore client.

SETUP REQUIRED BEFORE RUNNING:
1. Go to https://console.firebase.google.com/
2. Create a project (or use an existing one).
3. Enable "Firestore Database" from the left sidebar (start in test mode
   for development).
4. Go to Project Settings (gear icon) -> Service Accounts tab.
5. Click "Generate new private key" -> this downloads a JSON file.
6. Rename that file to "serviceAccountKey.json" and place it in this
   same project folder 
   IMPORTANT (NEVER commit this file to a public GitHub repo).
"""

import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

_app = None
_db = None


def get_db():
    """
    Returns a singleton Firestore client. Initializes the Firebase app
    only once, no matter how many times this function is called.
    """
    global _app, _db

    if _db is not None:
        return _db

    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    _app = firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db
