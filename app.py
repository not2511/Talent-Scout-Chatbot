# app.py
import streamlit as st
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import google.generativeai as genai
from prompts import PROMPT_TECH_Q, SYSTEM_PERSONA

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ----- Configuration -----
REQUIRED_KEYS = [
    "full_name",
    "email",
    "phone",
    "experience_years",
    "desired_positions",
    "location",
    "tech_stack",
]

FIELD_PROMPTS = {
    "full_name": "Welcome to TalentScout. Please provide your full name (first and last).",
    "email": "What is your email address? (e.g., alex@company.com)",
    "phone": "Please share your phone number (include country code if possible).",
    "experience_years": "How many years of professional experience do you have? (a number is fine)",
    "desired_positions": "Which role(s) are you applying for? (comma-separated if multiple)",
    "location": "What is your current location (City, Country)?",
    "tech_stack": "Please list your tech stack (languages, frameworks, databases, tools), comma-separated.",
}

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[\d\-\s()]{7,}$")


# ----- Validators -----
def validate_full_name(text: str):
    parts = text.strip().split()
    if len(parts) >= 2:
        return True, " ".join(parts[:2]), ""
    return False, None, "Please provide your full name (first and last)."


def validate_email(text: str):
    t = text.strip()
    return (True, t, "") if EMAIL_RE.match(t) else (False, None, "Please provide a valid email.")


def validate_phone(text: str):
    t = text.strip()
    if PHONE_RE.match(t):
        digits = re.sub(r"\D", "", t)
        return True, digits, ""
    return False, None, "Please provide a valid phone number."


def validate_experience(text: str):
    t = text.strip()
    if t.isdigit():
        return True, int(t), ""
    m = re.search(r"(\d+)", t)
    return (True, int(m.group(1)), "") if m else (False, None, "Please enter a number.")


def validate_desired_positions(text: str):
    parts = [p.strip() for p in re.split(r",|/|;| and ", text) if p.strip()]
    return (True, parts, "") if parts else (False, None, "Please list at least one position.")


def validate_location(text: str):
    return (True, text.strip(), "") if len(text.strip()) >= 2 else (False, None, "Please provide City, Country.")


def validate_tech_stack(text: str):
    parts = [p.strip() for p in re.split(r",|\||/|;", text) if p.strip()]
    return (True, parts, "") if parts else (False, None, "Please list at least one technology.")


VALIDATORS = {
    "full_name": validate_full_name,
    "email": validate_email,
    "phone": validate_phone,
    "experience_years": validate_experience,
    "desired_positions": validate_desired_positions,
    "location": validate_location,
    "tech_stack": validate_tech_stack,
}


# ----- Helpers -----
def next_missing_field(data: dict):
    for k in REQUIRED_KEYS:
        if data.get(k) is None:
            return k
    return None


def mask_preview(data: dict):
    d = dict(data)
    if d.get("email"):
        try:
            local, dom = d["email"].split("@", 1)
            d["email"] = local[0] + "***@" + dom
        except Exception:
            d["email"] = "***"
    if d.get("phone"):
        digits = re.sub(r"\D", "", str(d["phone"]))
        d["phone"] = "***" + digits[-4:] if len(digits) >= 4 else "***"
    return d


def save_session(farewell=False):
    os.makedirs("data", exist_ok=True)
    filename = f"data/session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    payload = {
        "created_at": st.session_state.created_at,
        "data": st.session_state.data,
        "messages": st.session_state.messages,
        "questions": st.session_state.questions,
        "answers": st.session_state.answers,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if farewell:
        st.success(f"Session saved to {filename}")


# ----- Init session -----
if "initialized" not in st.session_state:
    st.session_state.messages = []
    st.session_state.data = {k: None for k in REQUIRED_KEYS}
    st.session_state.current_field = REQUIRED_KEYS[0]
    st.session_state.questions = []
    st.session_state.current_q_index = 0
    st.session_state.answers = {}
    st.session_state.completed = False
    st.session_state.messages.append(("assistant", FIELD_PROMPTS[st.session_state.current_field]))
    st.session_state.initialized = True
    st.session_state.created_at = datetime.utcnow().isoformat()


# ----- UI -----
st.set_page_config(page_title="TalentScout — Hiring Assistant", layout="wide")
st.markdown("## TalentScout — Hiring Assistant")

# Layout: chat on left, controls on right
chat_col, ctrl_col = st.columns([3, 1], gap="large")

with chat_col:
    st.markdown("### Conversation")

    # Create a scrollable container for chat
    chat_container = st.container()

    with chat_container:
        for role, content in st.session_state.messages:
            with st.chat_message(role):
                st.markdown(content)

# Inject CSS to fix alignment
st.markdown("""
    <style>
    /* Make chat messages start from the top */
    section.main > div {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    /* Prevent early scrollbar until needed */
    .stChatMessageContainer {
        max-height: none !important;
    }
    </style>
""", unsafe_allow_html=True)


with ctrl_col:
    st.markdown("### Controls")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        quit_pressed = st.button("Quit", type="primary")
    with btn_col2:
        restart_pressed = st.button("Restart")

    if quit_pressed:
        save_session(farewell=True)
        st.session_state.messages.append(("assistant", "Thank you for your time. Goodbye!"))
        st.session_state.completed = True
        st.stop()

    if restart_pressed:
        save_session()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.caption("After pressing Quit or Restart all the session details will be saved for the recruiters.")

    st.markdown("### Data preview")
    st.json(mask_preview(st.session_state.data))




# ----- Chat input -----
user_input = st.chat_input("Type here...")
if user_input and not st.session_state.completed:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append(("user", user_input))

    # If we are asking questions
    if st.session_state.questions and st.session_state.current_q_index < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.current_q_index]
        st.session_state.answers[q] = user_input
        st.session_state.current_q_index += 1
        if st.session_state.current_q_index < len(st.session_state.questions):
            next_q = st.session_state.questions[st.session_state.current_q_index]
            reply = f"Thanks. Next question:\n{next_q}"
        else:
            reply = "Thank you. That's all the questions I had for now."
            st.session_state.completed = True
            save_session()
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append(("assistant", reply))

    else:
        # Collecting candidate info
        current = st.session_state.current_field
        if current:
            validator = VALIDATORS[current]
            ok, value, err = validator(user_input)
            if ok:
                st.session_state.data[current] = value
                nxt = next_missing_field(st.session_state.data)
                st.session_state.current_field = nxt
                if nxt:
                    reply = f"Saved. {FIELD_PROMPTS[nxt]}"
                else:
                    # Generate questions automatically
                    profile = st.session_state.data
                    prompt = PROMPT_TECH_Q.format(
                        full_name=profile["full_name"],
                        experience_years=profile["experience_years"],
                        desired_positions=", ".join(profile["desired_positions"]),
                        tech_stack=", ".join(profile["tech_stack"]),
                    )
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(f"{SYSTEM_PERSONA}\n\n{prompt}")
                    questions = [q.strip() for q in response.text.splitlines() if q.strip()]
                    st.session_state.questions = questions[:5]
                    st.session_state.current_q_index = 0
                    first_q = st.session_state.questions[0] if st.session_state.questions else "No questions generated."
                    reply = f"All details collected. Let's move to technical questions:\n{first_q}"
            else:
                reply = f"{err}\n{FIELD_PROMPTS[current]}"

            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append(("assistant", reply))