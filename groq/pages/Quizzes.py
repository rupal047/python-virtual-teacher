 
import streamlit as st
from groq import Groq
import json
import re
from datetime import datetime
from database import save_quiz_result

# ── Page config — SABSE PEHLE HONA CHAHIYE ──
st.set_page_config(page_title="Quizzes", page_icon="🧠", layout="wide")

# ── Auth guard ──
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first!")
    st.switch_page("app.py")
    st.stop()

# ── Groq Client ──
client = Groq(api_key="")

# ── Sidebar ──
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username  = None
        st.switch_page("app.py")

# ── Session state for quiz ──
for key, val in {
    "quiz_started":      False,
    "quiz_topic":        None,
    "quiz_questions":    [],
    "quiz_answers":      {},
    "quiz_submitted":    False,
    "quiz_score":        0,
    "rt_quiz_questions": [],
    "rt_quiz_answers":   {},
    "rt_quiz_submitted": False,
    "rt_quiz_score":     0,
    "rt_quiz_topic":     ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ════════════════════════════
#   HELPER FUNCTIONS
# ════════════════════════════

def generate_quiz(topic: str, num_questions: int) -> list:
    prompt = f"""
Generate exactly {num_questions} multiple choice questions about Python topic: "{topic}".
Rules:
- Each question must have exactly 4 options labeled A, B, C, D
- Clearly mark the correct answer
- Mix easy, medium, and hard questions
- Return ONLY in this exact format:

Q1: <question text>
A: <option>
B: <option>
C: <option>
D: <option>
ANSWER: <A or B or C or D>

Continue for all {num_questions} questions.
"""
    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        messages    = [{"role": "user", "content": prompt}],
        max_tokens  = 3000,
        temperature = 0.7
    )
    return parse_quiz(response.choices[0].message.content)


def parse_quiz(raw_text: str) -> list:
    questions = []
    blocks    = raw_text.strip().split("\n\n")
    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if len(lines) < 6:
            continue
        try:
            question_text = lines[0].split(":", 1)[-1].strip()
            options = {}
            answer  = ""
            for line in lines[1:]:
                if line.startswith("A:"):         options["A"] = line[2:].strip()
                elif line.startswith("B:"):        options["B"] = line[2:].strip()
                elif line.startswith("C:"):        options["C"] = line[2:].strip()
                elif line.startswith("D:"):        options["D"] = line[2:].strip()
                elif line.startswith("ANSWER:"):   answer = line.split(":")[-1].strip().upper()
            if question_text and len(options) == 4 and answer in ["A","B","C","D"]:
                questions.append({
                    "question": question_text,
                    "options":  options,
                    "answer":   answer
                })
        except Exception:
            continue
    return questions


def generate_quiz_json(topic: str, num_questions: int) -> list:
    prompt = f"""
Generate exactly {num_questions} multiple choice questions about Python topic: "{topic}".
Return ONLY a valid JSON array, no extra text, no markdown backticks:
[{{"question": "...", "options": {{"A":"...","B":"...","C":"...","D":"..."}}, "answer": "A"}}]
"""
    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        messages    = [{"role": "user", "content": prompt}],
        max_tokens  = 4000,
        temperature = 0.7
    )
    raw = response.choices[0].message.content
    try:
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return []


def show_result_section(questions, answers, score, topic, key_prefix):
    total   = len(questions)
    percent = int((score / total) * 100) if total > 0 else 0

    st.subheader(f"🎯 Results: {topic}")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("✅ Correct", value=score)
    with col2: st.metric("❌ Wrong",   value=total - score)
    with col3: st.metric("📊 Score",   value=f"{percent}%")

    if percent == 100:    st.success("🏆 Perfect Score! Python Master!")
    elif percent >= 80:   st.success("🎉 Excellent!")
    elif percent >= 60:   st.warning("👍 Good job! Keep practicing!")
    elif percent >= 40:   st.warning("📚 Review the topic and try again.")
    else:                 st.error("💪 Keep practicing!")

    st.progress(percent / 100)
    st.divider()

    st.subheader("📋 Answer Review")
    for i, q in enumerate(questions):
        user_ans    = answers.get(i, "")
        correct_ans = q["answer"]
        if user_ans == correct_ans:
            st.success(f"✅ Q{i+1}. {q['question']}")
        else:
            st.error(f"❌ Q{i+1}. {q['question']}")
        col_a, col_b = st.columns(2)
        with col_a: st.markdown(f"**Your answer:** {user_ans}) {q['options'].get(user_ans,'N/A')}")
        with col_b: st.markdown(f"**Correct:** {correct_ans}) {q['options'].get(correct_ans,'')}")
        st.markdown("---")

    result_text = (
        f"Python Quiz Results\nUser: {st.session_state.username}\n"
        f"Topic: {topic}\nDate: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
        f"Score: {score}/{total} ({percent}%)\n{'='*40}\n\n"
    )
    for i, q in enumerate(questions):
        user_ans    = answers.get(i, "")
        correct_ans = q["answer"]
        status      = "CORRECT" if user_ans == correct_ans else "WRONG"
        result_text += (
            f"Q{i+1}: {q['question']}\n"
            f"Your Answer: {user_ans}) {q['options'].get(user_ans,'')}\n"
            f"Correct: {correct_ans}) {q['options'].get(correct_ans,'')}\n"
            f"Status: {status}\n\n"
        )
    return percent, result_text


