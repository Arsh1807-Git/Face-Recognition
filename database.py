"""
database.py
-----------
All Firestore read/write logic lives here. The rest of the project
never talks to Firestore directly — it goes through these functions.

Firestore collection used: "faces"
Each document looks like:
{
    "name": "Arsh",
    "age": 23,
    "gender": "Male",
    "encoding": [128 float numbers...],
    "first_seen": "2026-09-18 10:30:00",
    "last_seen": "2026-09-18 14:12:45"
}
"""

from datetime import datetime
import numpy as np
from firebase_config import get_db

COLLECTION_NAME = "faces"


def load_all_faces():
    """
    Pulls every stored face from Firestore ONCE at startup and loads
    it into memory as three parallel lists. Doing this avoids hitting
    the database on every single video frame (which would be slow
    and expensive).

    Returns:
        known_encodings (list of numpy arrays)
        known_ids       (list of Firestore document IDs, same order)
        known_details   (list of dicts: {name, age, gender}, same order)
    """
    db = get_db()
    docs = db.collection(COLLECTION_NAME).stream()

    known_encodings = []
    known_ids = []
    known_details = []

    for doc in docs:
        data = doc.to_dict()
        known_encodings.append(np.array(data["encoding"]))
        known_ids.append(doc.id)
        known_details.append({
            "name": data.get("name", "Unknown"),
            "age": data.get("age", "Unknown"),
            "gender": data.get("gender", "Unknown"),
        })

    return known_encodings, known_ids, known_details


def add_new_face(encoding, name, age, gender):
    """
    Saves a brand-new face to Firestore. Called the first time a face
    is seen and details have been collected from the user.
    """
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    doc_ref = db.collection(COLLECTION_NAME).document()
    doc_ref.set({
        "name": name,
        "age": age,
        "gender": gender,
        "encoding": encoding.tolist(),
        "first_seen": now,
        "last_seen": now,
    })
    return doc_ref.id


def update_last_seen(doc_id):
    """
    Called every time a KNOWN face is recognized again, so Firestore
    always reflects when that person was last spotted by the camera.
    """
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.collection(COLLECTION_NAME).document(doc_id).update({
        "last_seen": now
    })
