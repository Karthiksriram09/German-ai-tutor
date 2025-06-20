import streamlit as st
import language_tool_python
from transformers import pipeline
from gtts import gTTS
import speech_recognition as sr
import sqlite3
import datetime
import os
import tempfile

# ---------------------- Setup ----------------------
st.set_page_config(page_title="German AI Tutor", layout="centered")
st.title("🇩🇪 Conversational German Tutor")
st.markdown("Learn and improve your German with AI, grammar help, flashcards, and voice!")

# ---------------------- Init Tools ----------------------
tool = language_tool_python.LanguageTool('de-DE')

@st.cache_resource
def load_ai_model():
    return pipeline("text-generation", model="EleutherAI/gpt-neo-125M")

generator = load_ai_model()

# ---------------------- Voice Input ----------------------
st.subheader("🎤 Voice Input (Optional)")
if st.button("🎙️ Speak Now"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)

    try:
        user_input = r.recognize_google(audio, language="de-DE")
        st.success(f"🗣️ You said: {user_input}")
    except:
        user_input = ""
        st.error("Could not understand audio. Try again.")

else:
    user_input = st.text_area("✍️ Or type your German sentence here:", height=150)

# ---------------------- CEFR Level ----------------------
level = st.selectbox("Choose CEFR Level", ["A1", "A2", "B1", "B2"])

# ---------------------- Sentence Analysis ----------------------
if st.button("🔍 Analyze Sentence", key="analyze_button"):
    if user_input.strip():
        matches = tool.check(user_input)
        if not matches:
            st.success("✅ No grammatical errors found. Gut gemacht!")
        else:
            st.error(f"⚠️ {len(matches)} issue(s) found:")
            for i, match in enumerate(matches, 1):
                st.markdown(f"""
                **{i}.** *{match.message}*  
                ‣ **Issue:** `{user_input[match.offset:match.offset + match.errorLength]}`  
                ‣ **Suggestion:** `{', '.join(match.replacements) if match.replacements else 'No suggestions'}`  
                """)

        # AI Rewriting
        st.markdown("---")
        st.subheader("🤖 AI Rewriting Suggestion")
        prompt = f"Improve this German sentence politely:\n{user_input}\n\nImproved:"
        result = generator(prompt, max_length=60, do_sample=True, temperature=0.7)[0]['generated_text']
        improved = result.split("Improved:")[-1].strip()
        st.success(improved)

        # Text-to-Speech
        tts = gTTS(text=improved, lang="de")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            st.audio(fp.name, format="audio/mp3")

    else:
        st.warning("Please enter or speak a sentence.")

# ---------------------- Flashcards: SQLite Setup ----------------------
conn = sqlite3.connect("flashcards.db")
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS cards (
        word TEXT,
        meaning TEXT,
        next_review DATE,
        easiness REAL DEFAULT 2.5,
        interval INTEGER DEFAULT 1,
        repetition INTEGER DEFAULT 0
    )
''')
conn.commit()

# ---------------------- Add Vocabulary ----------------------
st.markdown("---")
st.subheader("📖 Save Vocabulary to Review")
with st.form("vocab_form"):
    word = st.text_input("German Word or Phrase")
    meaning = st.text_input("English Meaning")
    submitted = st.form_submit_button("💾 Save")

    if submitted and word.strip() and meaning.strip():
        next_review = datetime.date.today() + datetime.timedelta(days=1)
        c.execute("INSERT INTO cards (word, meaning, next_review) VALUES (?, ?, ?)",
                  (word.strip(), meaning.strip(), next_review))
        conn.commit()
        st.success("✅ Word saved!")

# ---------------------- Review Flashcards ----------------------
st.markdown("---")
st.subheader("📅 Review Due Flashcards")

today = datetime.date.today()
c.execute("SELECT rowid, word, meaning FROM cards WHERE next_review <= ?", (today,))
rows = c.fetchall()

if rows:
    for rowid, word, meaning in rows:
        st.markdown(f"**📝 {word}** — *{meaning}*")
        if st.button(f"I remembered: {word}", key=f"remember_{rowid}"):
            # Update SM-2 logic
            c.execute("SELECT repetition, interval, easiness FROM cards WHERE rowid=?", (rowid,))
            rep, interval, ease = c.fetchone()
            rep += 1
            interval = 1 if rep == 1 else round(interval * ease)
            ease = max(1.3, ease - 0.1)  # simple forgetting curve
            next_review = today + datetime.timedelta(days=interval)
            c.execute("""
                UPDATE cards SET repetition=?, interval=?, easiness=?, next_review=?
                WHERE rowid=?
            """, (rep, interval, ease, next_review, rowid))
            conn.commit()
            st.success(f"🎉 Scheduled next review in {interval} days.")
else:
    st.info("No flashcards due for today. You're all caught up!")
