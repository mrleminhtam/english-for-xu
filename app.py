import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

# --- 2. KẾT NỐI API (DÙNG BẢN CŨ NHƯNG ỔN ĐỊNH) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm ơi, dán Key vào Secrets nhé!")
    st.stop()

# --- 3. THIẾT LẬP MODEL ---
# Dùng tên model rút gọn - Đây là chìa khóa để hết 404
MODEL_ID = "gemini-1.5-flash"

instruction = (
    "You are a sweet, fun English teacher for a little girl named Xu. "
    "Speak very simple English. Short sentences only. Be very encouraging."
)

model = genai.GenerativeModel(model_name=MODEL_ID, system_instruction=instruction)

# --- 4. GIAO DIỆN ---
st.title("👧 Hello Xu! Let's talk!")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. XỬ LÝ NÓI & NHẮN TIN ---
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
        with st.spinner("Thầy đang nghe bé Xu..."):
            # Gọi API theo cách truyền thống
            response = model.generate_content(user_input)
            answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")
        st.info("Ba Tâm ơi, thử lấy API Key từ một Gmail mới hoàn toàn xem sao!")
