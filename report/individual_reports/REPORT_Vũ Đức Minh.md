# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Vũ Đức Minh
- **Student ID**: 2A202600439
- **Date**: 4/6/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

-  `src/tools.py`
- **Code Highlights**: 
```python
def get_profile_text(profile_id: str) -> str:
    """Lấy nội dung chi tiết profile (Bio, Kinh nghiệm, Liên hệ) bằng ID ứng viên."""
    profiles = {
        "U01": "Kinh nghiệm: 5 năm Data Analyst tại Vin. Kỹ năng: Python, SQL. Liên hệ: nguyenvana@mock.com, sđt: 0901234567.",
        "U02": "Kinh nghiệm: 2 năm làm Data Scientist. Liên hệ qua LinkedIn message, không public sđt.",
        "U03": "Kinh nghiệm: Chạy Ads Facebook. Liên hệ sđt: 0988888888."
    }
    return profiles.get(profile_id, "Không tìm thấy thông tin chi tiết cho ID này.")

def testing_func() -> str:
    """Hàm này chỉ để test xem có gọi được hay không, không phục vụ chức năng gì."""
    return "Hàm testing_func đã được gọi thành công!"

```


---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Chưa có gửi email cho ứng viên để phản hồi
- **Solution**: Cần thêm hàm send_email và add SYSTEM_PROMPT sao cho agent gọi được email


---
## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1. **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
   - Khối `Thought` (suy nghĩ) hoạt động như một cơ chế Chain-of-Thought (chuỗi tư duy), ép LLM phải lập kế hoạch trước khi hành động thay vì đoán mò câu trả lời ngay lập tức. Ví dụ, thay vì trực tiếp bịa ra một email để gửi, Agent sẽ tự tư duy theo các bước: *Cần tìm ứng viên -> Lấy Profile ID -> Trích xuất văn bản profile để tìm email -> Kiểm tra xem email có hợp lệ không (@) -> Gọi hàm `send_email_to_candidate`*. Điều này giúp Agent giải quyết các bài toán nhiều bước một cách logic và chính xác hơn hẳn Chatbot thông thường.

2. **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?
   - Agent hoạt động kém hiệu quả hơn Chatbot trong các tác vụ giao tiếp cơ bản hoặc khi trả lời các câu hỏi kiến thức chung không dùng tool. Do cơ chế vòng lặp ReAct, Agent phản hồi chậm hơn, tốn nhiều token hơn và đôi khi bị stuck trong các vòng lặp lỗi nếu gọi sai tham số liên tục khiến chạm ngưỡng `MAX_ITERATIONS`.

3. **Observation**: How did the environment feedback (observations) influence the next steps?
   - `Observation` đóng vai trò là "mỏ neo" thực tế cho Agent. Trong hàm `send_email_to_candidate` tôi đã viết, nếu Agent cố tình gọi hàm khi chưa có email hợp lệ, hệ thống sẽ trả về Observation lỗi: *"Lỗi: Hành động thất bại. Địa chỉ email không hợp lệ..."*. Nhờ đọc được Observation này, Agent nhận ra sai lầm của mình, tự động dừng việc gửi email và quay lại bước trước đó (gọi `get_profile_text`) để tìm kiếm địa chỉ email chính xác trước khi gửi lại.

---
## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Xây dựng hệ thống hàng đợi bất đồng bộ (Asynchronous Task Queue như Celery hoặc RabbitMQ) cho các tool tốn thời gian. Ví dụ: việc gửi email thực tế (qua SMTP) hoặc cào dữ liệu có thể mất vài giây, nếu chạy đồng bộ sẽ làm nghẽn toàn bộ luồng suy nghĩ của Agent.
- **Safety**: 
  - Tích hợp cơ chế **Human-in-the-loop (HITL)**: Đối với các hành động không thể hoàn tác (như gửi email thật cho ứng viên), Agent chỉ được phép tạo bản nháp (draft) và phải có nút "Approve" từ Headhunter (con người) trước khi thực thi.
  - Sử dụng một 'Supervisor' LLM (nhẹ và nhanh hơn) để quét nội dung email trước khi gửi nhằm đảm bảo văn phong chuyên nghiệp và không chứa nội dung nhạy cảm/ảo giác.
- **Performance**: Áp dụng Retrieval-Augmented Tools (RAG cho tools). Khi hệ thống mở rộng lên hàng chục hoặc hàng trăm công cụ, việc nhét tất cả vào `SYSTEM_PROMPT` sẽ làm quá tải context window và khiến LLM dễ gọi nhầm hàm. Ta có thể dùng Vector DB để lưu trữ mô tả của các tools, sau đó tự động truy xuất (retrieve) và chỉ đưa vào prompt 3-5 tools phù hợp nhất với câu hỏi hiện tại của người dùng.