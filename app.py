import streamlit as st
from google import genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

# Fix lỗi hiển thị cho iPhone
st.markdown("<script>window.MathJax = { skipStartupTypeset: true };</script>", unsafe_allow_html=True)

# Giao diện màu hồng
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

# --- 2. KẾT NỐI API ---
if "GEMINI_API_KEY" in st.secrets:
    try:
        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"],
            http_options={'api_version': 'v1'}
        )
    except Exception as e:
        st.error(f"Lỗi cấu hình: {e}")
        st.stop()
else:
    st.error("Ba Tâm ơi, hãy dán API Key vào mục Secrets nhé!")
    st.stop()

# --- 3. THIẾT LẬP AI ---
MODEL_ID = "gemini-1.5-flash"

# Gộp hướng dẫn vào prompt để tránh lỗi Payload
SYSTEM_PROMPT = (
    "Context: You are a sweet English teacher for a girl named Xu. "
    "Rules: Short sentences, simple English, very friendly. "
    "Now, reply to this: "
)

# --- 4. GIAO DIỆN CHAT ---
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
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.spinner("Thầy đang nghe bé Xu..."):
            # CHIÊU CUỐI: Gửi kèm hướng dẫn trực tiếp trong nội dung
            full_prompt = f"{SYSTEM_PROMPT} {user_input}"
            
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=full_prompt
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
        st.error(f"Cố lên ba Tâm ơi! Lỗi này lạ quá: {str(e)}")
