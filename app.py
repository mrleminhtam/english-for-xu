import streamlit as st
from google import genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- 1. CẤU HÌNH TRANG & FIX LỖI IPHONE ---
st.set_page_config(page_title="English for Xu", page_icon="👧")

# Fix lỗi hiển thị cho Safari/Chrome trên iPhone
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

# --- 2. KẾT NỐI API ---
# Quan trọng: Key trong Secrets phải đặt tên là GEMINI_API_KEY
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm ơi, hãy kiểm tra lại GEMINI_API_KEY trong mục Secrets nhé!")
    st.stop()

# --- 3. THIẾT LẬP THẦY GIÁO AI ---
# Dùng tên model chuẩn nhất của thư viện mới
MODEL_ID = "gemini-1.5-flash"

instruction = (
    "You are a sweet, fun English teacher for a little girl named Xu. "
    "1. Speak very simple English. 2. Topics: toys, family, animals. "
    "3. Responses: 1-2 short sentences. 4. Be very encouraging."
)

# --- 4. GIAO DIỆN CHAT ---
st.title("👧 Hello Xu! Let's talk!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử trò chuyện
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
            # Gọi AI theo cú pháp Chat Session mới nhất
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=user_input,
                config={'system_instruction': instruction}
            )
            answer = response.text
        
        # Trả lời và phát âm thanh
        with st.chat_message("assistant"):
            st.markdown(answer)
            
            # Chuyển text sang tiếng Anh chuẩn
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)

        st.session_state.messages.append({"role": "assistant", "content": answer})
    
    except Exception as e:
        # Hiển thị lỗi thân thiện để ba Tâm biết đường sửa
        st.error(f"Lỗi rồi ba Tâm ơi: {str(e)}")
        st.info("Mẹo: Thử lấy API Key mới từ một Gmail khác nếu vẫn lỗi 404/429 nhé.")
