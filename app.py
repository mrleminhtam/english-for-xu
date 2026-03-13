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

# Thiết lập thầy giáo
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("👧 Hello Xu! Let's talk!")

# Nhận diện giọng nói hoặc văn bản
col1, col2 = st.columns([1, 2])
with col1:
    audio_text = speech_to_text(start_prompt="🎤 Nói", stop_prompt="🛑 Dừng", language='en')
with col2:
    chat_text = st.chat_input("Nhắn cho thầy...")

user_input = audio_text if audio_text else chat_text

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    try:
        response = model.generate_content(f"You are a teacher for a girl named Xu. Reply very short: {user_input}")
        answer = response.text
        
        with st.chat_message("assistant"):
            st.write(answer)
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"Lỗi AI: {e}")
