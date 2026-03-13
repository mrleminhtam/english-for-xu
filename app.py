import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# Cấu hình AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm dán Key vào Secrets nhé!")
    st.stop()

# Dùng model ổn định nhất
MODEL_ID = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_ID)

st.title("👧 Hello Xu! Let's talk!")

# Xử lý chat đơn giản
user_input = st.chat_input("Nói gì đó với thầy...")
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    response = model.generate_content(f"You are a teacher for Xu. Reply short: {user_input}")
    
    with st.chat_message("assistant"):
        st.write(response.text)
        tts = gTTS(text=response.text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)
