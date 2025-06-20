# 🇩🇪 German AI Tutor

An AI-powered German learning assistant built with Python and Streamlit. It corrects grammar, rewrites your sentences politely using AI, speaks them aloud, and helps you memorize vocabulary using spaced repetition flashcards.

## 🚀 Features

- ✅ Grammar correction using LanguageTool
- 🤖 Sentence rewriting with GPT-Neo (EleutherAI)
- 🎙️ Voice input using SpeechRecognition
- 🔈 Voice output using gTTS
- 📖 Vocabulary flashcards with Spaced Repetition (SM-2)
- 💻 Built with Streamlit, SQLite, and Hugging Face Transformers

## 🖼️ Screenshots

_(Add images here later)_

## 🧪 How It Works

| Feature | Description |
|--------|-------------|
| Grammar | Detects grammar errors using LanguageTool (`de-DE`) |
| AI Rewrite | Rewrites sentence politely using GPT-Neo |
| TTS | Speaks AI version aloud in native pronunciation |
| Voice Input | Lets users speak instead of typing |
| Flashcards | Tracks learned words using a memory curve |

## 🛠️ Getting Started

```bash
git clone https://github.com/Karthiksriram09/german-ai-tutor.git
cd german-ai-tutor
python -m venv venv
venv\Scripts\activate     # or source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
streamlit run app.py
