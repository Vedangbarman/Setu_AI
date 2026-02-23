import streamlit as st
import os
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
    st.markdown("- **Domain Expertise**: Specializes in Computer Science, Programming, DSA, and DAA.")
    st.markdown("- **Dynamic Localization**: Toggle output between English, Hindi, and Hinglish.")
    st.markdown("- **Multimodal Processing**: Native support for multiple PDF and Image analysis simultaneously.")
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
st.title("Setu_AI: Technical Assistant")
st.markdown("Upload technical documents or images, or submit a direct query regarding programming and algorithms.")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["display_text"])

# 5. Input Modules
uploaded_files = st.file_uploader("Attach Files (PDF, JPG, PNG) [Optional]", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
user_query = st.chat_input("Enter your technical query here...")

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
    
    # Pack files as Pydantic binary parts
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.getvalue()
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                mime_type = 'application/pdf'
            elif file_extension in ['jpg', 'jpeg']:
                mime_type = 'image/jpeg'
            elif file_extension == 'png':
                mime_type = 'image/png'
                
            user_message_dict["api_parts"].append(
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            )
        
    # FIX: Pack text as a strict Pydantic text part
    user_message_dict["api_parts"].append(
        types.Part.from_text(text=user_query)
    )
    
    st.session_state.messages.append(user_message_dict)

    with st.chat_message("model"):
        with st.spinner("Analyzing context and generating response..."):
            try:
                client = genai.Client()
                
                if selected_language == "English":
                    lang_rule = "You must communicate strictly in formal, professional English."
                elif selected_language == "Hindi":
                    lang_rule = "You must communicate strictly in formal Hindi, using the Devanagari script."
                else:
                    lang_rule = "You must communicate using a natural, professional mixture of English, Hindi, and Hinglish."
                
                system_instruction = (
                    "You are Setu_AI, a professional and formal technical assistant. "
                    "Your expertise lies exclusively in Computer Science, programming, Data Structures and Algorithms (DSA), "
                    "and Design and Analysis of Algorithms (DAA). "
                    f"{lang_rule} "
                    "CRITICAL GUARDRAIL: You are strictly limited to answering questions related to coding, computer science, and technology. "
                    "If the user query, uploaded image, or uploaded document relates to any non-technical domain (e.g., history, general knowledge, medical), "
                    "you must politely decline the request and state your specialized domain."
                )
                
                api_contents = []
                for msg in st.session_state.messages:
                    # FIX: Ensure fallback text is also a strict Pydantic text part
                    parts = msg.get("api_parts", [types.Part.from_text(text=msg["display_text"])])
                    api_contents.append(
                        types.Content(role=msg["role"], parts=parts)
                    )

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=api_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                
                st.markdown(response.text)
                
                # FIX: Store model response as a strict Pydantic text part
                st.session_state.messages.append({
                    "role": "model",
                    "display_text": response.text,
                    "api_parts": [types.Part.from_text(text=response.text)]
                })
                
            except Exception as e:
                st.error(f"System Exception: {e}")
                if st.session_state.messages:
                    st.session_state.messages.pop()