# lab3/agent.py
import os
import re
import time
from dotenv import load_dotenv
from openai import OpenAI
from src.tools import TOOLS_MAP
from src.telemetry.metrics import tracker

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Bạn là một ReAct Agent hỗ trợ Headhunter trích xuất thông tin.
Bạn có quyền truy cập các công cụ sau:
1. search_candidates(keyword: str): Tìm danh sách ứng viên (trả về mảng JSON).
2. get_profile_text(profile_id: str): Lấy text chi tiết của ứng viên bằng ID (truyền đúng ID, VD: U01).
3. testing_func(): Hàm này chỉ để test xem có gọi được hay không, không phục vụ chức năng gì.
4. send_email_to_candidate(email: str, subject: str, message: str): Gửi email tiếp cận đến ứng viên (chỉ gọi khi đã có email hợp lệ).

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

MAX_ITERATIONS = 5


def is_valid_tool(action: str) -> bool:
    return action in TOOLS_MAP
    
def run_agent(user_query: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    print(f"\n{'='*40}\n[USER QUERY]: {user_query}\n{'-'*40}")
    
    for step in range(MAX_ITERATIONS):
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            stop=["Observation:"] # Rất quan trọng: Bắt LLM dừng lại để code chạy Tool
        )
        latency_ms = int((time.time() - start_time) * 1000)

        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        tracker.track_request(
            provider="openai",
            model="gpt-4o-mini",
            usage=usage,
            latency_ms=latency_ms,
        )
        
        output = response.choices[0].message.content.strip()
        print(output)
        messages.append({"role": "assistant", "content": output})
        
        # Check điều kiện hoàn thành
        if "Final Answer:" in output:
            summary = tracker.summarize()
            print("\n[METRICS SUMMARY]")
            print(f"Average Latency (P50): {summary['average_latency_p50_ms']}ms")
            print(f"Max Latency (P99): {summary['max_latency_p99_ms']}ms")
            print(f"Average Tokens per Task: {summary['average_tokens_per_task']} tokens")
            print(f"Total Cost of Test Suite: ${summary['total_cost_test_suite_usd']}")
            print(f"{'='*40}\n")
            return
            
        # Parse Tool
        action_match = re.search(r"Action:\s*(.+)", output)
        input_match = re.search(r"Action Input:\s*(.+)", output)
        
        if action_match and input_match:
            action = action_match.group(1).strip()
            action_input = input_match.group(1).strip(' "\'')
            
            if action in TOOLS_MAP:
                observation = str(TOOLS_MAP[action](action_input))
            else:
                observation = f"Lỗi: Tool '{action}' không tồn tại."
                
            obs_msg = f"Observation: {observation}"
            print(f"\033[92m{obs_msg}\033[0m") # In màu xanh lá cho dễ nhìn tool
            messages.append({"role": "user", "content": obs_msg + "\n"})
        else:
            obs_msg = "Observation: Lỗi cú pháp. Hãy dùng đúng format Action và Action Input."
            print(f"\033[91m{obs_msg}\033[0m")
            messages.append({"role": "user", "content": obs_msg + "\n"})

    # Nhánh Fallback / Escalation
    summary = tracker.summarize()
    print("\n[METRICS SUMMARY]")
    print(f"Average Latency (P50): {summary['average_latency_p50_ms']}ms")
    print(f"Max Latency (P99): {summary['max_latency_p99_ms']}ms")
    print(f"Average Tokens per Task: {summary['average_tokens_per_task']} tokens")
    print(f"Total Cost of Test Suite: ${summary['total_cost_test_suite_usd']}")
    print(f"\n\033[91m[FALLBACK]: Agent đã chạm ngưỡng {MAX_ITERATIONS} bước. Đang chuyển giao cho chuyên viên Headhunter xử lý.\033[0m\n{'='*40}")

if __name__ == "__main__":
    # Test case 3 trong file bài tập
    run_agent("Tìm cho tôi 1 ứng viên Data Analyst và cho biết email của họ.")
