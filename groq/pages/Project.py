# pages/4_Projects.py

import streamlit as st
from groq import Groq
from datetime import datetime

# ── Page config — SABSE PEHLE ──
st.set_page_config(page_title="Projects", page_icon="🛠️", layout="wide")

# ── Auth guard ──
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first!")
    st.switch_page("app.py")
    st.stop()

# ── Groq Client ──
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ── Sidebar ──
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username  = None
        st.switch_page("app.py")

# ── Session state ──
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "project_steps" not in st.session_state:
    st.session_state.project_steps = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "steps_generated" not in st.session_state:
    st.session_state.steps_generated = False


# ════════════════════════════
#   ALL PROJECTS DATA
# ════════════════════════════

PROJECTS = {
    "🐣 Beginner Projects": [
        {
            "name": "Calculator",
            "icon": "🧮",
            "desc": "Build a simple calculator with basic operations",
            "difficulty": "Easy",
            "time": "1-2 hours",
            "tags": ["functions", "input/output", "conditionals"]
        },
        {
            "name": "Number Guessing Game",
            "icon": "🎲",
            "desc": "Guess the random number the computer picked",
            "difficulty": "Easy",
            "time": "1 hour",
            "tags": ["random", "loops", "conditionals"]
        },
        {
            "name": "To-Do List",
            "icon": "📝",
            "desc": "Create a command-line to-do list app",
            "difficulty": "Easy",
            "time": "2 hours",
            "tags": ["lists", "functions", "file handling"]
        },
        {
            "name": "Password Generator",
            "icon": "🔐",
            "desc": "Generate strong random passwords",
            "difficulty": "Easy",
            "time": "1 hour",
            "tags": ["random", "strings", "functions"]
        },
        {
            "name": "Unit Converter",
            "icon": "📏",
            "desc": "Convert between different units like km to miles",
            "difficulty": "Easy",
            "time": "1-2 hours",
            "tags": ["functions", "math", "input/output"]
        },
        {
            "name": "Rock Paper Scissors",
            "icon": "✊",
            "desc": "Play rock paper scissors against the computer",
            "difficulty": "Easy",
            "time": "1 hour",
            "tags": ["random", "conditionals", "loops"]
        },
        {
            "name": "Temperature Converter",
            "icon": "🌡️",
            "desc": "Convert Celsius to Fahrenheit and vice versa",
            "difficulty": "Easy",
            "time": "30 min",
            "tags": ["functions", "math", "input/output"]
        },
        {
            "name": "Mad Libs Generator",
            "icon": "📖",
            "desc": "Create funny stories by filling in the blanks",
            "difficulty": "Easy",
            "time": "1 hour",
            "tags": ["strings", "input/output", "formatting"]
        },
    ],

    "⚙️ Intermediate Projects": [
        {
            "name": "Snake Game",
            "icon": "🐍",
            "desc": "Classic snake game using Pygame",
            "difficulty": "Medium",
            "time": "4-6 hours",
            "tags": ["pygame", "OOP", "game logic"]
        },
        {
            "name": "Web Scraper",
            "icon": "🌐",
            "desc": "Scrape data from websites using BeautifulSoup",
            "difficulty": "Medium",
            "time": "3-4 hours",
            "tags": ["requests", "BeautifulSoup", "data parsing"]
        },
        {
            "name": "Contact Book",
            "icon": "📒",
            "desc": "Store and manage contacts with SQLite database",
            "difficulty": "Medium",
            "time": "4-5 hours",
            "tags": ["SQLite", "CRUD", "OOP"]
        },
        {
            "name": "Weather App",
            "icon": "☁️",
            "desc": "Fetch real-time weather using OpenWeatherMap API",
            "difficulty": "Medium",
            "time": "3-4 hours",
            "tags": ["API", "requests", "JSON"]
        },
        {
            "name": "Expense Tracker",
            "icon": "💰",
            "desc": "Track daily expenses with charts and reports",
            "difficulty": "Medium",
            "time": "5-6 hours",
            "tags": ["pandas", "matplotlib", "CSV"]
        },
        {
            "name": "Quiz App",
            "icon": "❓",
            "desc": "Multiple choice quiz with scoring system",
            "difficulty": "Medium",
            "time": "3-4 hours",
            "tags": ["OOP", "JSON", "file handling"]
        },
        {
            "name": "URL Shortener",
            "icon": "🔗",
            "desc": "Shorten long URLs using Python and Flask",
            "difficulty": "Medium",
            "time": "4-5 hours",
            "tags": ["Flask", "SQLite", "web"]
        },
        {
            "name": "Alarm Clock",
            "icon": "⏰",
            "desc": "Set alarms with sound notifications using tkinter",
            "difficulty": "Medium",
            "time": "3-4 hours",
            "tags": ["tkinter", "datetime", "threading"]
        },
        {
            "name": "File Organizer",
            "icon": "📁",
            "desc": "Auto-organize files by type into folders",
            "difficulty": "Medium",
            "time": "2-3 hours",
            "tags": ["os", "shutil", "file handling"]
        },
        {
            "name": "Typing Speed Test",
            "icon": "⌨️",
            "desc": "Measure your typing speed in words per minute",
            "difficulty": "Medium",
            "time": "3-4 hours",
            "tags": ["tkinter", "time", "strings"]
        },
    ],

    "🚀 Advanced Projects": [
        {
            "name": "Chat Application",
            "icon": "💬",
            "desc": "Real-time chat app using Python sockets",
            "difficulty": "Hard",
            "time": "8-10 hours",
            "tags": ["sockets", "threading", "networking"]
        },
        {
            "name": "Face Recognition",
            "icon": "👤",
            "desc": "Detect and recognize faces using OpenCV",
            "difficulty": "Hard",
            "time": "6-8 hours",
            "tags": ["OpenCV", "face_recognition", "numpy"]
        },
        {
            "name": "Stock Price Predictor",
            "icon": "📈",
            "desc": "Predict stock prices using machine learning",
            "difficulty": "Hard",
            "time": "8-10 hours",
            "tags": ["scikit-learn", "pandas", "LSTM"]
        },
        {
            "name": "Blog Website",
            "icon": "✍️",
            "desc": "Full-stack blog with Flask and SQLite",
            "difficulty": "Hard",
            "time": "10-12 hours",
            "tags": ["Flask", "SQLite", "HTML/CSS"]
        },
        {
            "name": "Image Classifier",
            "icon": "🖼️",
            "desc": "Classify images using TensorFlow CNN",
            "difficulty": "Hard",
            "time": "8-10 hours",
            "tags": ["TensorFlow", "CNN", "numpy"]
        },
        {
            "name": "Voice Assistant",
            "icon": "🎙️",
            "desc": "Build Alexa-like voice assistant using Python",
            "difficulty": "Hard",
            "time": "8-10 hours",
            "tags": ["speech_recognition", "pyttsx3", "API"]
        },
        {
            "name": "Sentiment Analyzer",
            "icon": "😊",
            "desc": "Analyze text sentiment using NLP and NLTK",
            "difficulty": "Hard",
            "time": "6-8 hours",
            "tags": ["NLTK", "NLP", "machine learning"]
        },
        {
            "name": "Portfolio Website",
            "icon": "🌟",
            "desc": "Build your developer portfolio with Flask",
            "difficulty": "Hard",
            "time": "8-10 hours",
            "tags": ["Flask", "HTML/CSS", "deployment"]
        },
    ],

    "🤖 AI / ML Projects": [
        {
            "name": "Chatbot with Groq",
            "icon": "🤖",
            "desc": "Build an AI chatbot using Groq API and LLaMA",
            "difficulty": "Medium",
            "time": "4-5 hours",
            "tags": ["Groq", "LLaMA", "Streamlit"]
        },
        {
            "name": "Text Summarizer",
            "icon": "📄",
            "desc": "Summarize long articles using Hugging Face",
            "difficulty": "Medium",
            "time": "3-4 hours",
            "tags": ["transformers", "HuggingFace", "NLP"]
        },
        {
            "name": "Object Detection",
            "icon": "🔍",
            "desc": "Detect objects in images using YOLO",
            "difficulty": "Hard",
            "time": "8-10 hours",
            "tags": ["YOLO", "OpenCV", "deep learning"]
        },
        {
            "name": "Recommendation System",
            "icon": "💡",
            "desc": "Build a movie recommendation engine",
            "difficulty": "Hard",
            "time": "8-10 hours",
            "tags": ["scikit-learn", "pandas", "collaborative filtering"]
        },
        {
            "name": "AI Image Generator",
            "icon": "🎨",
            "desc": "Generate images from text using Stable Diffusion",
            "difficulty": "Hard",
            "time": "6-8 hours",
            "tags": ["diffusers", "HuggingFace", "torch"]
        },
        {
            "name": "Resume Parser",
            "icon": "📋",
            "desc": "Extract info from resumes using NLP",
            "difficulty": "Medium",
            "time": "5-6 hours",
            "tags": ["spaCy", "PDF parsing", "NLP"]
        },
    ],

    "🌐 Web Projects": [
        {
            "name": "REST API",
            "icon": "🔌",
            "desc": "Build a REST API with FastAPI and SQLite",
            "difficulty": "Medium",
            "time": "5-6 hours",
            "tags": ["FastAPI", "SQLite", "REST"]
        },
        {
            "name": "E-commerce Backend",
            "icon": "🛒",
            "desc": "Build shopping cart API with Django REST",
            "difficulty": "Hard",
            "time": "12-15 hours",
            "tags": ["Django", "REST", "authentication"]
        },
        {
            "name": "Social Media Dashboard",
            "icon": "📱",
            "desc": "Dashboard to track social media stats",
            "difficulty": "Medium",
            "time": "6-8 hours",
            "tags": ["Streamlit", "API", "charts"]
        },
        {
            "name": "Job Scraper",
            "icon": "💼",
            "desc": "Scrape job listings and send email alerts",
            "difficulty": "Medium",
            "time": "4-5 hours",
            "tags": ["BeautifulSoup", "smtplib", "scheduling"]
        },
    ]
}


