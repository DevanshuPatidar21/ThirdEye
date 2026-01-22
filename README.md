# 👁️ The Third Eye: AI Assistant for Visually Impaired

This project uses **Gemini 1.5 Flash** and **Voice Commands** to help blind people navigate, read text, and find objects.

## 🚀 Features
- **Navigation Mode:** Detects obstacles and hazards.
- **Reading Mode:** Reads medicines and books using OCR.
- **Find Object:** Voice-activated search for lost items (e.g., "Find my Keys").
- **SOS Alert:** Sends emergency logs to guardians.

## 🛠️ Tech Stack
- Python
- Streamlit
- Google Gemini API
- OpenCV
- SpeechRecognition

## ⚙️ How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Add API Key in `.streamlit/secrets.toml`
3. Run app: `streamlit run main.py`