import streamlit as st
from google import genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH TRANG & FIX LỖI IPHONE ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

# Fix lỗi RegEx trên Safari/Chrome iPhone
st.markdown("<script>window.MathJax = { skipStartupTypeset: true };</script>", unsafe_allow_html=True)

# Giao diện màu hồng bé gái
st.markdown("""
    <style>
    .stButton > button {
        background-color: #FFC0CB;
        color: #515151;
        border-radius: 20px;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KẾT NỐI API (ÉP PHIÊN BẢN V1) ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        # CHIÊU CUỐI: Ép API dùng bản v1 để tránh lỗi 404 của bản v1beta
        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"],
            http_options={'api_version': 'v1'}
        )
    except Exception as e:
        st.error(f"Lỗi cấu hình Client: {e}")
        st.stop()
else:
    st.error("Ba Tâm ơi, hãy dán API Key vào mục Secrets nhé!")
    st.stop()

# --- 3. THIẾT LẬP THẦY GIÁO AI ---
MODEL_ID = "gemini-1.5-flash"

instruction = (
    "You are a sweet, fun English teacher for a little girl named Xu. "
    "1. Speak very simple English. 2. Responses: 1-2 short sentences. "
    "3. Correct her gently. 4. Use words like 'sweetie' or 'good job'."
)

# --- 4. GIAO DIỆN CHAT ---
st.title("👧 Hello Xu! Let's talk!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. XỬ LÝ NÓI & NHẮN TIN ---
st.write("---")
col1, col2 = st.columns([1, 2])

with col1:
    audio_text = speech_to_text(
        start_prompt="🎤 Nhấn nói",
        stop_prompt="🛑 Dừng",
        language='en',
        key='speech_input'
    )

with col2:
    chat_text = st.chat_input("Hoặc gõ ở đây...")

user_input = audio_text if audio_text else chat_text

if user_input:
    # Lưu tin nhắn của bé
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.spinner("Thầy đang nghe bé Xu..."):
            # Gọi AI trực tiếp
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=user_input,
                config={'system_instruction': instruction}
            )
            answer = response.text
        
        # Trả lời và phát âm thanh
        with st.chat_message("assistant"):
            st.markdown(answer)
            
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)

        st.session_state.messages.append({"role": "assistant", "content": answer})
    
    except Exception as e:
        st.error(f"Thầy bận chút xíu, ba Tâm kiểm tra Key nhé: {str(e)}")
