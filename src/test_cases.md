# 5 Test Cases Có Mục Đích (Chatbot vs ReAct Agent)

## 2 Cases: Chatbot đủ tốt (Query đơn giản)
**TC1:** "Headhunter là làm nghề gì?"
* **Expected:** Chatbot định nghĩa nhanh từ kiến thức nền.
* **Actual:** Chatbot thắng (xử lý tức thì, không tốn token gọi loop).

**TC2:** "Viết email template 50 chữ mời phỏng vấn vị trí Data."
* **Expected & Actual:** Chatbot thắng. Sinh text mượt mà, không cần grounding data.

## 2 Cases: Agent vượt trội (Cần grounding và multi-step)
**TC3:** "Tìm cho tôi 1 ứng viên Data Analyst và cho biết email của họ."
* **Expected:** Chatbot ảo giác (bịa email). Agent qua 2 bước tool để lấy email thật.
* **Actual:** Agent thắng. Agent gọi `search_candidates` -> lấy ID 'U01' -> gọi `get_profile_text` -> trích xuất đúng 'nguyenvana@mock.com'.

**TC4:** "Trần Thị B có số điện thoại public không?"
* **Expected & Actual:** Agent thắng. Chatbot chịu chết, Agent dò ra ID U02 và phát hiện ứng viên này không public SĐT.

## 1 Edge Case (Kiểm thử lỗi/Graceful Degradation)
**TC5:** "Tìm số điện thoại của ứng viên có kỹ năng Lái Đĩa Bay."
* **Expected:** Tool 1 trả về `[]`. Agent phải bắt được và xin lỗi, KHÔNG ĐƯỢC bịa tool.
* **Actual:** Agent nhận `Observation: []` -> Lập tức suy nghĩ "Không có ứng viên" và xuất `Final Answer` báo lỗi lịch sự. Xử lý êm đẹp!
