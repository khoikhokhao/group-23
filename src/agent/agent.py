# lab3/agent.py
import re
from openai import OpenAI
from tools import TOOLS_MAP

# TODO: Thay API Key của bạn vào đây
client = OpenAI(api_key="your api key")

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

MAX_ITERATIONS = 5

def run_agent(user_query: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    print(f"\n{'='*40}\n[USER QUERY]: {user_query}\n{'-'*40}")
    
    for step in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            stop=["Observation:"] # Rất quan trọng: Bắt LLM dừng lại để code chạy Tool
        )
        
        output = response.choices[0].message.content.strip()
        print(output)
        messages.append({"role": "assistant", "content": output})
        
        # Check điều kiện hoàn thành
        if "Final Answer:" in output:
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
    print(f"\n\033[91m[FALLBACK]: Agent đã chạm ngưỡng {MAX_ITERATIONS} bước. Đang chuyển giao cho chuyên viên Headhunter xử lý.\033[0m\n{'='*40}")

if __name__ == "__main__":
    # Test case 3 trong file bài tập
    run_agent("Tìm cho tôi 1 ứng viên Data Analyst và cho biết email của họ.")
