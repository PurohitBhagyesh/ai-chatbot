# 🤖 My Personal Assistant

A completely private, highly customizable, local AI chat application built with Python, Streamlit, and Ollama. 

This app acts as a local replacement for cloud-based AI assistants (like ChatGPT or Claude). It runs the `llama3.2` model entirely on your own hardware, meaning your conversations are 100% private, require no internet connection (except for the built-in web scraper!), and are completely free.

## ✨ Features

- **100% Local & Private:** Powered by Ollama running `llama3.2`. Your data never leaves your computer.
- **Bespoke Apple-Inspired UI:** A completely custom, frosted-glass interface mimicking native macOS desktop apps.
- **Dynamic Theming:** Drag-and-drop any image to instantly set a 4K, full-screen background wallpaper for the app. 
- **Multi-Chat History:** A built-in local JSON database (`.chat_data.json`) automatically saves all your chat threads, allowing you to seamlessly switch between them, rename them, or delete them.
- **Custom Personas:** Customize your display name and your assistant's display name for every conversation.
- **Web Scraping "Eyes":** Paste any URL into the chat, and the app will use `BeautifulSoup` to automatically scrape, clean, and read the webpage to answer your questions about it.
- **File Uploads:** Upload `.txt`, `.md`, `.py`, `.csv`, and `.html` files for the AI to analyze.

## 🚀 Getting Started

### Prerequisites
1. **Install Ollama:** Download from [ollama.com](https://ollama.com/)
2. **Pull the Model:** Open your terminal and run:
   ```bash
   ollama run llama3.2
   ```
3. **Python Environment:** Ensure you have Python installed. 

### Installation
1. Clone this repository to your computer.
2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install streamlit ollama beautifulsoup4 requests
   ```

### Running the App
You will need two terminal windows open:

**Terminal 1 (Backend LLM Engine):**
```bash
ollama serve
```

**Terminal 2 (Frontend UI):**
```bash
source .venv/bin/activate
cd "ai chatbot"
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

## 🛠 Customization

Don't like the fonts or colors? You don't need to know Python to change them! Simply open `style.css` and modify the colors, padding, and layout to match your exact aesthetic preferences.

## 📄 License
This project is for personal use and is completely open source. Feel free to fork and modify it to build your own ultimate personal assistant.
