import streamlit as st
import os
import fitz  # PyMuPDF for PDF to Image conversion
from google import genai
from dotenv import load_dotenv
from google.genai import types

# 1. Load the hidden API key from the .env file
load_dotenv() 

# 2. Interface Configuration
st.set_page_config(page_title="Setu_AI", layout="centered")

# Initialize Session State for Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar Configuration
with st.sidebar:
    st.title("Setu_AI Configuration")
    
    st.markdown("### Output Preferences")
    selected_language = st.selectbox(
        "Select Output Language:",
        ("English", "Hindi", "Hinglish")
    )
    
    st.markdown("---")
    st.markdown("### Application Features")
    st.markdown("- **Domain Expertise**: Specializes in B.Tech CSE, Programming, DSA, and DAA.")
    st.markdown("- **Dynamic Localization**: Toggle output between English, Hindi, and Hinglish.")
    st.markdown("- **Multimodal Processing**: Native support for PDF (Max 5 pages) and Image analysis.")
    st.markdown("- **Contextual Memory**: Remembers session history for follow-up questions.")
    st.markdown("- **Export Functionality**: Download session notes as a Markdown document.")
    st.markdown("---")
    
    # EXPORT FUNCTIONALITY
    if st.session_state.messages:
        st.markdown("### Session Export")
        
        export_text = "# Setu_AI Technical Session Notes\n\n"
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Setu_AI"
            export_text += f"### {role}\n{msg['display_text']}\n\n"
            
        st.download_button(
            label="Download Notes (.md)",
            data=export_text,
            file_name="Setu_AI_Notes.md",
            mime="text/markdown"
        )
        
        if st.button("Clear Conversation Memory"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.markdown("### Interface Appearance")
    st.markdown("To toggle Light/Night Mode, click the Menu icon (⋮) in the top right, select **Settings**, and adjust the **Theme**.")

# 4. Main Application Header
st.title("Setu_AI: B.Tech Academic Assistant")
st.markdown("Upload CSE technical documents, university schedules, or submit a direct programming query.")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["display_text"])

# 5. Input Modules
uploaded_files = st.file_uploader("Attach Files (PDF, JPG, PNG) [Max 5 Pages Total]", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
user_query = st.chat_input("Enter your technical query here...")

# 6. Execution Logic
# 6. Execution Logic
if user_query:
    display_user_text = user_query
    if uploaded_files:
        file_names = ", ".join([f.name for f in uploaded_files])
        display_user_text = f"**[Attached Files: {file_names}]**\n\n" + user_query
        
    with st.chat_message("user"):
        st.markdown(display_user_text)
        
    user_message_dict = {
        "role": "user",
        "display_text": display_user_text,
        "api_parts": []
    }
    
    # --- STEP A: PROCESS FILES ---
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.getvalue()
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                try:
                    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
                    # We store the PDF text as a clean string first
                    raw_text = f"\nDOCUMENT CONTEXT ({uploaded_file.name}):\n"
                    for page_num in range(len(pdf_document)):
                        page = pdf_document.load_page(page_num)
                        raw_text += f"--- Page {page_num + 1} ---\n{page.get_text()}\n"
                    pdf_document.close()
                    
                    # Wrap the extracted text in a Part
                    user_message_dict["api_parts"].append(types.Part.from_text(text=raw_text))
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
                    
            elif file_extension in ['jpg', 'jpeg', 'png']:
                m_type = "image/jpeg" if file_extension != 'png' else "image/png"
                user_message_dict["api_parts"].append(
                    types.Part.from_bytes(data=file_bytes, mime_type=m_type)
                )

    # --- STEP B: ADD THE USER QUERY ---
    user_message_dict["api_parts"].append(types.Part.from_text(text=f"\nUSER QUESTION: {user_query}"))
    st.session_state.messages.append(user_message_dict)

    # --- STEP C: GENERATE RESPONSE ---
    with st.chat_message("model"):
        with st.spinner("Setu_AI is analyzing your request..."):
            try:
                client = genai.Client()
                
                # Persona Injection (Bypasses 400 error)
                if selected_language == "English":
                    lang_rule = "Use formal, professional English."
                elif selected_language == "Hindi":
                    lang_rule = "Use formal Hindi (Devanagari script)."
                else:
                    lang_rule = "Use a natural mixture of English, Hindi, and Hinglish."
                
                persona = (
                    f"SYSTEM: You are Setu_AI. Expertise: B.Tech CSE, DSA, DAA, and Academic Logistics. "
                    f"Instructions: {lang_rule} Always analyze attached document text or images to answer."
                )
                
                # Sliding Window (Last 4)
                recent_messages = st.session_state.messages[-4:]
                
                api_contents = [types.Content(role="user", parts=[types.Part.from_text(text=persona)])]
                api_contents.append(types.Content(role="model", parts=[types.Part.from_text(text="Confirmed. I have processed your academic persona.")]))

                for msg in recent_messages:
                    p = msg.get("api_parts", [types.Part.from_text(text=msg["display_text"])])
                    api_contents.append(types.Content(role=msg["role"], parts=p))

                # Final Call
                response = client.models.generate_content(model='gemma-3-27b-it', contents=api_contents)
                
                st.markdown(response.text)
                st.session_state.messages.append({
                    "role": "model",
                    "display_text": response.text,
                    "api_parts": [types.Part.from_text(text=response.text)]
                })
                
            except Exception as e:
                st.error(f"System Exception: {e}")
                if st.session_state.messages: st.session_state.messages.pop()
