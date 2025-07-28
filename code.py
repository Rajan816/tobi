import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

# Initialize Firebase
if not firebase_admin._apps:
    try:
        # Using Streamlit secrets for Firebase configuration
        firebase_config = {
            "type": "service_account",
            "project_id": "tobi-e5fc5",
            "private_key_id": "088467e16ed2945646c42e77fd4bab24796decc9",
            "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC4k+iwg1vfVfbQ
Py6HIw+HIu8Af4ckpTXBs6dBPi0b/R5fcVSksCRRnOPid1yFpITAuNg2f2Gz4Hr6
PqLgu05Bz65mAvVKknsSW+n7TldxUPZO221I+terlFBtYdyrT6L6qJCo7xV10WhR
De7xRX0LYbCgD090+MVXd/+nfX9vDWVuO7V/DtYZz5WhuNxHqAcyRG5/G/30q42v
p1e9WlfyzZAGh8QZcUZsAdTRXT2DeaS5wXdH8YiS/KT5gbuKo4aJg09Z9e1F9Y+y
H/Ya6I3fRsmu1Zz7gtZmsE8sVQUqUw6eIrCXHF9Fgiii7EnFKe1zAcL5iFxjqZhy
CjSs0x9rAgMBAAECggEAJDOuceBxxo4fyJx7zbmMtB6f7eMVaJSWxJUt+tftFQ5C
RMn/pgV+OhuhfquWlAe+meYnUhkN2q/uruJWI+nY4YOQWyW9YpD0Xpd0fvvQnsMY
bEMRXj0Ey/xdAfctxtPpzWv+Y4PxG5ik8zDeaqgMbI0OjXYzSWf5nLxGgl1U/zy1
rPJ3lBBLbTzv6MxNSPcSsn0YIVO47uKVHjKys7qLv4PRXW9tbbLJ+etUJQ7L4FSI
Xm9UBZVKI1NhSJcp6WRReeT3XvNqxyLWa6YAOx7Mkl1TxiaY2a8w3zYSLajETpJ8
vvYVg2VGUpxh0OdRhTdktIqXJbH/GE8IY02Mlpct4QKBgQDw+dQhjJ1/BhlRHmhW
OgQaaBeDlSCvpkmazIxHzmyYfKaPwLabfiWcxsuBPwNDyyYOHDzxSr5DhGLAFCMU
RfmIjDuktQPFcL4dHzztX7GDOdx9OujKPyjeCww/XP9NxJt1hYpFSx7KKio5PBMW
YE00vknLIniNRAEjnd2f3jzScwKBgQDEFeucQufj5GyYcbRhdln2t3VmQ+KlDE+g
QpYqNsK9Y5lrtuJZTHa6Pb4cwVWdfJIH6v8yXRbqOlijIk3BMBD69Tme2w/V95ln
NkTnVG2T4kfNKQibH+42r93evgdoTeHA+pXcRUh43kRegd8qx5ZhPHrfQhFEYgP5
8MZVtdspKQKBgBT4OIx+1wnBtxxHAB9YxxihLEKoDIMcflU5LY/mF68hUcE6rOlV
DeLZrcXefOM+X15k+Kyqq2nmsE00s2TFPhSy11Ha6qwYxoJ0QHILnL/lnhlLsgw/
eMfxwCwXZKQY0spkR4cGJXTEPI5keui8kptfX76Mjl8EpvC5gRqzVSmfAoGAX/S2
Ku7W2b/joKor8nHfTouyqMvZspkWsj9Div7nR5Tg9EQ3+ikgBL3INfwqcHoQYE2Q
es3xM8g/rf1QfZSPCrBMdT+QPU4ARPDawTWgtfjK2EwXSQpUIXDoq2Lk7xcFvdEi
2vsQnw1t+a2mTyICpizZmD2Vg5hPh9VayYDH8hkCgYAvptX0oCyzIvcSElXQ2vdy
KN9hU/8VU37CJ9EndkLwqevX+42nxqDnqNattm5kcYrDjR32XU/4GbWbSsN8PHYs
PQv6gkay0Ej1zh0zrCq+4bPLkKynNCXU9ovdhwZd6V9pgpKJbBtaov1IZQe9p2FK
y0ia4hPDBGxiejZ7ljl01w==
-----END PRIVATE KEY-----""",
            "client_email": "firebase-adminsdk-fbsvc@tobi-e5fc5.iam.gserviceaccount.com",
            "client_id": "117438689733859423098",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40tobi-e5fc5.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase initialization failed: {e}")

# Firestore database functions
def get_db():
    return firestore.client()

def load_notes():
    try:
        db = get_db()
        notes_ref = db.collection('notes')
        docs = notes_ref.stream()
        notes = []
        for doc in docs:
            note = doc.to_dict()
            note['id'] = doc.id  # ✅ Add the document ID manually
            notes.append(note)
        return notes
    except Exception as e:
        st.error(f"Error loading notes: {e}")
        return []

def save_note(note):
    try:
        db = get_db()
        notes_ref = db.collection('notes')
        notes_ref.document(note['id']).set(note)
    except Exception as e:
        st.error(f"Error saving note: {e}")

def delete_note(note_id):
    try:
        db = get_db()
        notes_ref = db.collection('notes')
        notes_ref.document(note_id).delete()
    except Exception as e:
        st.error(f"Error deleting note: {e}")

def main():
    st.title("📝 Firebase-Backed Notes App")
    
    # Initialize notes
    if 'notes' not in st.session_state:
        st.session_state.notes = load_notes()
    
    # Add note UI
    with st.sidebar:
        st.header("New Note")
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.button("💾 Save to Firebase"):
            if title and content:
                new_note = {
                    "id": datetime.now().isoformat(),
                    "title": title,
                    "content": content,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_note(new_note)
                st.session_state.notes = load_notes()  # Refresh notes
                st.success("Saved to Firebase!")
    
    # Display notes
    st.header("Your Notes")
    for note in st.session_state.notes:
        with st.expander(f"{note['title']} - {note['date']}"):
            st.write(note['content'])
            if st.button(f"Delete {note['title']}", key=note['id']):
                delete_note(note['id'])
                st.session_state.notes = load_notes()  # Refresh notes
                st.rerun()

if __name__ == "__main__":
    main()
