# lab3/chatbot.py
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from src.telemetry.metrics import tracker

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Bạn là trợ lý Headhunter xuất sắc. Hãy trả lời câu hỏi của người dùng một cách chuyên nghiệp. 
Lưu ý: Bạn KHÔNG CÓ khả năng tìm kiếm internet hay dùng tool. Chỉ trả lời bằng kiến thức nền có sẵn."""

def run_chatbot(user_query: str):
    print(f"\n[USER QUERY]: {user_query}\n")
    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3
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

        print("[CHATBOT ANSWER]:\n", response.choices[0].message.content)

        summary = tracker.summarize()
        print("\n[METRICS SUMMARY]")
        print(f"Average Latency (P50): {summary['average_latency_p50_ms']}ms")
        print(f"Max Latency (P99): {summary['max_latency_p99_ms']}ms")
        print(f"Average Tokens per Task: {summary['average_tokens_per_task']} tokens")
        print(f"Total Cost of Test Suite: ${summary['total_cost_test_suite_usd']}")

    except Exception as e:
        print(f"Lỗi API: {e}")

if __name__ == "__main__":
    # Test thử 1 case
    run_chatbot("Tìm cho tôi sđt của ứng viên Data Analyst tên Nguyễn Văn A.")
