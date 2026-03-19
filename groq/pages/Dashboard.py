# pages/3_📊_Dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from database import get_user_stats, get_quiz_stats, get_chat_history
``
# ── Auth guard ──
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first!")
    st.switch_page("app.py")
    st.stop()

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username  = None
        st.switch_page("app.py")

st.title("📊 Performance Dashboard")
st.caption(f"Your learning progress — {st.session_state.username}")
st.divider()

# ── Chatbot Stats ──
stats = get_user_stats(st.session_state.username)

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("💬 Questions Asked", value=stats["total_questions"])
with col2: st.metric("🤖 Bot Replies",     value=stats["total_replies"])
with col3: st.metric("📅 Days Active",     value=stats["days_active"])
with col4: st.metric("🔥 Last Active",     value=stats["last_active"])
with col5: st.metric("🗓️ Member Since",    value=stats["member_since"])

st.divider()

# ── Daily Chatbot Activity ──
st.subheader("📈 Daily Chatbot Activity")
daily_counts = stats.get("daily_counts", [])

if daily_counts:
    df = pd.DataFrame(daily_counts)
    df.columns = ["Date", "Questions Asked"]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    fig = px.bar(df, x="Date", y="Questions Asked",
        title="Chatbot Questions Per Day",
        color="Questions Asked", color_continuous_scale="blues")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No chatbot activity data yet!")

st.divider()

# ── Questions vs Replies ──
st.subheader("🥧 Questions vs Replies Ratio")
total_q = stats["total_questions"]
total_r = stats["total_replies"]

if total_q > 0 or total_r > 0:
    pie_df = pd.DataFrame({"Type": ["Your Questions", "Bot Replies"], "Count": [total_q, total_r]})
    fig2 = px.pie(pie_df, names="Type", values="Count",
        color_discrete_sequence=["#636EFA", "#EF553B"], hole=0.4)
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#ffffff")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No data for chart yet!")

st.divider()

# ── Quiz Performance ──
st.subheader("🧠 Quiz Performance")
quiz_stats = get_quiz_stats(st.session_state.username)

if quiz_stats["total_quizzes"] == 0:
    st.info("No quizzes taken yet! Go to Quizzes page and test yourself.")
else:
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1: st.metric("🧠 Total Quizzes",  value=quiz_stats["total_quizzes"])
    with qc2: st.metric("📊 Average Score",  value=f"{quiz_stats['average_score']}%")
    with qc3: st.metric("🏆 Best Score",     value=f"{quiz_stats['best_score']}%")
    with qc4: st.metric("📉 Lowest Score",   value=f"{quiz_stats['worst_score']}%")

    st.divider()

    # Score progress line chart
    st.subheader("📈 Quiz Score Progress")
    if quiz_stats["quiz_history"]:
        df_p = pd.DataFrame(quiz_stats["quiz_history"])
        fig_line = px.line(df_p, x="attempt", y="percent",
            title="Score % per Quiz Attempt", markers=True,
            labels={"attempt": "Attempt #", "percent": "Score (%)"},
            hover_data=["topic", "score", "date"],
            color_discrete_sequence=["#00CC96"])
        fig_line.add_hline(y=quiz_stats["average_score"], line_dash="dash",
            line_color="#FFA500",
            annotation_text=f"Average: {quiz_stats['average_score']}%",
            annotation_position="top right")
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", yaxis=dict(range=[0, 105]), showlegend=False)
        st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # Topic-wise bar chart
    st.subheader("📊 Performance by Topic")
    if quiz_stats["topic_scores"]:
        df_t = pd.DataFrame(quiz_stats["topic_scores"])
        fig_t = px.bar(df_t, x="topic", y="average",
            title="Average Score per Topic",
            color="average",
            color_continuous_scale=[[0.0,"#E24B4A"],[0.4,"#EF9F27"],[0.7,"#00CC96"],[1.0,"#00CC96"]],
            labels={"topic": "Topic", "average": "Avg (%)"},
            text="average", hover_data=["attempts"])
        fig_t.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_t.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", xaxis_tickangle=-35,
            yaxis=dict(range=[0, 115]), coloraxis_showscale=False, showlegend=False)
        st.plotly_chart(fig_t, use_container_width=True)

    st.divider()

    # Daily quiz activity
    st.subheader("📅 Daily Quiz Activity")
    if quiz_stats["daily_quiz_data"]:
        df_d = pd.DataFrame(quiz_stats["daily_quiz_data"])
        df_d["date"] = pd.to_datetime(df_d["date"])
        fig_d = px.bar(df_d, x="date", y="quizzes",
            title="Quizzes Taken Per Day",
            color="quizzes", color_continuous_scale="purples",
            labels={"date": "Date", "quizzes": "Quizzes"})
        fig_d.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", coloraxis_showscale=False, showlegend=False)
        st.plotly_chart(fig_d, use_container_width=True)

    st.divider()

    # Recent quiz history table
    st.subheader("📋 Recent Quiz History")
    for q in quiz_stats["quiz_history"][-10:][::-1]:
        icon = "🟢" if q["percent"] >= 80 else "🟡" if q["percent"] >= 50 else "🔴"
        c1, c2, c3 = st.columns([4, 2, 2])
        with c1: st.markdown(f"{icon} **{q['topic']}**")
        with c2: st.markdown(f"Score: **{q['score']}** — {q['percent']}%")
        with c3: st.markdown(f"📅 {q['date']}")

st.divider()

# ── Chat History ──
st.subheader("📝 Your Chat History")
history = get_chat_history(st.session_state.username)

if not history:
    st.info("No chat history yet!")
else:
    for msg in history[-20:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.divider()

# ── Export Chat ──
st.subheader("📥 Export Your Chat")
if history:
    export_text = (
        f"Python Chatbot — Chat Export\n"
        f"User: {st.session_state.username}\n"
        f"Exported on: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
        f"{'='*40}\n\n"
    )
    for msg in history:
        role = "You" if msg["role"] == "user" else "Bot"
        export_text += f"{role}: {msg['content']}\n\n"

    st.download_button("📥 Download Chat as .txt", export_text,
        file_name=f"{st.session_state.username}_chat.txt",
        mime="text/plain", use_container_width=True)
else:
    st.info("No chat history to export yet!")