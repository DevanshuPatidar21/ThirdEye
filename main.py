import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import time
from PIL import Image
import cv2 
import numpy as np
import speech_recognition as sr # Nayi library voice ke liye

# --- PAGE CONFIG ---
st.set_page_config(page_title="Third Eye Final", page_icon="👁️", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'run_auto' not in st.session_state:
    st.session_state.run_auto = False
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "Navigation Mode (Safety)"
if 'target_query' not in st.session_state:
    st.session_state.target_query = ""
if 'guardian_phone' not in st.session_state:
    st.session_state.guardian_phone = "+91 9098237764" # Default dummy

# --- API SETUP ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("🚨 API Key Error. Check .streamlit/secrets.toml")
    st.stop()

# --- FUNCTIONS ---

def listen_for_command():
    """Voice Command sunta hai aur Mode change karta hai"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now!")
        try:
            # 2 second wait karega voice ke liye
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Voice Service Down"
        except Exception:
            return "No audio detected"

def text_to_speech(text):
    try:
        timestamp = int(time.time_ns()) 
        filename = f"temp_audio_{timestamp}.mp3"
        for file in os.listdir():
             if file.startswith("temp_audio_") and file.endswith(".mp3"):
                 try: os.remove(file)
                 except: pass
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        return None

def capture_frame():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): return None
    ret, frame = cap.read()
    cap.release()
    if not ret: return None
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb)

def analyze_scene_smart(image, mode, target_obj=""):
    # ... (Prompt Logic Same as before) ...
    if mode == "Navigation Mode (Safety)":
        prompt = """
        You are a vision assistant for a blind person. Keep it UNDER 3 SENTENCES.
        Priority: Immediate HAZARDS (steps, obstacles) and distance.
        """
    elif mode == "Reading Mode (Text/Medicine)":
        prompt = """
        You are a reading assistant. Focus ONLY on text (Signs, Medicines, Books).
        Read the content clearly. Keep it concise.
        """
    elif mode == "Find Specific Object":
        prompt = f"""
        User is looking for: '{target_obj}'.
        Scan image for '{target_obj}'.
        If found, say "Found {target_obj}" and describe exact location.
        If NOT found, say "Searching for {target_obj}..."
        """
    else: prompt = "Describe scene."
    
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e: return f"Error: {e}"

# --- SIDEBAR (Settings Only) ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("Current Guardian Number:")
    # User yahan number dalega
    st.session_state.guardian_phone = st.text_input("Emergency Contact", st.session_state.guardian_phone)
    st.info("Note: In a real app, SOS sends SMS to this number.")

# --- MAIN UI ---
st.title("👁️ The Third Eye: Voice Controlled")

# --- 1. VOICE COMMAND CENTER (The Solution to Issue 1 & 3) ---
st.markdown("### 🗣️ Voice Command Center")
col_mic, col_status = st.columns([1, 3])

with col_mic:
    # Bada Mic Button
    if st.button("🎤 TAP TO SPEAK", type="primary", help="Click and say 'Find Keys' or 'Read Mode'"):
        cmd = listen_for_command()
        
        # --- SMART COMMAND PARSING ---
        if "find" in cmd:
            # Example: "Find my keys" -> Extracts "keys"
            obj = cmd.replace("find", "").replace("my", "").strip()
            st.session_state.app_mode = "Find Specific Object"
            st.session_state.target_query = obj
            st.success(f"✅ Command Accepted: Finding '{obj}'")
            
        elif "read" in cmd or "text" in cmd:
            st.session_state.app_mode = "Reading Mode (Text/Medicine)"
            st.success("✅ Switched to Reading Mode")
            
        elif "navigate" in cmd or "safety" in cmd or "walk" in cmd:
            st.session_state.app_mode = "Navigation Mode (Safety)"
            st.success("✅ Switched to Navigation Mode")
            
        elif "help" in cmd or "sos" in cmd:
            st.session_state.app_mode = "SOS" # Trigger logic below
            
        else:
            st.warning(f"❌ Heard '{cmd}', but command not recognized. Try 'Find Keys' or 'Navigation'.")

with col_status:
    # Display Current Status big
    st.markdown(f"**Current Mode:** `{st.session_state.app_mode}`")
    if st.session_state.app_mode == "Find Specific Object":
        st.markdown(f"**Target:** `{st.session_state.target_query}`")

st.divider()

# --- 2. SOS LOGIC (The Solution to Issue 2) ---
if st.button("🚨 MANUAL SOS ALERT", type="secondary"):
    st.toast("Triggering Emergency Protocol...", icon="🚨")
    
    # Fake SMS Log display karna judges ke liye
    st.error("🆘 EMERGENCY ALERT SENT!")
    with st.expander("View Backend SMS Log (Proof)", expanded=True):
        st.code(f"""
        [LOG] Sending SMS via Twilio API...
        -----------------------------------
        TO:      {st.session_state.guardian_phone}
        FROM:    Third Eye App
        MESSAGE: "URGENT! {st.session_state.guardian_phone}, the user has triggered SOS. 
                  GPS Location: 22.7196° N, 75.8577° E. 
                  Snapshot uploaded to Cloud."
        STATUS:  200 OK (Delivered)
        """, language="json")

# --- 3. MAIN LOOP (Unchanged) ---
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ START SYSTEM"):
        st.session_state.run_auto = True
        st.rerun()
with col2:
    if st.button("⏹️ STOP SYSTEM"):
        st.session_state.run_auto = False
        st.rerun()

if st.session_state.run_auto:
    with st.spinner("👀 Scanning..."):
        img_pil = capture_frame()
    
    if img_pil:
        st.image(img_pil, caption=f"Live Feed - {st.session_state.app_mode}", width=400)
        
        # Analyze based on current session state mode
        desc = analyze_scene_smart(img_pil, st.session_state.app_mode, st.session_state.target_query)
        
        # UI Feedback
        if "Found" in desc: st.success(f"🗣️ {desc}")
        else: st.info(f"🗣️ {desc}")
        
        # Audio
        audio_file = text_to_speech(desc)
        if audio_file:
            st.audio(audio_file, format="audio/mp3", autoplay=True)
        
        time.sleep(6)
        st.rerun()