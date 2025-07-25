import streamlit as st
import datetime
import json
import os

# File to store notes
NOTES_FILE = "notes.json"

def load_notes():
    """Load notes from file"""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return []

def save_notes(notes):
    """Save notes to file"""
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

def main():
    st.title("📝 Simple Notes App")
    
    # Initialize session state
    if 'notes' not in st.session_state:
        st.session_state.notes = load_notes()
    
    # Sidebar for adding new notes
    with st.sidebar:
        st.header("Add New Note")
        new_note_title = st.text_input("Title")
        new_note_content = st.text_area("Content")
        if st.button("Save Note"):
            if new_note_title and new_note_content:
                new_note = {
                    "title": new_note_title,
                    "content": new_note_content,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.notes.append(new_note)
                save_notes(st.session_state.notes)
                st.success("Note saved!")
            else:
                st.warning("Please enter both title and content")
    
    # Display all notes
    st.header("Your Notes")
    
    if not st.session_state.notes:
        st.info("No notes yet. Add one using the sidebar!")
    else:
        for i, note in enumerate(st.session_state.notes):
            with st.expander(f"{note['title']} - {note['date']}"):
                st.write(note['content'])
                if st.button(f"Delete ❌", key=f"delete_{i}"):
                    del st.session_state.notes[i]
                    save_notes(st.session_state.notes)
                    st.rerun()

if __name__ == "__main__":
    main()
