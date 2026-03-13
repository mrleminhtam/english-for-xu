import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH TRANG & FIX LỖI IPHONE ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

# Fix lỗi RegEx trên Safari/Chrome iPhone
st.markdown("<script>window.MathJax = { skipStartupTypeset: true };</script>", unsafe_allow_html=True)

# Giao diện màu hồng cho bé Xu
st.markdown("""
    <style>
    .stButton > button {
        background-color: #FFC0CB;
        color: #5D5D5D;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CẤU HÌNH API (BẢO MẬT) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm ơi, hãy dán API Key mới vào mục Secrets nhé!")
    st.stop()

# --- 3. THIẾT LẬP AI ---
# Dùng tên model ngắn gọn nhất để tránh lỗi 404
MODEL_NAME = "gemini-1.5-flash"

instruction = (
    "You are a sweet, fun English teacher for a little girl named Xu. "
    "1. Use very simple English. 2. Topics: anything Xu likes. "
    "3. Responses: 1-2 short sentences. 4. Correct her gently."
)

model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=instruction)

# --- 4. GIAO DIỆN CHÍNH ---
st.title("👧 Hello Xu! Let's talk!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. XỬ LÝ ĐẦU VÀO ---
st.write("---")
col1, col2 = st.columns([1, 3])

with col1:
    audio_text = speech_to_text(
        start_prompt="🎤 Nhấn nói",
        stop_prompt="🛑 Dừng",
        language='en',
        key='speech_input'
    )

with col2:
    chat_text = st.chat_input("Hoặc gõ vào đây...")

user_input = audio_text if audio_text else chat_text

if user_input:
    # Lưu tin nhắn của bé
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # Gọi AI (Dùng phương thức trực tiếp nhất)
        response = model.generate_content(user_input)
        answer = response.text
        
        # Hiển thị và phát âm thanh
        with st.chat_message("assistant"):
            st.markdown(answer)
            
            # Chuyển văn bản thành giọng nói
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)

        st.session_state.messages.append({"role": "assistant", "content": answer})
    
    except Exception as e:
        # Nếu vẫn lỗi 404, hiển thị thông báo hướng dẫn ba Tâm
        st.error(f"Thầy đang bận một chút, ba Tâm kiểm tra lại API Key nhé!")
        st.info("Lưu ý: Anh cần dùng API Key từ 'New Project' trong AI Studio.")