# ════════════════════════════
#   QUIZ PAGE UI
# ════════════════════════════
st.title("🧠 Python Quiz Center")
st.caption("Test your Python knowledge — AI generated questions!")

# ── SECTION 1 — Real-Time AI Quiz ──
st.markdown("## 🤖 Real-Time AI Quiz")
st.markdown("Type **any** Python topic — AI generates questions instantly!")

col_topic, col_num, col_btn = st.columns([5, 2, 2])
with col_topic:
    custom_topic = st.text_input(
        "topic",
        placeholder="e.g. Python decorators, NumPy...",
        label_visibility="collapsed"
    )
with col_num:
    num_q = st.selectbox(
        "num",
        options=[5, 10, 15, 20],
        index=1,
        label_visibility="collapsed"
    )
with col_btn:
    generate_btn = st.button("🚀 Generate Quiz", use_container_width=True, type="primary")

if generate_btn and custom_topic.strip():
    st.session_state.rt_quiz_submitted = False
    st.session_state.rt_quiz_questions = []
    st.session_state.rt_quiz_answers   = {}
    st.session_state.rt_quiz_score     = 0
    st.session_state.rt_quiz_topic     = custom_topic.strip()

    with st.spinner(f"🤖 Generating {num_q} questions on '{custom_topic}'..."):
        questions = generate_quiz_json(custom_topic.strip(), num_q)

    if not questions:
        st.error("Could not generate questions. Try a different topic!")
    else:
        st.session_state.rt_quiz_questions = questions
        st.success(f"✅ {len(questions)} questions generated!")

elif generate_btn:
    st.warning("⚠️ Please enter a topic first!")

# ── Real-time questions ──
if st.session_state.rt_quiz_questions and not st.session_state.rt_quiz_submitted:
    st.divider()
    st.markdown(f"### 📝 {st.session_state.rt_quiz_topic}")

    rt_answers = {}
    for i, q in enumerate(st.session_state.rt_quiz_questions):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        selected = st.radio(
            label            = f"rt_{i}",
            options          = ["A", "B", "C", "D"],
            format_func      = lambda x, q=q: f"{x})  {q['options'].get(x,'')}",
            key              = f"rt_q_{i}_{st.session_state.rt_quiz_topic}",
            label_visibility = "collapsed"
        )
        rt_answers[i] = selected
        st.markdown("---")

    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        if st.button("✅ Submit Quiz", use_container_width=True, type="primary", key="rt_submit"):
            score   = sum(
                1 for i, q in enumerate(st.session_state.rt_quiz_questions)
                if rt_answers.get(i) == q["answer"]
            )
            total   = len(st.session_state.rt_quiz_questions)
            percent = int((score / total) * 100) if total > 0 else 0
            st.session_state.rt_quiz_score     = score
            st.session_state.rt_quiz_answers   = rt_answers
            st.session_state.rt_quiz_submitted = True
            save_quiz_result(
                st.session_state.username,
                st.session_state.rt_quiz_topic,
                score, total, percent
            )
            st.rerun()

