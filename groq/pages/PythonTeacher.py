import streamlit as st
from groq import Groq
import gtts
from io import BytesIO
import tempfile
import os
from database import save_chat, get_chat_history, clear_chat_history

# ── Page config — SABSE PEHLE ──
st.set_page_config(page_title="Python Teacher", page_icon="🐍", layout="wide")

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
        st.session_state.messages  = []
        st.switch_page("app.py")

# ── Page Title ──
st.title("🧑‍🏫 Python Virtual Teacher")
st.caption(f"Logged in as: {st.session_state.username} — Ask any Python question!")
st.divider()


 
def text_to_audio(text: str) -> BytesIO:
    """Convert text to speech using gTTS"""
    tts = gtts.gTTS(text=text, lang="en", slow=False)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf


def get_llm_reply(messages: list) -> str:
    """Get response from Groq LLM"""
    response = client.chat.completions.create(
        model       = "llama-3.3-70b-versatile",
        messages    = messages,
        max_tokens  = 2048,
        temperature = 0.5
    )
    return response.choices[0].message.content


def handle_prompt(prompt: str):

    # Save and show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat(st.session_state.username, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Save and show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat(st.session_state.username, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and show bot reply
    with st.chat_message("assistant"):
        with st.spinner(" Generating..."):
            reply = get_llm_reply(st.session_state.messages)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            save_chat(st.session_state.username, "assistant", reply)

    # Play audio
    st.audio(text_to_audio(reply), format="audio/mp3", autoplay=True)


if "messages" not in st.session_state:
    history = get_chat_history(st.session_state.username)
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are an expert Python developer and teacher. Always answer in Python by default unless the user explicitly mentions another language. If the user asks to write code, write it in Python. Be clear, concise and beginner-friendly."
        }
    ] + history

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.divider()

# ════════════════════════════
#   INPUT BAR — Text + Mic
# ════════════════════════════
if "show_voice" not in st.session_state:
    st.session_state.show_voice = False

col_input, col_mic = st.columns([11, 1])

with col_input:
    prompt = st.chat_input("Ask a Python question...")

with col_mic:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎤", help="Click to use voice input", use_container_width=True):
        st.session_state.show_voice = not st.session_state.show_voice
        st.rerun()

# Handle text input
if prompt:
    handle_prompt(prompt)

# ════════════════════════════
#   VOICE RECORDER
# ════════════════════════════
if st.session_state.show_voice:
    st.info("🎤 Recording mode ON — speak your Python question below")
    audio_file = st.audio_input("🎙️ Tap to record your question")

    if audio_file is not None:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name

        # Transcribe using Whisper
        with st.spinner("🎧 Understanding your voice..."):
            with open(tmp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model    = "whisper-large-v3",
                    file     = f,
                    language = "en"
                )
            voice_prompt = transcription.text
            os.unlink(tmp_path)

        st.success(f"**You said:** {voice_prompt}")
        st.session_state.show_voice = False
        handle_prompt(voice_prompt)

# ════════════════════════════
#   CLEAR CHAT
# ════════════════════════════
st.divider()
if st.button("🗑️ Clear Chat"):
    clear_chat_history(st.session_state.username)
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()