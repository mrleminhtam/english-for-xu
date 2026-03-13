import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. KẾT NỐI API ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm chưa dán Key vào Secrets kìa!")
    st.stop()

# --- 2. THIẾT LẬP THẦY GIÁO (DÙNG 8B ĐỂ THÔNG LỖI 404) ---
model = genai.GenerativeModel("gemini-1.5-flash-8b")

st.title("👧 Hello Xu! Let's talk!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. XỬ LÝ NÓI ---
st.write("---")
audio_text = speech_to_text(start_prompt="🎤 Nhấn để nói với thầy", stop_prompt="🛑 Dừng", language='en')

if audio_text:
    st.session_state.messages.append({"role": "user", "content": audio_text})
    with st.chat_message("user"):
        st.markdown(audio_text)

    try:
        with st.spinner("Thầy đang nghe..."):
            response = model.generate_content(f"You are a teacher for Xu. Reply short: {audio_text}")
            answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Lỗi AI: {e}")
