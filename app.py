import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm dán Key vào Secrets nhé!")
    st.stop()

# --- 2. THIẾT LẬP THẦY GIÁO ---
# Thử dùng bản gemini-1.5-flash-8b (bản này cực nhẹ và ít lỗi 404 nhất)
MODEL_ID = "gemini-1.5-flash-8b" 

prompt_prefix = "You are a sweet English teacher for a girl named Xu. Speak simple English, short sentences. Answer this: "

# --- 3. GIAO DIỆN ---
st.title("👧 Hello Xu! Let's talk!")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. XỬ LÝ ---
st.write("---")
col1, col2 = st.columns([1, 2])
with col1:
    audio_text = speech_to_text(start_prompt="🎤 Nhấn nói", stop_prompt="🛑 Dừng", language='en', key='speech_input')
with col2:
    chat_text = st.chat_input("Hoặc gõ ở đây...")

user_input = audio_text if audio_text else chat_text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.spinner("Thầy đang nghe..."):
            # Cách gọi đơn giản nhất để không bị lỗi 404
            model = genai.GenerativeModel(MODEL_ID)
            response = model.generate_content(f"{prompt_prefix} {user_input}")
            answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Vẫn lỗi 404 à anh? Thử nút Reboot app nhé! Lỗi: {str(e)}")
