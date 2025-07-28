import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter
import datetime
import os
from io import BytesIO
from pathlib import Path

# Option 1: Same directory as script
cred_path = Path(__file__).parent / "tobi.json"

# Option 2: .streamlit subfolder
# cred_path = Path(__file__).parent / ".streamlit" / "tobi.json"

if not cred_path.exists():
    st.error(f"❌ Firebase key not found at: {cred_path}")
    st.stop()

cred = credentials.Certificate(str(cred_path))
# Initialize Firebase
def initialize_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(r"C:\Users\Lab\.vscode\.streamlit\tobi.json")
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'tobi-e5fc5.appspot.com'  # Replace with your bucket name
            })
            st.success("🔥 Firebase connected successfully!")
            return True
    except Exception as e:
        st.error(f"❌ Firebase initialization failed: {str(e)}")
        return False
    return True

# Test Firestore connection
def test_firestore_connection():
    try:
        db = firestore.client()
        db.collection("connection_test").document("test").set(
            {"timestamp": datetime.datetime.now().isoformat()}, 
            merge=True
        )
        return True
    except Exception as e:
        st.error(f"❌ Firestore connection failed: {str(e)}")
        return False

# Initialize Firebase and test connection
if not initialize_firebase() or not test_firestore_connection():
    st.stop()

# Initialize clients
db = firestore.client()
bucket = storage.bucket()

def upload_file(file, note_id):
    try:
        blob = bucket.blob(f"notes/{note_id}/{file.name}")
        blob.upload_from_file(file)
        return blob.public_url
    except Exception as e:
        st.error(f"❌ File upload failed: {str(e)}")
        return None

def load_notes():
    try:
        notes_ref = db.collection("notes")
        docs = notes_ref.stream()
        notes = []
        for doc in docs:
            note_data = doc.to_dict()
            note_data['id'] = doc.id
            # Get attached files
            files_ref = db.collection("notes").document(doc.id).collection("files")
            note_data['files'] = [file.to_dict() for file in files_ref.stream()]
            notes.append(note_data)
        return notes
    except Exception as e:
        st.error(f"❌ Failed to load notes: {str(e)}")
        return []

def save_note(title, content, files=None):
    try:
        note_ref = db.collection("notes").document()
        note_data = {
            "title": title,
            "content": content,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": note_ref.id
        }
        note_ref.set(note_data)
        
        # Handle file uploads
        if files:
            for file in files:
                file_url = upload_file(file, note_ref.id)
                if file_url:
                    db.collection("notes").document(note_ref.id).collection("files").add({
                        "name": file.name,
                        "url": file_url,
                        "uploaded_at": datetime.datetime.now().isoformat()
                    })
        
        st.success("Note saved successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to save note: {str(e)}")
        return False

def delete_note(note_id):
    try:
        # Delete associated files first
        files_ref = db.collection("notes").document(note_id).collection("files")
        for file_doc in files_ref.stream():
            # Delete from Firebase Storage
            file_url = file_doc.to_dict().get('url')
            if file_url:
                blob_name = file_url.split('/')[-1]
                blob = bucket.blob(f"notes/{note_id}/{blob_name}")
                blob.delete()
            # Delete file reference
            file_doc.reference.delete()
        
        # Delete the note
        db.collection("notes").document(note_id).delete()
        st.success("Note deleted successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete note: {str(e)}")
        return False

def main():
    st.title("📝 Tobi's Notes App with File Upload")
    
    # Initialize session state
    if 'notes' not in st.session_state:
        st.session_state.notes = load_notes()
    
    # Sidebar for adding new notes
    with st.sidebar:
        st.header("Add New Note")
        new_note_title = st.text_input("Title")
        new_note_content = st.text_area("Content")
        uploaded_files = st.file_uploader("Attach files", accept_multiple_files=True)
        
        if st.button("Save Note"):
            if new_note_title and new_note_content:
                if save_note(new_note_title, new_note_content, uploaded_files):
                    st.session_state.notes = load_notes()
            else:
                st.warning("Please enter both title and content")
    
    # Display all notes
    st.header("Your Notes")
    
    if not st.session_state.notes:
        st.info("No notes yet. Add one using the sidebar!")
    else:
        for note in st.session_state.notes:
            with st.expander(f"{note['title']} - {note['date']}"):
                st.write(note['content'])
                
                # Display attached files
                if 'files' in note and note['files']:
                    st.subheader("Attachments")
                    for file in note['files']:
                        st.markdown(f"""
                        - {file['name']}  
                        [Download]({file['url']}) (Uploaded: {file['uploaded_at']})
                        """)
                
                if st.button(f"Delete ❌", key=f"delete_{note['id']}"):
                    if delete_note(note['id']):
                        st.session_state.notes = load_notes()
                        st.rerun()
    
    # Debug view
    st.subheader("Debug: Raw Firestore Data")
    st.json(load_notes())

if __name__ == "__main__":
    main()
