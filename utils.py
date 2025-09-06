import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{6,}\d")

def is_email(text: str) -> bool:
    return EMAIL_RE.fullmatch(text.strip()) is not None

def is_phone(text: str) -> bool:
    return PHONE_RE.fullmatch(text.strip()) is not None
