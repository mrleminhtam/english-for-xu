import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- CẤU HÌNH TRANG & FIX LỖI SAFARI ---
st.set_page_config(page_title="English for Xu", page_icon="👧", layout="centered")

# Fix lỗi RegEx trên iPhone bằng cách tắt MathJax
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

# --- CẤU HÌNH API (BẢO MẬT) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm ơi, hãy dán API Key vào mục Secrets nhé!")
    st.stop()

# --- THIẾT LẬP AI ---
# Dùng tên model đầy đủ để tránh lỗi NotFound
MODEL_NAME = "models/gemini-1.5-flash-latest"

instruction = (
    "You are a sweet, fun English teacher for a little girl named Xu. "
    "Rules: 1. Use very simple English. 2. Be flexible: if she talks about toys, cartoons, or family, follow her. "
    "3. Keep responses short (1-2 sentences). 4. Correct her gently. "
    "5. Use friendly words like 'sweetie' or 'good job'."
)

model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=instruction)

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- GIAO DIỆN CHÍNH ---
st.title("👧 Hello Xu! Let's talk!")
st.write("Bé Xu nhấn nút micro rồi nói chuyện với thầy nhé!")

# Hiển thị lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ ĐẦU VÀO ---
st.write("---")
col1, col2 = st.columns([1, 3])

with col1:
    audio_text = speech_to_text(
        start_prompt="🎤 Nhấn để nói",
        stop_prompt="🛑 Dừng",
        language='en',
        key='speech_input'
    )

with col2:
    chat_text = st.chat_input("Hoặc nhắn tin...")

user_input = audio_text if audio_text else chat_text

if user_input:
    # 1. Lưu tin nhắn của bé
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Gọi AI (Dùng generate_content trực tiếp để tránh lỗi chat session)
    try:
        with st.spinner("Thầy đang nghe..."):
            response = model.generate_content(user_input)
            answer = response.text
        
        # 3. Hiển thị và phát âm thanh
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
