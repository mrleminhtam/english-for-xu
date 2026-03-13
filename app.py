import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io
import os

# --- 1. KẾT NỐI API (ÉP DÙNG BẢN CHÍNH THỨC V1) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    # Ép thư viện dùng bản v1 thay vì v1beta để tránh lỗi 404
    os.environ["GOOGLE_API_VERSION"] = "v1" 
    genai.configure(api_key=api_key)
else:
    st.error("Ba Tâm chưa dán Key vào Secrets kìa!")
    st.stop()

# --- 2. THIẾT LẬP THẦY GIÁO ---
# Dùng tên model chuẩn nhất
MODEL_ID = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_ID)

st.title("👧 Hello Xu! Let's talk!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. XỬ LÝ NÓI ---
st.write("---")
audio_text = speech_to_text(
    start_prompt="🎤 Nhấn để nói với thầy", 
    stop_prompt="🛑 Dừng", 
    language='en'
)

if audio_text:
    st.session_state.messages.append({"role": "user", "content": audio_text})
    with st.chat_message("user"):
        st.markdown(audio_text)

    try:
        with st.spinner("Thầy đang nghe..."):
            # Gửi tin nhắn kèm hướng dẫn nhân vật
            response = model.generate_content(
                f"You are a teacher for a girl named Xu. Reply very short: {audio_text}"
            )
            answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Vẫn lỗi 404 à ba Tâm? Lỗi: {str(e)}")
