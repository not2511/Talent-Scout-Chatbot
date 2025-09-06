# TalentScout — Intelligent Hiring Assistant

## Overview
TalentScout is an AI-powered hiring assistant chatbot that collects candidate details and generates tailored technical questions based on their declared tech stack.  
It simulates the initial screening process for recruiters in a professional, structured, and polite manner.

## Features
- Collects essential candidate details step by step:
  - Full Name  
  - Email Address  
  - Phone Number  
  - Years of Experience  
  - Desired Position(s)  
  - Current Location  
  - Tech Stack  
- Automatically generates 3–5 technical questions based on the tech stack (Gemini API).  
- Asks one question at a time and saves user answers.  
- Quit and Restart buttons:
  - Quit ends the session with a farewell message and saves data automatically.  
  - Restart clears the session and starts fresh (previous session saved automatically).  
- All session data (details, chat, questions, answers) is saved as JSON in the `data/` folder for recruiters to review.

## Tech Stack
- [Streamlit](https://streamlit.io/) — for the user interface.  
- [Google Gemini API](https://ai.google.dev/) — for LLM-based text generation.  
- [uv](https://github.com/astral-sh/uv) — dependency management & virtual environment.  
- Python 3.10+  

## Project Structure
```
talent_scout/
│
├── app.py           # Main Streamlit chatbot app
├── prompts.py       # System and question prompts
├── utils.py         # Validators and helpers
├── data/            # Auto-saved session logs (JSON)
├── .env             # Environment variables (contains GEMINI_API_KEY)
├── pyproject.toml   # Project dependencies (uv)
└── README.md        # Project documentation
```

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/not2511/Projects
cd talent_scout
```

### 2. Setup environment with uv
```bash
uv sync
```

### 3. Configure API Key
Create a `.env` file in the project root with your Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the app
```bash
uv run streamlit run app.py
```

## Usage Flow
1. The assistant greets the candidate and starts collecting details.  
2. After the tech stack is provided, it generates 3–5 technical questions.  
3. The candidate answers each question one at a time.  
4. Recruiters can press **Quit** or **Restart** at any time:  
   - Data is automatically saved to `data/`.  
   - A farewell or restart message is shown.  
5. Recruiters can later review JSON logs for candidate responses.

## Prompt Design
- **System Persona:** The assistant acts as a polite, professional recruiter.  
- **Question Prompt:** Generates concise, relevant, interview-ready questions based on tech stack.  
- **Fallback Prompt:** Handles invalid/unclear inputs politely and asks for clarification.  

## Challenges & Solutions
- **Delayed chat display:** Fixed by rendering user + assistant messages immediately with `st.chat_message`.  
- **Validation loops:** Relaxed validators for name/phone/email to handle more natural inputs.  
- **Session saving:** Implemented auto-save JSON for every Quit/Restart action.

## Future Enhancements
- Multilingual support.  
- Sentiment analysis of candidate answers.  
- Deploy on Streamlit Cloud or Hugging Face Spaces.  
- Recruiter dashboard for reviewing candidate logs.

---
