import streamlit as st
from google import genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

# --- 2. KẾT NỐI API ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"],
            http_options={'api_version': 'v1beta'}
        )
    except Exception as e:
        st.error(f"Lỗi: {e}")
        st.stop()
else:
    st.error("Ba Tâm ơi, dán Key vào Secrets nhé!")
    st.stop()

# --- 3. THIẾT LẬP AI ---
# Dùng 1.0 Pro để trị dứt điểm lỗi 404
MODEL_ID = "gemini-1.0-pro"

SYSTEM_PROMPT = "You are a sweet English teacher for a girl named Xu. Short sentences, simple English. Reply to: "

# --- 4. GIAO DIỆN ---
st.title("👧 Hello Xu! Let's talk!")
if "messages" not in st.session_state: st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

# --- 5. XỬ LÝ ---
st.write("---")
col1, col2 = st.columns([1, 2])
with col1:
    audio_text = speech_to_text(start_prompt="🎤 Nhấn nói", stop_prompt="🛑 Dừng", language='en', key='speech_input')
with col2:
    chat_text = st.chat_input("Hoặc gõ ở đây...")

user_input = audio_text if audio_text else chat_text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    try:
        with st.spinner("Thầy đang nghe..."):
            # Gọi trực tiếp không qua chat session cho nhẹ
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"{SYSTEM_PROMPT} {user_input}"
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
        st.error(f"Ba Tâm thử đổi model xem sao: {str(e)}")
