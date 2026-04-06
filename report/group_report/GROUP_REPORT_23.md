# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: 23
- **Team Members**:Phạm Minh Khôi, Trần Sỹ Minh Quân, Vũ Đức Minh, Ngô Quang Tăng, Nguyễn Thế Anh
- **Deployment Date**: 6-4-2026

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: 80%/ 5 test cases
- **Key Outcome**: ReAct Agent của chúng tôi đánh bại hoàn toàn Chatbot baseline trong các truy vấn đa bước (multi-step queries). Nó có khả năng Grounding (bám sát dữ liệu thực qua việc gọi Tool) để lấy chính xác email/SĐT ứng viên, loại bỏ hoàn toàn tình trạng ảo giác (hallucination) thường gặp ở Chatbot.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
*Hệ thống sử dụng vòng lặp suy luận ReAct (Reasoning and Acting). LLM sẽ phân tích câu hỏi, suy nghĩ (Thought), quyết định gọi công cụ (Action) kèm tham số (Action Input), nhận kết quả (Observation), và lặp lại cho đến khi đủ dữ kiện để đưa ra câu trả lời cuối cùng (Final Answer).*

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_candidates` | `search_candidates` | Tìm kiếm ID và tên ứng viên dựa trên chức danh (VD: "Data Analyst").. |
| `get_profile_text` | `string (profile_id)` | Truy xuất chi tiết Bio, kinh nghiệm, email, số điện thoại dựa vào ID. |

### 2.3 LLM Providers Used
- **Primary**: OpenAI gpt-4o-mini (Tối ưu cho tốc độ và chi phí rẻ trong vòng lặp nhiều bước).
- **Secondary (Backup)**: [e.g., Gemini 1.5 Flash]

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: ~2,500ms (Cho các luồng chạy đủ 2 tools).
- **Max Latency (P99)**: 4,800ms (Trong trường hợp Agent xử lý lỗi format và gọi lại).
- **Average Tokens per Task**: ~450 tokens (Bao gồm System Prompt và lịch sử vòng lặp).
- **Total Cost of Test Suite**: ~$0.001 (Rất rẻ nhờ sử dụng model gpt-4o-mini).

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study 1: Parameter Parsing Error (Kẹt tham số)
- **Input**: "Tìm email của ứng viên Data Analyst tên Nguyễn Văn A"
- **Observation**: Agent gọi get_profile_text(profile_id="U01") thay vì U01. Tool trả về lỗi do hệ thống chỉ nhận string không có dấu ngoặc kép.
- **Root Cause**: LLM tự động thêm cặp dấu ngoặc kép " " vào chuỗi tham số theo thói quen định dạng JSON.
- **Fix**: Cập nhật script Python bằng cách thêm hàm strip(' "\'') để gọt sạch dấu ngoặc kép dư thừa trước khi truyền vào Tool.
### Case Study 2: Format Forgetting (Quên định dạng)
- **Input**:"Viết email template mời phỏng vấn vị trí Data"
- **Observation**: Agent sinh thẳng nội dung email mà không bọc trong thẻ Final Answer:, khiến code báo lỗi format. Sau khi bị bắt lỗi, Agent bị "over-thinking", tự động gọi tool cào data ứng viên để cá nhân hóa email thay vì viết template chung chung.
- **Root Cause**: Input quá đơn giản khiến LLM "quên" vai trò Agent và cư xử như một Chatbot thông thường..
---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: Cập nhật System Prompt v2, thêm dòng ranh giới an toàn: "KHÔNG ĐƯỢC tự bịa email/sđt. Nếu tool trả về mảng rỗng [], hãy báo cáo là không tìm thấy."
- **Result**: Trong ca kiểm thử biên (Edge Case: Tìm ứng viên Lái Đĩa Bay), Agent v1 cố gắng bịa ra một ID giả để tra cứu. Agent v2 (có prompt mới) đã nhận diện được Observation: [] và lập tức kích hoạt Final Answer báo lỗi lịch sự. Giảm 100% tỷ lệ ảo giác ở các ca không có dữ liệu.

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q (Hỏi định nghĩa, Viết template) | Xử lý tức thì (1s), văn phong tốt. | Bối rối về định dạng, tốn nhiều loop không cần thiết. | **Chatbot** |
| Multi-step (Tìm email ứng viên Data) | Ảo giác (Bịa bừa email). | Chính xác. Gọi đủ 2 tools, trích xuất đúng email thực tế. | **Agent** |
| Edge Case (Tìm ứng viên không tồn tại)| Bịa ra ứng viên ảo. | Dừng ngay bước 1, xin lỗi êm đẹp. | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: ần thêm lớp mã hóa dữ liệu cá nhân (PII redaction) trong Observation để tránh việc LLM API ghi log lại số điện thoại/email thực của ứng viên quỹ.
- **Guardrails**: Đã thiết lập cứng MAX_ITERATIONS = 5 trong code. Nếu Agent lặp quá 5 vòng mà không tìm ra Final Answer, hệ thống tự động ngắt kết nối và Escalate (chuyển giao) cho chuyên viên Headhunter con người.
- **Scaling**: Việc dùng Regex để bóc tách Action Input hiện tại rất dễ gãy (brittle). Khi scale lên nhiều tools hơn, cần chuyển đổi kiến trúc sang dùng LangChain/LangGraph hoặc tính năng Function Calling/Structured Outputs native của OpenAI để đảm bảo tham số truyền vào tool luôn đúng định dạng.

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
