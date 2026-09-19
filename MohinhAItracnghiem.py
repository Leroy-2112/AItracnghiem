import streamlit as st
import google.generativeai as genai
import json

# --- CẤU HÌNH GIAO DIỆN MÀN HÌNH ---
st.set_page_config(page_title="AI Tạo Trắc Nghiệm Cấp 3", page_icon="📝", layout="centered")
st.title("📝 AI Tạo Câu Hỏi Trắc Nghiệm")
st.subheader("Giải cứu học sinh cấp 3 trước giờ kiểm tra 💡✨")

# --- BẢO MẬT API KEY (ĐƠN GIẢN HÓA CỰC HẠN) ---
# Điền chính xác API Key bắt đầu bằng "AQ." của cậu vào đây
API_KEY = "AQ.Ab8RN6IRJfzhAuJ4XaMr8mmF4bFQzEghTos38suI0mOqY_DnTQ"

# Khối lệnh tự động đồng bộ khi đem lên mạng Streamlit Cloud
if API_KEY == "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY" or not API_KEY:
    try:
        if "API_KEY" in st.secrets:
            API_KEY = st.secrets["API_KEY"]
    except Exception:
        pass

# Kiểm tra điều kiện ngắt ứng dụng nếu thiếu Key
if not API_KEY or API_KEY == "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY":
    st.warning("⚠️ Vui lòng cấu hình Gemini API Key vào dòng số 11 để ứng dụng hoạt động nhé!")
    st.stop()
else:
    # Sử dụng SDK chính thức của Google, triệt tiêu hoàn toàn lỗi dính chữ URL
    genai.configure(api_key=API_KEY.strip())

# --- GIAO DIỆN NHẬP LIỆU ---
lecture_content = st.text_area("⬇️ Dán nội dung bài giảng hoặc ghi chú vào đây:", height=200, 
                               placeholder="Ví dụ: Rễ cây hấp thụ nước và ion khoáng từ đất qua các tế bào lông hút...")

col1, col2 = st.columns(2)
with col1:
    num_questions = st.slider("Số lượng câu hỏi cần tạo:", min_value=1, max_value=10, value=3)
with col2:
    difficulty = st.selectbox("Mức độ khó:", ["Nhận biết (Dễ)", "Thông hiểu (Vừa)", "Vận dụng (Khó)"])

# --- XỬ LÝ KHI BẤM NÚT TẠO CÂU HỎI ---
if st.button("🚀 Bắt đầu tạo câu hỏi bằng AI"):
    if not lecture_content.strip():
        st.error("❌ Bạn chưa nhập nội dung bài giảng kìa!")
    else:
        with st.spinner("AI đang đọc bài giảng và tạo câu hỏi siêu tốc..."):
            try:
                prompt = f"""
                Dựa trên nội dung bài giảng sau đây: "{lecture_content}"
                Hãy tạo ra đúng {num_questions} câu hỏi trắc nghiệm ở mức độ "{difficulty}".
                Mỗi câu hỏi bắt buộc phải có 4 lựa chọn (A, B, C, D) và chỉ có 1 đáp án đúng duy nhất.
                
                Trả về cấu trúc dạng mảng JSON như sau:
                [
                  {{
                    "question": "Câu hỏi?",
                    "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
                    "answer": "Điền chính xác văn bản của đáp án đúng giống hệt trong mảng options",
                    "explanation": "Giải thích ngắn gọn tại sao đúng"
                  }}
                ]
                """
                
                
                model = genai.GenerativeModel("gemini-3.6-flash")
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                # Ép kiểu văn bản thuần sang cấu trúc dữ liệu JSON để hiển thị bài thi
                quiz_data = json.loads(response.text)
                
                st.session_state.quiz_data = quiz_data
                st.session_state.user_answers = {}
                st.success("🎉 Đã tạo xong câu hỏi! Làm bài ngay bên dưới 👇")
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi tạo câu hỏi: {e}")

# --- HIỂN THỊ ĐỀ THI VÀ CHẤM ĐIỂM ---
if "quiz_data" in st.session_state:
    st.write("---")
    st.header("✍️ ĐỀ KIỂM TRA TRẢI NGHIỆM")
    
    for idx, q in enumerate(st.session_state.quiz_data):
        st.write(f"**Câu {idx+1}: {q['question']}**")
        user_choice = st.radio(
            f"Chọn đáp án cho câu {idx+1}:", 
            options=q['options'], 
            key=f"q_{idx}",
            index=None,
            label_visibility="collapsed"
        )
        st.session_state.user_answers[idx] = user_choice
        st.write("")

    if st.button("💯 Nộp bài xem điểm"):
        score = 0
        total = len(st.session_state.quiz_data)
        
        st.write("---")
        st.header("📊 KẾT QUẢ CỦA BẠN")
        
        for idx, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.user_answers.get(idx)
            correct_ans = q['answer']
            
            if user_ans == correct_ans:
                score += 1
                st.success(f"✅ **Câu {idx+1}: Chính xác!**")
            else:
                st.error(f"❌ **Câu {idx+1}: Sai rồi!** (Bạn chọn: {user_ans if user_ans else 'Chưa chọn'})")
                st.info(f"💡 *Đáp án đúng là:* {correct_ans}")
            
            st.caption(f"ℹ️ *Giải thích:* {q['explanation']}")
            st.write("")
            
        final_score = round((score / total) * 10, 2)
        if final_score >= 8:
            st.balloons()
            st.success(f"😎 Quá đỉnh! Điểm số: {final_score}/10 ({score}/{total} câu)")
        elif final_score >= 5:
            st.warning(f"😮 Tạm ổn nè! Điểm số: {final_score}/10 ({score}/{total} câu).")
        else:
            st.error(f"💔 Điểm số: {final_score}/10 ({score}/{total} câu). Ôn bài lại nhé!")
