# lab3/chatbot.py
from openai import OpenAI

# TODO: Thay API Key của bạn vào đây
client = OpenAI(api_key="your api key")

SYSTEM_PROMPT = """Bạn là trợ lý Headhunter xuất sắc. Hãy trả lời câu hỏi của người dùng một cách chuyên nghiệp. 
Lưu ý: Bạn KHÔNG CÓ khả năng tìm kiếm internet hay dùng tool. Chỉ trả lời bằng kiến thức nền có sẵn."""

def run_chatbot(user_query: str):
    print(f"\n[USER QUERY]: {user_query}\n")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3
        )
        print("[CHATBOT ANSWER]:\n", response.choices[0].message.content)
    except Exception as e:
        print(f"Lỗi API: {e}")

if __name__ == "__main__":
    # Test thử 1 case
    run_chatbot("Tìm cho tôi sđt của ứng viên Data Analyst tên Nguyễn Văn A.")
