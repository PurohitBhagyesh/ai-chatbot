# Product Requirements Document (PRD)
**Project Name:** Personal AI Assistant
**Version:** 1.0.0
**Target Platform:** Web (Desktop optimized via Streamlit)

## 1. Overview
The Personal AI Assistant is a locally hosted, privacy-first web application designed to serve as a customizable replacement for cloud-based large language models (LLMs) like ChatGPT. By utilizing `Ollama` and Streamlit, the application ensures that all data processing occurs on the user's local hardware.

## 2. Goals & Objectives
- **Privacy First:** Ensure zero data exfiltration by running the inference engine (`llama3.2`) locally.
- **High Customizability:** Allow users to rapidly change the look and feel of the app via external CSS and drag-and-drop background theming.
- **Persistent State:** Maintain chat histories across browser sessions without requiring an external database server like PostgreSQL or MySQL.
- **Extensibility:** Support reading external documents and web pages natively within the chat flow.

## 3. Core Features & Requirements

### 3.1. Local Inference Integration
- **Requirement:** The app must communicate directly with a local `Ollama` server.
- **Fallback:** If `ollama serve` is not running, the application must catch the connection error and gracefully notify the user in the chat UI.

### 3.2. Bespoke User Interface (UI)
- **Requirement:** Override default Streamlit UI components to achieve a macOS-native aesthetic.
- **Details:**
  - Sidebar must be permanently fixed (hamburger menu hidden).
  - Streamlit header/footer must be hidden.
  - Chat bubbles must utilize a "glassmorphism" effect (semi-transparent dark background with a backdrop blur).
  - Main welcome text must be aggressively sized and perfectly centered.
  - Custom names must replace default Streamlit avatars.

### 3.3. Persistent Storage (Multi-Chat)
- **Requirement:** The app must support creating, resuming, renaming, and deleting multiple chat threads.
- **Details:**
  - State must be saved in a local `.chat_data.json` file.
  - The sidebar must display all historical chats with an active indicator (🟢).
  - Chats must have a `⋮` popover menu allowing instant renaming or deletion.
  - New chats must auto-rename themselves based on the first prompt sent.

### 3.4. Dynamic Theming Engine
- **Requirement:** Users must be able to change the app's background image.
- **Details:**
  - Settings expander must include a file uploader specifically for background images (`png`, `jpg`, `jpeg`).
  - Images must be converted to Base64 strings and stored in `.chat_data.json` to persist across reloads.
  - The image must cover the entire viewport (`background-size: cover`).

### 3.5. Web Scraping & File Analysis
- **Requirement:** The assistant must be able to ingest local files and remote URLs.
- **Details:**
  - Sidebar file uploader supports `.txt`, `.md`, `.py`, `.csv`, and `.html`.
  - Chat input automatically parses regex to find `http/https` links.
  - `BeautifulSoup4` must be used to scrape the URL, strip HTML tags (scripts, navs, styles), and append the text invisibly to the LLM's context window.

## 4. Technical Architecture
- **Frontend/Routing:** Python 3 + Streamlit
- **Styling:** Injected HTML/CSS (`style.css`)
- **Backend/LLM:** Ollama (`llama3.2` model)
- **Data Storage:** Local JSON file I/O (`.chat_data.json`)
- **Web Parsing:** `requests` + `beautifulsoup4`

## 5. Future Roadmap (V2)
- Add speech-to-text input capabilities.
- Support multimodal image inputs (if switching to a vision-capable local model like `llava`).
- Export chat history to PDF or Markdown.
