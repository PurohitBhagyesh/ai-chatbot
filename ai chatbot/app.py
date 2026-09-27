import streamlit as st
import ollama

st.set_page_config(page_title="My Personal Assistant", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# Extreme CSS injection to mimic the exact Gemini macOS app interface
st.markdown("""
    <style>
        /* Hide all default Streamlit chrome except the header so you can still open the sidebar */
        #MainMenu, footer {visibility: hidden !important;}
        
        /* Make header transparent and hide the sidebar toggle button so the sidebar is permanently fixed */
        header {background: transparent !important;}
        [data-testid="collapsedControl"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

import base64
import uuid
import json
import os
import re
import requests
from bs4 import BeautifulSoup

DATA_FILE = ".chat_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"bg_base64": "", "chats": {}, "theme": "Background Mode", "user_name": "User", "ai_name": "AI"}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "bg_base64": st.session_state.bg_base64,
            "chats": st.session_state.chats,
            "theme": st.session_state.theme,
            "user_name": st.session_state.user_name,
            "ai_name": st.session_state.ai_name
        }, f)

# Load data on first run
if "data_loaded" not in st.session_state:
    saved = load_data()
    st.session_state.bg_base64 = saved.get("bg_base64", "")
    st.session_state.chats = saved.get("chats", {})
    st.session_state.theme = saved.get("theme", "Background Mode")
    st.session_state.user_name = saved.get("user_name", "User")
    st.session_state.ai_name = saved.get("ai_name", "AI")
    st.session_state.data_loaded = True

if "theme" not in st.session_state:
    st.session_state.theme = "Background Mode"
if "user_name" not in st.session_state:
    st.session_state.user_name = "User"
if "ai_name" not in st.session_state:
    st.session_state.ai_name = "AI"

if "bg_base64" not in st.session_state:
    st.session_state.bg_base64 = ""

if "chats" not in st.session_state or len(st.session_state.chats) == 0:
    default_id = str(uuid.uuid4())
    st.session_state.chats = {default_id: {"name": "New Chat", "messages": []}}
    st.session_state.current_chat_id = default_id
elif "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]

# Apply dynamic theme
if st.session_state.theme == "Background Mode" and st.session_state.bg_base64 != "":
    st.markdown(f"""
        <style>
            .stApp {{
                background-color: #0b0e14 !important;
                background-image: linear-gradient(rgba(11, 14, 20, 0.2), rgba(11, 14, 20, 0.4)), url("{st.session_state.bg_base64}") !important;
                background-size: cover !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
            }}
        </style>
    """, unsafe_allow_html=True)
else:
    # Dark Mode (Default)
    st.markdown("""
        <style>
            .stApp {
                background-color: #0b0e14 !important;
                background-image: radial-gradient(circle at 50% 50%, #172445 0%, #0b0e14 100%) !important;
                color: #e2e8f0;
            }
        </style>
    """, unsafe_allow_html=True)

try:
    with open("style.css", "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown("""
    <style>
        /* Hide the native Streamlit chat avatar blocks (the black squares with icons) */
        [data-testid="stChatMessageAvatar"] { display: none !important; }
        .stChatMessage .stIcon { display: none !important; }
        /* Alternative broad hide if classes change */
        .stChatMessage > div:first-child { display: none !important; }
        .stChatMessage > div:nth-child(2) { width: 100% !important; margin-left: 0px !important; }
        
        /* Name tags for custom avatars */
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color: white; margin-bottom: 20px;'>✨ Your Personal Assistant</h3>", unsafe_allow_html=True)
    
    if st.button("📝 New chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat_id = new_id
        save_data()
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("📎 **Attach Local File**")
    uploaded_file = st.file_uploader("Upload a document for me to read", type=["txt", "md", "py", "csv", "html"])
    if uploaded_file:
        st.success("File attached! Ask me a question about it.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("💬 **Conversations:**")
    
    # Show list of chats
    for chat_id, chat_data in list(st.session_state.chats.items()):
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            prefix = "🟢" if chat_id == st.session_state.current_chat_id else "📄"
            if st.button(f"{prefix} {chat_data['name']}", key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col2:
            with st.popover("⋮"):
                new_name = st.text_input("Rename Chat", value=chat_data["name"], key=f"ren_{chat_id}")
                if new_name != chat_data["name"]:
                    st.session_state.chats[chat_id]["name"] = new_name
                    save_data()
                    st.rerun()
                if st.button("Delete Chat", key=f"del_{chat_id}"):
                    del st.session_state.chats[chat_id]
                    if chat_id == st.session_state.current_chat_id:
                        if len(st.session_state.chats) > 0:
                            st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                        else:
                            new_id = str(uuid.uuid4())
                            st.session_state.chats[new_id] = {"name": "New Chat", "messages": []}
                            st.session_state.current_chat_id = new_id
                    save_data()
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Settings Section
    with st.expander("⚙️ Settings"):
        st.markdown("<small>Configure your assistant.</small>", unsafe_allow_html=True)
        selected_model = st.selectbox("AI Model", ["llama3.2"])
        
        st.markdown("<small>Your Name</small>", unsafe_allow_html=True)
        new_u = st.text_input("Your Name", value=st.session_state.user_name, label_visibility="collapsed")
        if new_u != st.session_state.user_name:
            st.session_state.user_name = new_u
            save_data()
            st.rerun()
            
        st.markdown("<small>Assistant Name</small>", unsafe_allow_html=True)
        new_ai = st.text_input("Assistant Name", value=st.session_state.ai_name, label_visibility="collapsed")
        if new_ai != st.session_state.ai_name:
            st.session_state.ai_name = new_ai
            save_data()
            st.rerun()
        
        st.markdown("<small>Appearance</small>", unsafe_allow_html=True)
        # Use safe index checking in case Light Mode was saved previously
        current_theme_index = 0 if st.session_state.theme not in ["Background Mode", "Dark Mode"] else ["Background Mode", "Dark Mode"].index(st.session_state.theme)
        new_theme = st.selectbox("Theme", ["Background Mode", "Dark Mode"], index=current_theme_index, label_visibility="collapsed")
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            save_data()
            st.rerun()
        
        st.markdown("<small>Wallpaper Image</small>", unsafe_allow_html=True)
        bg_file = st.file_uploader("Upload Background", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if bg_file:
            base64_img = base64.b64encode(bg_file.getvalue()).decode()
            new_bg = f"data:{bg_file.type};base64,{base64_img}"
            if st.session_state.bg_base64 != new_bg:
                st.session_state.bg_base64 = new_bg
                save_data()
                st.rerun()
            
        if st.session_state.bg_base64 != "":
            if st.button("Reset Wallpaper"):
                st.session_state.bg_base64 = ""
                save_data()
                st.rerun()
    
# --- MAIN AREA ---

# Convenience variable for the current active chat's messages
current_messages = st.session_state.chats[st.session_state.current_chat_id]["messages"]

# If no messages, show welcome screen
if len(current_messages) == 0:
    st.markdown('''
        <div style="text-align: center; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div class="welcome-text" style="margin-top: 15vh; margin-bottom: 15px;">Welcome to your personal assistant.</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 20px; font-weight: 300;">What would you like to explore today?</div>
        </div>
    ''', unsafe_allow_html=True)
else:
    # We add a hidden div to trigger CSS changes when chatting starts
    st.markdown('<div class="chat-active"></div>', unsafe_allow_html=True)

# Display chat messages for the current chat
for message in current_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            name = st.session_state.user_name if message["role"] == "user" else st.session_state.ai_name
            st.markdown(f"**{name}:** {message['content']}")

# Get user input
if prompt := st.chat_input("✨ Ask your assistant..."):
    
    file_context = ""
    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        if uploaded_file.name.endswith(".html"):
            soup = BeautifulSoup(file_contents, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.extract()
            file_contents = soup.get_text(separator=' ', strip=True)
        file_context = f"\n\n[Attached File Content:]\n{file_contents[:6000]}\n"
        
    # Check for URLs in the prompt to scrape
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*')
    urls = url_pattern.findall(prompt)
    
    scraped_context = ""
    if urls:
        for url in urls:
            try:
                # Add a simple user-agent to avoid getting blocked by basic anti-bot walls
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts, styles, navs, footers for cleaner text extraction
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.extract()
                    
                text = soup.get_text(separator=' ', strip=True)
                # Limit the scraped text to 6000 characters to prevent crashing the LLM context window
                scraped_context += f"\n\n[Content scraped from {url}]:\n{text[:6000]}\n"
            except Exception as e:
                scraped_context += f"\n\n[Failed to scrape {url}: {e}]\n"
    
    # If this is the very first message in the chat and it's named "New Chat", auto-rename it
    if len(current_messages) == 0 and st.session_state.chats[st.session_state.current_chat_id]["name"] == "New Chat":
        st.session_state.chats[st.session_state.current_chat_id]["name"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
        
    current_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(f"**{st.session_state.user_name}:** {prompt}")

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                # Prepare temporary messages with the file data and scraped web data
                temp_messages = current_messages.copy()
                
                if file_context or scraped_context:
                    temp_messages[-1] = {"role": "user", "content": prompt + file_context + scraped_context}
                
                response = ollama.chat(model=selected_model, messages=temp_messages)
                reply = response["message"]["content"]
                st.markdown(f"**{st.session_state.ai_name}:** {reply}")
                current_messages.append({"role": "assistant", "content": reply})
                save_data()
            except Exception as e:
                st.error("Engine offline. Run `ollama serve`.")
                
        st.rerun()
