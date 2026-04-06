
# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Phạm Minh Khôi
- **Student ID**: 2A20260262
- **Date**: 6-4-2026

---

## I. Technical Contribution (15 Points)

Trong project này, mình đảm nhiệm việc xây dựng vòng lặp ReAct cốt lõi, tích hợp giao diện "Glass Box" bằng Streamlit để trực quan hóa trace log, và tinh chỉnh cơ chế Parsing (Bóc tách dữ liệu) để kết nối LLM với các Python functions nội bộ.

- **Modules Implementated**: app.py (chứa UI và logic Agent)
- **Code Highlights**: 
```python
# Bóc tách Action và Action Input từ LLM output
action_match = re.search(r"Action:\s*(.+)", output)
input_match = re.search(r"Action Input:\s*(.+)", output)

if action_match and input_match:
    action = action_match.group(1).strip()
    # Dùng strip() để gọt sạch dấu ngoặc kép hoặc nháy đơn dư thừa do LLM tự sinh ra
    action_input = input_match.group(1).strip(' "\'') 
    
    # Thực thi Tool an toàn
    if action in TOOLS_MAP:
        observation = str(TOOLS_MAP[action](action_input))
```
- **Documentation**: Đoạn code trên đóng vai trò là "Cầu nối" (Bridge) trong vòng lặp ReAct. Sau khi LLM sinh ra text, code sẽ dùng Regex để bắt lệnh. Điểm quan trọng nhất là hàm strip(' "\'') giúp xử lý tình trạng LLM tự động thêm ngoặc kép vào tham số (ví dụ: "U01" thay vì U01), đảm bảo Dictionary TOOLS_MAP nhận đúng key và không bị crash hệ thống.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Agent bị lỗi Format Hallucination (Ảo giác định dạng), tự ý chèn thêm dấu ngoặc tròn khi gọi tool giống cú pháp code Python.
- **Log Source**: Observation: Lỗi: Tool 'search_candidates("Data Analyst")' không tồn tại.
- **Diagnosis**: Do System Prompt ban đầu liệt kê công cụ dưới dạng search_candidates(keyword). LLM đã bắt chước y hệt cấu trúc này (bao gồm ngoặc tròn) thay vì chỉ xuất tên tool, khiến Regex bóc tách sai.
- **Solution**: Cập nhật System Prompt (Negative Prompting) với chỉ thị nghiêm ngặt: "Format BẮT BUỘC: KHÔNG dùng dấu ngoặc tròn trong Action, chỉ ghi giá trị tham số vào Action Input".

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Khối Thought hoạt động như một "cuốn sổ nháp" (scratchpad). Khác với Chatbot phải nặn ra kết quả cuối cùng ngay lập tức (thường dẫn đến ảo giác), Agent dùng Thought để chia nhỏ bài toán (Chain-of-Thought): "Muốn có email -> phải tìm ID trước -> dùng ID để tra profile". Điều này giúp Agent giải quyết được các truy vấn đa bước (multi-step queries).
2.  **Reliability**: Agent hoạt động tệ hơn Chatbot ở những tác vụ đơn giản, ví dụ như "Viết một email template mời phỏng vấn". Chatbot sinh text ngay trong 1 giây. Agent lại bị "over-thinking", bối rối về định dạng ReAct, sau đó tốn thời gian gọi tool cào data ứng viên để cá nhân hóa bức thư dù không được yêu cầu, gây lãng phí Token và thời gian (Latency cao).
3.  **Observation**: eedback từ môi trường đóng vai trò là Grounding (Mỏ neo thực tế). Khi yêu cầu tìm "Ứng viên lái đĩa bay", tool trả về Observation: []. Agent lập tức đọc được feedback này và xin lỗi người dùng một cách êm đẹp (Graceful Degradation), trái ngược hoàn toàn với Chatbot truyền thống thường cố gắng bịa ra một ứng viên ảo để chiều lòng người dùng.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Việc dùng Regex để bóc tách string trong vòng for/while là quá mỏng manh (brittle). Ở môi trường Production, mình sẽ chuyển sang sử dụng framework LangGraph để quản lý trạng thái (State) và luồng rẽ nhánh linh hoạt hơn, kết hợp với tính năng Function Calling (Structured Outputs) gốc của OpenAI API để ép kiểu dữ liệu JSON, loại bỏ hoàn toàn lỗi Parsing.
- **Safety**:Cần triển khai cơ chế PII Redaction (Che giấu dữ liệu cá nhân). Trước khi đưa Observation chứa email/SĐT của ứng viên vào lại LLM prompt, hệ thống cần mask nó lại (VD: nguyenvana@***.com) để tránh lộ lọt dữ liệu nhạy cảm cho bên cung cấp API bên thứ 3. Ngoài ra, cần thiết kế nút "Human-in-the-loop" (Người duyệt) trên UI trước khi lưu data vào CRM.
- **Performance**: Khi hệ thống Headhunter mở rộng lên hàng chục tools (VD: check lương, check lịch sử cty, search Github), mình sẽ tích hợp một Tool Retrieval Agent. Nó sẽ dùng Vector Database để tìm và nạp (inject) chỉ 3-5 tools cần thiết nhất vào Prompt cho mỗi truy vấn, giúp tiết kiệm Context Window và giảm chi phí Token.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
