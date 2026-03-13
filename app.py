import streamlit as st
from google import genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

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

# --- 2. CẤU HÌNH API MỚI ---
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm ơi, hãy dán API Key vào mục Secrets nhé!")
    st.stop()

# --- 3. THIẾT LẬP AI ---
MODEL_ID = "gemini-1.5-flash-002"

instruction = (
    "You are a sweet, fun English teacher for a little girl named Xu. "
    "1. Use very simple English. 2. Responses: 1-2 short sentences. "
    "3. Correct her gently. 4. Be very friendly."
)

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
        # Gọi AI theo cú pháp thư viện MỚI
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_input,
            config={'system_instruction': instruction}
        )
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
        st.error(f"Lỗi rồi ba Tâm ơi: {str(e)}")