# ── Real-time result ──
if st.session_state.rt_quiz_submitted and st.session_state.rt_quiz_questions:
    percent, result_text = show_result_section(
        st.session_state.rt_quiz_questions,
        st.session_state.rt_quiz_answers,
        st.session_state.rt_quiz_score,
        st.session_state.rt_quiz_topic,
        "rt"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Try Again", use_container_width=True, key="rt_retry"):
            st.session_state.rt_quiz_submitted = False
            st.session_state.rt_quiz_questions = []
            st.session_state.rt_quiz_answers   = {}
            st.rerun()
    with col2:
        if st.button("📚 New Topic", use_container_width=True, key="rt_new"):
            st.session_state.rt_quiz_submitted = False
            st.session_state.rt_quiz_questions = []
            st.session_state.rt_quiz_answers   = {}
            st.rerun()
    with col3:
        st.download_button(
            "📥 Download Result", result_text,
            file_name = f"rt_quiz_{datetime.now().strftime('%d%m%Y')}.txt",
            mime      = "text/plain",
            use_container_width=True,
            key       = "rt_download"
        )

st.divider()

# ════════════════════════════
#   SECTION 2 — PRESET TOPICS
# ════════════════════════════
st.markdown("## 📚 Or Choose a Preset Topic")
st.divider()

QUIZ_TOPICS = {
    "🐣 Beginner": [
        "Python Variables and Data Types", "Python Strings", "Python Lists",
        "Python Tuples", "Python Dictionaries", "Python Sets",
        "Python If Else Conditions", "Python For Loops", "Python While Loops",
        "Python Functions Basics", "Python Input and Output", "Python Type Casting",
    ],
    "⚙️ Intermediate": [
        "Python List Comprehensions", "Python Lambda Functions", "Python Map Filter Reduce",
        "Python File Handling", "Python Exception Handling", "Python Object Oriented Programming",
        "Python Inheritance", "Python Modules and Packages", "Python Iterators and Generators",
        "Python Decorators", "Python Regular Expressions", "Python JSON Handling",
    ],
    "🚀 Advanced": [
        "Python Multithreading", "Python Multiprocessing", "Python Async and Await",
        "Python Memory Management", "Python Design Patterns", "Python Metaclasses",
        "Python Context Managers", "Python Descriptors", "Python C Extensions",
        "Python Performance Optimization",
    ],
    "📦 Libraries": [
        "NumPy Basics", "Pandas DataFrames", "Matplotlib Plotting",
        "Scikit-learn Machine Learning", "TensorFlow Basics", "FastAPI Basics",
        "Flask Web Framework", "SQLAlchemy ORM", "Streamlit Apps", "Requests HTTP Library",
    ]
}

# ── Topic selector ──
if not st.session_state.quiz_started:
    for category, topics in QUIZ_TOPICS.items():
        st.markdown(f"### {category}")
        cols = st.columns(3)
        for i, topic in enumerate(topics):
            with cols[i % 3]:
                if st.button(topic, key=f"topic_{topic}", use_container_width=True):
                    st.session_state.quiz_topic     = topic
                    st.session_state.quiz_started   = True
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers   = {}
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_score     = 0
                    st.rerun()
        st.divider()

# ── Preset quiz in progress ──
elif st.session_state.quiz_started and not st.session_state.quiz_submitted:
    st.subheader(f"📝 Quiz: {st.session_state.quiz_topic}")

    col_info, col_btn = st.columns([8, 2])
    with col_info:
        st.info(f"Topic: **{st.session_state.quiz_topic}** — Answer all then Submit!")
    with col_btn:
        if st.button("🔙 Back to Topics", use_container_width=True):
            st.session_state.quiz_started   = False
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers   = {}
            st.rerun()

    if not st.session_state.quiz_questions:
        with st.spinner(f"🤖 Generating quiz on {st.session_state.quiz_topic}..."):
            st.session_state.quiz_questions = generate_quiz(
                st.session_state.quiz_topic, 10
            )

    questions = st.session_state.quiz_questions

    if not questions:
        st.error("Could not generate questions. Please try again!")
        if st.button("🔄 Try Again"):
            st.session_state.quiz_questions = []
            st.rerun()
    else:
        st.markdown(f"**Total Questions: {len(questions)}**")
        st.divider()

        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            selected = st.radio(
                label            = f"Q{i+1}",
                options          = ["A", "B", "C", "D"],
                format_func      = lambda x, q=q: f"{x}) {q['options'].get(x,'')}",
                key              = f"q_{i}",
                label_visibility = "collapsed"
            )
            st.session_state.quiz_answers[i] = selected
            st.markdown("---")

        col1, col2, col3 = st.columns([2, 2, 2])
        with col2:
            if st.button("✅ Submit Quiz", use_container_width=True, type="primary"):
                score   = sum(
                    1 for i, q in enumerate(questions)
                    if st.session_state.quiz_answers.get(i) == q["answer"]
                )
                total   = len(questions)
                percent = int((score / total) * 100) if total > 0 else 0
                st.session_state.quiz_score     = score
                st.session_state.quiz_submitted = True
                save_quiz_result(
                    st.session_state.username,
                    st.session_state.quiz_topic,
                    score, total, percent
                )
                st.rerun()

# ── Preset quiz result ──
elif st.session_state.quiz_submitted:
    percent, result_text = show_result_section(
        st.session_state.quiz_questions,
        st.session_state.quiz_answers,
        st.session_state.quiz_score,
        st.session_state.quiz_topic,
        "preset"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Retry Same Topic", use_container_width=True):
            st.session_state.quiz_submitted = False
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers   = {}
            st.session_state.quiz_score     = 0
            st.rerun()
    with col2:
        if st.button("📚 Choose New Topic", use_container_width=True):
            st.session_state.quiz_started   = False
            st.session_state.quiz_submitted = False
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers   = {}
            st.session_state.quiz_score     = 0
            st.rerun()
    with col3:
        st.download_button(
            "📥 Download Result", result_text,
            file_name = f"{st.session_state.username}_quiz_{datetime.now().strftime('%d%m%Y')}.txt",
            mime      = "text/plain",
            use_container_width=True
        )
