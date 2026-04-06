# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trần Sỹ Minh Quân
- **Student ID**: 2A202600308
- **Date**: 6-4-2026

---

## I. Technical Contribution (15 Points)

Trong project này, tôi build tool `send_email_to_candidate` để ReAct Agent có thể gửi email tiếp cận ứng viên đúng định dạng, và build hàm ghi nhận telemetry metrics để đo latency, token usage, và cost ước tính cho từng lượt gọi model.

- **Modules Implementated**: `src/tools.py`, `src/telemetry/metrics.py`, `src/agent/agent.py`
- **Code Highlights**: 
```python
def send_email_to_candidate(email: str, subject: str, message: str) -> str:
    if "@" not in email:
        return "Lỗi: Hành động thất bại. Địa chỉ email không hợp lệ hoặc bị thiếu."

    return f"Thành công: Đã gửi email tới '{email}' với tiêu đề '{subject}'."


def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
    metric = {
        "provider": provider,
        "model": model,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "latency_ms": latency_ms,
        "cost_estimate": self._calculate_cost(provider, model, usage)
    }
    self.session_metrics.append(metric)
```
- **Documentation**: `send_email_to_candidate` là tool giúp Agent thực hiện hành động có tính nghiệp vụ cao hơn thay vì chỉ trả lời văn bản. Mình thêm bước kiểm tra email hợp lệ bằng dấu `@` để tránh Agent gửi dữ liệu đầu vào sai định dạng vào tool. Còn hàm telemetry metrics ghi lại các chỉ số quan trọng cho mỗi request như `prompt_tokens`, `completion_tokens`, `total_tokens`, `latency_ms`, và `cost_estimate`. Các metrics này được Agent gọi ở mỗi vòng lặp để tổng hợp hiệu năng toàn bộ phiên chạy, từ đó có thể đánh giá được chất lượng phản hồi của chatbot và ReAct agent một cách định lượng.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Agent bị lỗi hallucinate dữ liệu liên hệ khi xử lý yêu cầu kiểu "tìm ứng viên Data Analyst và gửi email cho họ". Ở bản prompt cũ, model đã cố tự suy ra hoặc bịa email từ tên ứng viên rồi gọi `send_email_to_candidate` với một giá trị không hợp lệ, khiến tool trả về lỗi vì không có địa chỉ email đúng định dạng.
- **Log Source**: Observation: Lỗi: Hành động thất bại. Địa chỉ email không hợp lệ hoặc bị thiếu.
- **Diagnosis**: Prompt cũ chưa đủ chặt chẽ cho các dữ liệu nhạy cảm như email và số điện thoại, vì vậy LLM đã cố hoàn thiện câu trả lời bằng cách tự điền thông tin còn thiếu, nên nó dùng sai tool input và đi ngược nguyên tắc không bịa email/sđt.
- **Solution**: Prompt hiện tại đã sửa đúng điểm này bằng cách ghi rõ tool send_email_to_candidate() chỉ được gọi khi đã có email hợp lệ, đồng thời thêm chỉ thị an toàn: KHÔNG bịa email/sđt và nếu tool trả về `[]` thì phải báo cáo là không tìm thấy.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1.  **Reasoning**: Với tôi, điểm khác biệt rõ nhất là ReAct không trả lời kiểu đoán, mà đi theo từng bước rõ ràng. Phần `Thought` giống như cách agent tự nhắc mình phải kiểm tra gì trước, làm gì sau, nên nó hợp với các bài toán nhiều bước hơn là câu trả lời ngắn.
2.  **Reliability**: Chatbot thường ổn hơn khi câu hỏi đơn giản và chỉ cần một câu trả lời nhanh, còn Agent đôi lúc lại rườm rà hơn mức cần thiết. Khi nhiệm vụ không thật sự cần tool, Agent rất tốn token, lại còn tăng latency. Do đó, với những problem có yêu cầu đơn giản, tôi thấy Chatbot tốt hơn Agent.
3.  **Observation**: Phần tôi thấy giá trị nhất là `Observation` giúp agent bám vào dữ liệu thật thay vì suy đoán. Khi tool trả về thông tin rỗng hoặc dữ liệu không hợp lệ, agent có cơ sở để đổi hướng hoặc báo không tìm thấy thay vì bịa thêm. Nhờ vậy, phản hồi của agent thường thực tế hơn.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Cách parse bằng Regex hiện tại chạy được cho bài lab, nhưng càng mở rộng thì càng dễ vỡ khi format đầu ra thay đổi. Nếu làm ở mức production, tôi sẽ chuyển sang kiến trúc có quản lý state rõ ràng như LangGraph, đồng thời dùng Function Calling để nhận dữ liệu dạng cấu trúc thay vì phải bóc tách chuỗi thủ công.
- **Safety**: Tôi sẽ thêm lớp bảo vệ dữ liệu cá nhân trước khi đưa thông tin vào prompt, ví dụ che bớt email/số điện thoại trong Observation. Ngoài ra, với các hành động nhạy cảm như gửi email, tôi nghĩ cần có bước duyệt của con người để giảm rủi ro thao tác sai.
- **Performance**: Khi số lượng tool tăng lên, không nên nhét toàn bộ vào cùng một prompt vì sẽ tốn context và token. Giải pháp phù hợp hơn là có lớp chọn tool theo ngữ cảnh, chỉ nạp các tool thật sự liên quan cho từng truy vấn để giảm độ trễ và chi phí.

---