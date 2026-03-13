import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

# --- KẾT NỐI API ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm ơi, hãy dán API Key vào mục Secrets nhé!")
    st.stop()

# --- THIẾT LẬP THẦY GIÁO (BẢN 8B ĐỂ TRÁNH LỖI 404) ---
# Đây là thay đổi quan trọng nhất để thông lỗi 404
MODEL_ID = "gemini-1.5-flash-8b"
model = genai.GenerativeModel(MODEL_ID)

st.title("👧 Hello Xu! Let's talk!")

# Hiển thị lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ NÓI & NHẮN TIN ---
st.write("---")
col1, col2 = st.columns([1, 2])
with col1:
    # Nút mic màu hồng cho bé Xu
    audio_text = speech_to_text(start_prompt="🎤 Nói", stop_prompt="🛑 Dừng", language='en', key='speech_input')
with col2:
    chat_text = st.chat_input("Nhắn cho thầy...")

user_input = audio_text if audio_text else chat_text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.spinner("Thầy đang nghe..."):
            # Gửi yêu cầu cho AI
            response = model.generate_content(f"You are a sweet teacher for a girl named Xu. Reply short in English: {user_input}")
            answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
            # Phát âm thanh cho bé nghe
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Lỗi AI: {str(e)}")
