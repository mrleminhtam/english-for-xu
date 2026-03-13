import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io

# --- CẤU HÌNH TRANG & GIAO DIỆN ---
st.set_page_config(page_title="English for Xu", page_icon="👧", layout="centered")

# CSS để làm nút bấm màu hồng và giao diện thân thiện cho bé Xu
st.markdown("""
    <style>
    .stButton > button {
        background-color: #FFC0CB;
        color: #5D5D5D;
        border-radius: 20px;
        border: 2px solid #FFB6C1;
        font-weight: bold;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CẤU HÌNH API (BẢO MẬT) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Ba Tâm ơi, hãy vào Settings > Secrets để dán GEMINI_API_KEY nhé!")
    st.stop()

# --- KHỞI TẠO AI & BỘ NHỚ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Thiết lập nhân vật AI giáo viên linh hoạt
instruction = (
    "You are a sweet, fun English teacher for a little girl named Xu. "
    "Guidelines: 1. Use very simple, easy English. 2. Be flexible with topics: "
    "If she mentions dolls, cartoons, drawing, or family, follow her lead. "
    "3. Keep responses short (max 2 sentences). 4. Correct her gently. "
    "5. Use friendly words like 'sweetie', 'dear', or 'great job'."
)
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction)

# --- GIAO DIỆN CHÍNH ---
st.title("👧 Hello Xu! Let's talk!")
st.write("Bé Xu nhấn nút micro màu hồng rồi nói chuyện với thầy nhé!")

# Hiển thị lịch sử trò chuyện
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ ĐẦU VÀO ---
st.write("---")
col1, col2 = st.columns([1, 3])

with col1:
    # Nút nhấn để nói - Ưu tiên nhận diện tiếng Anh
    audio_text = speech_to_text(
        start_prompt="🎤 Nhấn để nói",
        stop_prompt="🛑 Dừng",
        language='en',
        key='speech_input'
    )

with col2:
    chat_text = st.chat_input("Hoặc nhắn tin tại đây...")

# Lấy thông tin từ bé (Ưu tiên giọng nói)
user_input = audio_text if audio_text else chat_text

if user_input:
    # 1. Lưu và hiển thị câu nói của bé
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. AI phản hồi dựa trên toàn bộ lịch sử trò chuyện (để linh hoạt chủ đề)
    with st.spinner("Thầy đang nghe bé Xu..."):
        chat = model.start_chat(history=[
            {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ])
        response = chat.send_message(user_input)
        answer = response.text
    
    # 3. Trả lời bằng chữ và tự động phát âm thanh
    with st.chat_message("assistant"):
        st.markdown(answer)
        
        # Chuyển văn bản thành giọng nói (TTS)
        try:
            tts = gTTS(text=answer, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
        except Exception:
            st.warning("Loa của thầy gặp chút trục trặc, bé đọc chữ giúp thầy nhé!")

    # Lưu phản hồi của AI vào lịch sử
    st.session_state.messages.append({"role": "assistant", "content": answer})