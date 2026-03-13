import streamlit as st
import requests
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Ba Tâm dán Key vào Secrets nhé!")
    st.stop()

# URL gọi thẳng bản v1 chính thức
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

st.title("👧 Hello Xu! Let's talk!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. XỬ LÝ ---
st.write("---")
audio_text = speech_to_text(start_prompt="🎤 Nhấn nói", stop_prompt="🛑 Dừng", language='en')

if audio_text:
    st.session_state.messages.append({"role": "user", "content": audio_text})
    with st.chat_message("user"):
        st.markdown(audio_text)

    try:
        with st.spinner("Thầy đang nghe..."):
            # Gói tin gửi đi siêu tối giản
            payload = {
                "contents": [{"parts": [{"text": f"You are a teacher for Xu. Reply short: {audio_text}"}]}]
            }
            response = requests.post(API_URL, json=payload)
            result = response.json()
            
            # Lấy câu trả lời
            answer = result['candidates'][0]['content']['parts'][0]['text']
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Vẫn lỗi à ba Tâm? Check lại Key nhé: {str(e)}")
