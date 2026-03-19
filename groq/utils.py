# utils.py

import re
from datetime import datetime


# ════════════════════════════
#   PYTHON TOPIC CHECK
# ════════════════════════════

PYTHON_KEYWORDS = [
    "python", "django", "flask", "fastapi", "pandas", "numpy",
    "matplotlib", "tensorflow", "pytorch", "scikit", "opencv",
    "pip", "virtualenv", "lambda", "decorator", "generator",
    "list", "dict", "tuple", "set", "class", "function", "def",
    "loop", "array", "string", "integer", "variable", "module",
    "import", "package", "library", "error", "exception", "debug",
    "streamlit", "jupyter", "notebook", "conda", "anaconda"
]

def is_python_related(text: str) -> bool:
    """Check if the question is Python related"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in PYTHON_KEYWORDS)


 

def clean_text_for_voice(text: str) -> str:
    """
    Remove markdown symbols before converting to voice
    so gTTS doesn't read '**' or '#' out loud
    """
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "Here is a code example.", text)

    # Remove inline code
    text = re.sub(r"`[^`]*`", "", text)

    # Remove bold / italic markers
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)

    # Remove headers (#, ##, ###)
    text = re.sub(r"#+\s*", "", text)

    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


 

def validate_password(password: str) -> tuple[bool, str]:
     
    if len(password) < 6:
        return False, "Password must be at least 6 characters!"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter!"

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number!"

    return True, "OK"


def validate_email(email: str) -> bool:
    """Basic email format check"""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username
    Returns (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters!"

    if len(username) > 20:
        return False, "Username must be less than 20 characters!"

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers and underscore!"

    return True, "OK"


# ════════════════════════════
#   TIMESTAMP HELPER
# ════════════════════════════

def get_timestamp() -> str:
    """Return current time as readable string"""
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


# ════════════════════════════
#   MESSAGE FORMATTER
# ════════════════════════════

def format_chat_export(messages: list, username: str) -> str:
    """
    Format chat history as plain text for export/download
    """
    lines = [
        f"Python Chatbot — Chat Export",
        f"User: {username}",
        f"Date: {get_timestamp()}",
        "=" * 40,
        ""
    ]

    for msg in messages:
        if msg["role"] == "system":
            continue
        role = "You" if msg["role"] == "user" else "Bot"
        lines.append(f"{role}: {msg['content']}")
        lines.append("")

    return "\n".join(lines)