# ════════════════════════════
#   HELPER — Generate Steps
# ════════════════════════════

def generate_project_steps(project_name: str) -> str:
    """Ask Groq to generate step by step guide for a project"""
    prompt = f"""
You are an expert Python teacher. Generate a detailed step-by-step guide to build this Python project: "{project_name}"

Format your response EXACTLY like this:

## 📦 Prerequisites
List all libraries to install with pip install commands

## 🗂️ Project Structure
Show the folder and file structure

## Step 1: [Step Title]
Explain what to do in this step clearly.
Include complete working Python code.

## Step 2: [Step Title]
Explain what to do in this step clearly.
Include complete working Python code.

## Step 3: [Step Title]
...continue all steps...

## ✅ Final Result
Describe what the finished project looks like and how to run it.

## 💡 How to Improve
Give 3-5 ideas to extend or improve this project.

Rules:
- Give complete, copy-paste ready code for each step
- Be very detailed and beginner friendly
- Minimum 5 steps, maximum 10 steps
- Each step must have explanation + code
"""
    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        messages    = [{"role": "user", "content": prompt}],
        max_tokens  = 4000,
        temperature = 0.5
    )
    return response.choices[0].message.content


# ════════════════════════════
#   PAGE UI
# ════════════════════════════

# ── If a project is selected — show steps ──
if st.session_state.selected_project:

    project = st.session_state.selected_project

    # Back button
    if st.button("← Back to Projects", key="back_btn"):
        st.session_state.selected_project  = None
        st.session_state.project_steps     = []
        st.session_state.current_step      = 0
        st.session_state.steps_generated   = False
        st.rerun()

    st.divider()

    # Project header
    col_icon, col_info = st.columns([1, 8])
    with col_icon:
        st.markdown(f"<div style='font-size:64px;text-align:center'>{project['icon']}</div>", unsafe_allow_html=True)
    with col_info:
        st.title(project["name"])
        st.markdown(f"**{project['desc']}**")

        tag_cols = st.columns(len(project["tags"]) + 2)
        with tag_cols[0]:
            color = "#2d9f6a" if project["difficulty"] == "Easy" else "#c07020" if project["difficulty"] == "Medium" else "#cc3333"
            st.markdown(f"<span style='background:{color};color:white;padding:3px 10px;border-radius:12px;font-size:12px'>⚡ {project['difficulty']}</span>", unsafe_allow_html=True)
        with tag_cols[1]:
            st.markdown(f"<span style='background:#2d6a9f;color:white;padding:3px 10px;border-radius:12px;font-size:12px'>⏱️ {project['time']}</span>", unsafe_allow_html=True)
        for j, tag in enumerate(project["tags"]):
            with tag_cols[j + 2]:
                st.markdown(f"<span style='background:#444;color:white;padding:3px 10px;border-radius:12px;font-size:12px'>#{tag}</span>", unsafe_allow_html=True)

    st.divider()

    # Generate steps
    if not st.session_state.steps_generated:
        with st.spinner(f"🤖 Generating step-by-step guide for {project['name']}..."):
            content = generate_project_steps(project["name"])
            st.session_state.project_steps   = content
            st.session_state.steps_generated = True
            st.session_state.current_step    = 0

    # Show content
    if st.session_state.project_steps:

        # Parse steps from content
        content   = st.session_state.project_steps
        sections  = content.split("## ")
        sections  = [s for s in sections if s.strip()]

        # Progress bar
        total_sections = len(sections)
        current        = st.session_state.current_step

        st.markdown(f"**Step {current + 1} of {total_sections}**")
        st.progress((current + 1) / total_sections)
        st.divider()

        # Show current section
        current_section = sections[current]
        lines           = current_section.split("\n", 1)
        section_title   = lines[0].strip()
        section_content = lines[1].strip() if len(lines) > 1 else ""

        st.subheader(f"📌 {section_title}")
        st.markdown(section_content)

        st.divider()

        # Navigation buttons
        col_prev, col_all, col_next = st.columns([2, 3, 2])

        with col_prev:
            if current > 0:
                if st.button("⬅️ Previous Step", use_container_width=True):
                    st.session_state.current_step -= 1
                    st.rerun()

        with col_all:
            # Show all steps toggle
            if st.button("📄 Show All Steps at Once", use_container_width=True):
                st.session_state.current_step = -1   # -1 = show all
                st.rerun()

        with col_next:
            if current < total_sections - 1:
                if st.button("Next Step ➡️", use_container_width=True, type="primary"):
                    st.session_state.current_step += 1
                    st.rerun()
            else:
                st.success("🎉 Project Complete!")

        # Show all mode
        if st.session_state.current_step == -1:
            st.divider()
            st.subheader("📄 Complete Guide")
            st.markdown(content)

            # Reset to step mode
            if st.button("🔢 Go Back to Step Mode", use_container_width=True):
                st.session_state.current_step = 0
                st.rerun()

        st.divider()

        # Download guide
        st.download_button(
            label       = "📥 Download Complete Guide",
            data        = content,
            file_name   = f"{project['name'].replace(' ', '_')}_guide.md",
            mime        = "text/markdown",
            use_container_width=True
        )

