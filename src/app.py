# lab3/app.py
import streamlit as st
import re
import time
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH TRANG & BIẾN TOÀN CỤC
# ==========================================
st.set_page_config(page_title="Headhunter AI Assistant", page_icon="🎯", layout="wide")

# TODO: Thay API Key của bạn vào đây
API_KEY = "your api key" 

# ==========================================
# 2. ĐỊNH NGHĨA TOOLS (MOCK DATA)
# ==========================================
def search_candidates(keyword: str) -> str:
    time.sleep(1) # Giả lập độ trễ mạng
    keyword = keyword.lower()
    if "data" in keyword:
        return '[{"id": "U01", "name": "Nguyễn Văn A", "headline": "Senior Data Analyst"}, {"id": "U02", "name": "Trần Thị B", "headline": "Data Scientist"}]'
    return '[]'

def get_profile_text(profile_id: str) -> str:
    time.sleep(1)
    profiles = {
        "U01": "Kinh nghiệm: 5 năm Data Analyst tại Vin. Kỹ năng: Python, SQL. Liên hệ: nguyenvana@mock.com, sđt: 0901234567.",
        "U02": "Kinh nghiệm: 2 năm làm Data Scientist. Liên hệ qua LinkedIn message, không public sđt."
    }
    return profiles.get(profile_id, "Không tìm thấy thông tin chi tiết cho ID này.")

TOOLS_MAP = {
    "search_candidates": search_candidates,
    "get_profile_text": get_profile_text
}

# ==========================================
# 3. GIAO DIỆN (UI LAYOUT)
# ==========================================
st.title("🎯 Headhunter AI Assistant")
st.markdown("Hệ thống tự động tra cứu và trích xuất thông tin ứng viên (Powered by ReAct Agent)")
st.divider()

# Chia Layout thành 3 cột
col1, col2, col3 = st.columns([1, 1.5, 1], gap="large")

# --- CỘT 1: KHU VỰC ĐIỀU KHIỂN ---
with col1:
    st.subheader("🛠️ Bảng Điều Khiển")
    mode = st.radio("Chế độ hoạt động:", ["ReAct Agent (Đề xuất)", "Chatbot Thường"])
    
    st.markdown("**Gợi ý nhanh:**")
    if st.button("Tìm email của Nguyễn Văn A"):
        st.session_state.user_query = "Tìm cho tôi 1 ứng viên Data Analyst và cho biết email của họ."
    if st.button("Lấy SĐT người lái Đĩa Bay"):
        st.session_state.user_query = "Tìm số điện thoại của ứng viên có kỹ năng Lái Đĩa Bay."
        
    query = st.text_area("Nhập yêu cầu của bạn:", 
                         value=st.session_state.get('user_query', ''), 
                         height=100)
    
    run_btn = st.button("🚀 Chạy AI", type="primary", use_container_width=True)

# --- CỘT 2: THE GLASS BOX (TRACE LOG) ---
with col2:
    st.subheader("🧠 Quá Trình Suy Luận (Trace)")
    trace_container = st.container(height=500) # Khung cuộn được

# --- CỘT 3: KẾT QUẢ & CRM ---
with col3:
    st.subheader("✅ Kết Quả (Final Output)")
    result_container = st.empty()
    action_container = st.empty()

# ==========================================
# 4. LOGIC CHẠY AGENT TRÊN UI
# ==========================================
if run_btn and query:
    if mode == "Chatbot Thường":
        with trace_container:
            st.warning("Chatbot đang chạy (Không có tool). Mọi thông tin có thể là ảo giác!")
        
        # Chạy Chatbot Baseline
        client = OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Bạn là trợ lý Headhunter. Không có tool."},
                      {"role": "user", "content": query}]
        )
        result_container.success(response.choices[0].message.content)
        
    else:
        # Chạy ReAct Agent
        client = OpenAI(api_key=API_KEY)
        SYSTEM_PROMPT = """Bạn là một ReAct Agent hỗ trợ Headhunter trích xuất thông tin.
        Bạn có quyền truy cập các công cụ sau:
        1. search_candidates(keyword: str): Tìm danh sách ứng viên (trả về mảng JSON).
        2. get_profile_text(profile_id: str): Lấy text chi tiết của ứng viên bằng ID (truyền đúng ID, VD: U01).

        Để sử dụng công cụ, bạn BẮT BUỘC tuân thủ định dạng sau (không thêm bớt):
        Thought: Suy nghĩ của bạn
        Action: tên_công_cụ_cần_gọi
        Action Input: tham_số_truyền_vào

        Sau khi có Observation, hãy suy nghĩ tiếp. 
        Khi đã có đủ thông tin, bạn DỪNG LẠI bằng định dạng:
        Thought: Tôi đã có đủ thông tin.
        Final Answer: Câu trả lời cuối cùng gửi cho người dùng.

        Ranh giới an toàn: KHÔNG bịa email/sđt. Nếu tool trả về [], hãy báo cáo là không tìm thấy.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": query}]
        
        result_container.info("⏳ Agent đang xử lý...")
        
        with trace_container:
            for step in range(5):
                st.markdown(f"**--- Bước {step + 1} ---**")
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini", messages=messages, temperature=0.0, stop=["Observation:"]
                )
                output = response.choices[0].message.content.strip()
                messages.append({"role": "assistant", "content": output})
                
                # In Thought & Action ra UI
                if "Thought:" in output:
                    thought = output.split("Thought:")[1].split("Action:")[0].strip() if "Action:" in output else output.split("Thought:")[1].strip()
                    st.info(f"🤔 **Suy nghĩ:** {thought}")
                
                if "Final Answer:" in output:
                    final_ans = output.split("Final Answer:")[-1].strip()
                    st.success("✅ Đã tìm thấy kết quả!")
                    
                    # Cập nhật kết quả sang cột 3
                    result_container.success(final_ans)
                    action_container.button("📥 Lưu vào hệ thống CRM")
                    break
                
                action_match = re.search(r"Action:\s*(.+)", output)
                input_match = re.search(r"Action Input:\s*(.+)", output)
                
                if action_match and input_match:
                    action = action_match.group(1).strip()
                    action_input = input_match.group(1).strip(' "\'')
                    
                    st.warning(f"⚡ **Hành động:** Gọi tool `{action}` với tham số `{action_input}`")
                    
                    # Chạy tool
                    with st.spinner("Đang truy xuất dữ liệu..."):
                        if action in TOOLS_MAP:
                            observation = str(TOOLS_MAP[action](action_input))
                        else:
                            observation = f"Lỗi: Tool '{action}' không tồn tại."
                    
                    st.code(f"👁️ Observation: {observation}", language="json")
                    messages.append({"role": "user", "content": f"Observation: {observation}\n"})
                else:
                    msg = "Observation: Lỗi định dạng. Dùng đúng Thought/Action/Action Input."
                    st.error(msg)
                    messages.append({"role": "user", "content": msg + "\n"})
            else:
                st.error("🚨 Vượt quá số bước cho phép. Đã chuyển cho người thật xử lý.")
                result_container.error("Agent không thể hoàn thành tác vụ.")