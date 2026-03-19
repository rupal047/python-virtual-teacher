 
import streamlit as st
from auth import show_auth_page
from database import get_user_stats, get_quiz_stats

# ── Page config — SABSE PEHLE ──
st.set_page_config(
    page_title            = "Python Virtual Teacher",
    page_icon             = "🧑‍🏫",
    layout                = "wide",
    initial_sidebar_state = "collapsed"
)

# ── CSS Styles ──
st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }

    /* Navbar container */
    .navbar-wrap {
        background: linear-gradient(90deg, #0d1b2a, #1a2f4a);
        border-radius: 12px;
        border: 1px solid #2d4a6a;
        padding: 6px 20px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
    }

    /* Navbar buttons override */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #a8c8e8 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 5px 12px !important;
        border-radius: 8px !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: #2d6a9f !important;
        color: #ffffff !important;
    }

    /* Stats cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #0d1b2a, #1a2f4a);
        border: 1px solid #2d4a6a;
        border-radius: 12px;
        padding: 16px;
    }

    /* Footer */
    .footer {
        margin-top: 48px;
        padding: 32px;
        background: linear-gradient(90deg, #0d1b2a, #1a2f4a);
        border-radius: 12px;
        border: 1px solid #2d4a6a;
        text-align: center;
    }
    .footer-divider {
        border: none;
        border-top: 1px solid #2d4a6a;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ──
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# ── Auth check ──
if not st.session_state.logged_in:
    show_auth_page()
    st.stop()

# ── Sidebar logout ──
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username  = None
        st.rerun()

# ════════════════════════════
#   NAVBAR — Streamlit buttons
# ════════════════════════════
nb_brand, nb_home, nb_teacher, nb_quiz, nb_proj, nb_dash, nb_user = st.columns([3, 1, 1.2, 1.2, 1.2, 1.3, 2])

with nb_brand:
    st.markdown("""
    <div style="
        padding: 8px 0;
        height: 46px;
        display: flex;
        align-items: center;
    ">
        <span style="font-size:17px; font-weight:700; color:#ffffff;">🧑‍🏫 Python Virtual Teacher</span>
    </div>
    """, unsafe_allow_html=True)

with nb_home:
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.switch_page("app.py")

with nb_teacher:
    if st.button("🧑‍🏫 Teacher", use_container_width=True, key="nav_teacher"):
        st.switch_page("pages/PythonTeacher.py")

with nb_quiz:
    if st.button("🧠 Quizzes", use_container_width=True, key="nav_quiz"):
        st.switch_page("pages/Quizzes.py")

with nb_proj:
    if st.button("🛠️ Projects", use_container_width=True, key="nav_proj"):
        st.switch_page("pages/Project.py")

with nb_dash:
    if st.button("📊 Dashboard", use_container_width=True, key="nav_dash"):
        st.switch_page("pages/Dashboard.py")

with nb_user:
    st.markdown(f"""
    <div style="
        padding: 8px 0;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    ">
        <span style="color:#a8e8c8; font-size:14px; font-weight:500;">👤 {st.session_state.username}</span>
    </div>
    """, unsafe_allow_html=True)

# Navbar background wrapper
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"]:first-of-type {
    background: linear-gradient(90deg, #0d1b2a, #1a2f4a);
    border-radius: 12px;
    border: 1px solid #2d4a6a;
    padding: 4px 16px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════
#   HERO SECTION
# ════════════════════════════
st.markdown(f"""
<div style="text-align:center; padding: 36px 20px 28px 20px;">
    <div style="font-size:64px; margin-bottom:12px;">🧑‍🏫</div>
    <h1 style="font-size:34px; font-weight:700; margin:0 0 8px 0;">
        Welcome back, <span style="color:#4a9fd4;">{st.session_state.username}</span>! 👋
    </h1>
    <p style="color:#888; font-size:16px; margin:0;">
        Your personal Python learning platform — Learn, Practice, Build!
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ════════════════════════════
#   NAVIGATION CARDS
# ════════════════════════════
st.markdown("### 🚀 Jump To")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 16px; padding: 28px 20px;
        text-align: center; border: 1px solid #2d6a9f; min-height: 180px;
    ">
        <div style="font-size:48px;">🧑‍🏫</div>
        <h3 style="color:#ffffff; margin:10px 0 6px 0;">Python Teacher</h3>
        <p style="color:#a8c8e8; font-size:13px; margin:0;">
            Ask any Python question<br>via text or voice
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧑‍🏫 Open Teacher", use_container_width=True, type="primary", key="btn_chat"):
        st.switch_page("pages/PythonTeacher.py")

with col2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #3a1e5f, #7a2d9f);
        border-radius: 16px; padding: 28px 20px;
        text-align: center; border: 1px solid #7a2d9f; min-height: 180px;
    ">
        <div style="font-size:48px;">🧠</div>
        <h3 style="color:#ffffff; margin:10px 0 6px 0;">Quizzes</h3>
        <p style="color:#c8a8e8; font-size:13px; margin:0;">
            Test your Python knowledge<br>with AI quizzes
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🧠 Open Quizzes", use_container_width=True, type="primary", key="btn_quiz"):
        st.switch_page("pages/Quizzes.py")

with col3:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #5f3a1e, #9f6a2d);
        border-radius: 16px; padding: 28px 20px;
        text-align: center; border: 1px solid #9f6a2d; min-height: 180px;
    ">
        <div style="font-size:48px;">🛠️</div>
        <h3 style="color:#ffffff; margin:10px 0 6px 0;">Projects</h3>
        <p style="color:#e8c8a8; font-size:13px; margin:0;">
            Build real Python projects<br>with step-by-step AI guide
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🛠️ Open Projects", use_container_width=True, type="primary", key="btn_proj"):
        st.switch_page("pages/Project.py")

with col4:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e5f3a, #2d9f6a);
        border-radius: 16px; padding: 28px 20px;
        text-align: center; border: 1px solid #2d9f6a; min-height: 180px;
    ">
        <div style="font-size:48px;">📊</div>
        <h3 style="color:#ffffff; margin:10px 0 6px 0;">Dashboard</h3>
        <p style="color:#a8e8c8; font-size:13px; margin:0;">
            Track your learning progress<br>and quiz scores
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📊 Open Dashboard", use_container_width=True, type="primary", key="btn_dash"):
        st.switch_page("pages/Dashboard.py")

st.divider()

# ════════════════════════════
#   QUICK STATS
# ════════════════════════════
st.markdown("### 📈 Your Quick Stats")
st.markdown("<br>", unsafe_allow_html=True)

stats      = get_user_stats(st.session_state.username)
quiz_stats = get_quiz_stats(st.session_state.username)

sc1, sc2, sc3, sc4, sc5 = st.columns(5)
with sc1:
    st.metric("💬 Questions Asked", value=stats["total_questions"])
with sc2:
    st.metric("📅 Days Active",     value=stats["days_active"])
with sc3:
    st.metric("🧠 Quizzes Taken",   value=quiz_stats["total_quizzes"])
with sc4:
    st.metric(
        "🏆 Best Quiz Score",
        value=f"{quiz_stats['best_score']}%" if quiz_stats["total_quizzes"] > 0 else "N/A"
    )
with sc5:
    st.metric("🔥 Last Active", value=stats["last_active"])

st.divider()

# ════════════════════════════
#   FEATURES SECTION
# ════════════════════════════
st.markdown("### ✨ What You Can Do")
st.markdown("<br>", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.markdown("""
    <div style="text-align:center; padding:16px;">
        <div style="font-size:36px;">🎤</div>
        <h4 style="margin:8px 0 4px 0;">Voice Input</h4>
        <p style="color:#888; font-size:13px;">Ask questions using your microphone</p>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div style="text-align:center; padding:16px;">
        <div style="font-size:36px;">🤖</div>
        <h4 style="margin:8px 0 4px 0;">AI Powered</h4>
        <p style="color:#888; font-size:13px;">Powered by LLaMA 3.3 70B via Groq</p>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div style="text-align:center; padding:16px;">
        <div style="font-size:36px;">📊</div>
        <h4 style="margin:8px 0 4px 0;">Track Progress</h4>
        <p style="color:#888; font-size:13px;">See your learning journey over time</p>
    </div>
    """, unsafe_allow_html=True)

with f4:
    st.markdown("""
    <div style="text-align:center; padding:16px;">
        <div style="font-size:36px;">🛠️</div>
        <h4 style="margin:8px 0 4px 0;">40+ Projects</h4>
        <p style="color:#888; font-size:13px;">Real projects with step-by-step guides</p>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════
#   FOOTER
# ════════════════════════════
st.markdown("""
<div class="footer">
    <div style="font-size:28px; margin-bottom:8px;">🧑‍🏫</div>
    <h3 style="color:#ffffff; margin:0 0 4px 0;">Python Virtual Teacher</h3>
    <p style="color:#667788; font-size:13px; margin:0 0 16px 0;">
        Your AI-powered Python learning companion
    </p>
    <div style="display:flex; justify-content:center; gap:24px; margin-bottom:16px; flex-wrap:wrap;">
        <span style="color:#a8c8e8; font-size:13px;">🧑‍🏫 Python Teacher</span>
        <span style="color:#a8c8e8; font-size:13px;">🧠 Quizzes</span>
        <span style="color:#a8c8e8; font-size:13px;">🛠️ Projects</span>
        <span style="color:#a8c8e8; font-size:13px;">📊 Dashboard</span>
    </div>
    <hr class="footer-divider">
    <div style="display:flex; justify-content:center; gap:32px; margin-bottom:12px; flex-wrap:wrap;">
        <span style="color:#667788; font-size:12px;">🤖 LLaMA 3.3 70B</span>
        <span style="color:#667788; font-size:12px;">⚡ Groq API</span>
        <span style="color:#667788; font-size:12px;">🎙️ Whisper STT</span>
        <span style="color:#667788; font-size:12px;">🗄️ MongoDB</span>
        <span style="color:#667788; font-size:12px;">🚀 Streamlit</span>
    </div>
    <p style="color:#667788; font-size:12px; margin:0;">
        © 2025-26 Python Virtual Teacher — Built with ❤️ using Python
    </p>
</div>
""", unsafe_allow_html=True)