# ── Project list page ──
else:

    st.title("🛠️ Python Projects")
    st.caption("Click any project to get a step-by-step guide — powered by AI!")
    st.divider()

    # Search bar
    search = st.text_input(
        "🔍 Search projects...",
        placeholder="e.g. snake, weather, chatbot...",
        label_visibility="collapsed"
    )

    st.divider()

    # Show all categories
    for category, projects in PROJECTS.items():

        # Filter by search
        if search:
            projects = [
                p for p in projects
                if search.lower() in p["name"].lower()
                or search.lower() in p["desc"].lower()
                or any(search.lower() in tag for tag in p["tags"])
            ]
            if not projects:
                continue

        st.markdown(f"### {category}")

        cols = st.columns(4)
        for i, project in enumerate(projects):

            with cols[i % 4]:
                # Difficulty color
                diff_color = (
                    "#2d9f6a" if project["difficulty"] == "Easy"
                    else "#c07020" if project["difficulty"] == "Medium"
                    else "#cc3333"
                )

                # Project card
                st.markdown(f"""
                <div style="
                    background: var(--background-color);
                    border: 1px solid #333;
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 8px;
                    min-height: 160px;
                ">
                    <div style="font-size:36px;text-align:center">{project['icon']}</div>
                    <h4 style="text-align:center;margin:8px 0 4px 0">{project['name']}</h4>
                    <p style="font-size:12px;color:#aaa;text-align:center;margin:0 0 8px 0">{project['desc']}</p>
                    <div style="text-align:center">
                        <span style="background:{diff_color};color:white;padding:2px 8px;border-radius:8px;font-size:11px">{project['difficulty']}</span>
                        <span style="background:#2d6a9f;color:white;padding:2px 8px;border-radius:8px;font-size:11px;margin-left:4px">{project['time']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(
                    f"🧑‍🏫 Start Project",
                    key     = f"proj_{category}_{project['name']}",
                    use_container_width=True,
                    type    = "primary"
                ):
                    st.session_state.selected_project  = project
                    st.session_state.project_steps     = []
                    st.session_state.current_step      = 0
                    st.session_state.steps_generated   = False
                    st.rerun()

        st.divider()

    # Total count
    total = sum(len(p) for p in PROJECTS.values())
    st.caption(f"Total: {total} projects available — more coming soon!")