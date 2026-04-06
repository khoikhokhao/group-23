# lab3/tools.py

def search_candidates(keyword: str) -> str:
    """Tìm kiếm danh sách ứng viên dựa trên từ khóa chức danh."""
    keyword = keyword.lower()
    if "data" in keyword or "phân tích" in keyword:
        return '[{"id": "U01", "name": "Nguyễn Văn A", "headline": "Senior Data Analyst"}, {"id": "U02", "name": "Trần Thị B", "headline": "Data Scientist"}]'
    elif "marketing" in keyword:
        return '[{"id": "U03", "name": "Lê Văn C", "headline": "Marketing Manager"}]'
    else:
        return '[]'

def get_profile_text(profile_id: str) -> str:
    """Lấy nội dung chi tiết profile (Bio, Kinh nghiệm, Liên hệ) bằng ID ứng viên."""
    profiles = {
        "U01": "Kinh nghiệm: 5 năm Data Analyst tại Vin. Kỹ năng: Python, SQL. Liên hệ: nguyenvana@mock.com, sđt: 0901234567.",
        "U02": "Kinh nghiệm: 2 năm làm Data Scientist. Liên hệ qua LinkedIn message, không public sđt.",
        "U03": "Kinh nghiệm: Chạy Ads Facebook. Liên hệ sđt: 0988888888."
    }
    return profiles.get(profile_id, "Không tìm thấy thông tin chi tiết cho ID này.")

<<<<<<< HEAD
def testing_func() -> str:
    """Hàm này chỉ để test xem có gọi được hay không, không phục vụ chức năng gì."""
    return "Hàm testing_func đã được gọi thành công!"

=======
def send_email_to_candidate(email: str, subject: str, message: str) -> str:
    """
    Gửi email tiếp cận (cold email) đến ứng viên.
    LƯU Ý: Chỉ gọi hàm này khi bạn đã trích xuất được một địa chỉ email hợp lệ 
    (có chứa ký tự '@') từ hàm get_profile_text.
    """
    if "@" not in email:
        return "Lỗi: Hành động thất bại. Địa chỉ email không hợp lệ hoặc bị thiếu."
    
    # Giả lập việc gửi email thành công
    return f"Thành công: Đã gửi email tới '{email}' với tiêu đề '{subject}'."
>>>>>>> 92beed24ba6e6d5299fac7ddfef1d423bb026bea

TOOLS_MAP = {
    "search_candidates": search_candidates,
    "get_profile_text": get_profile_text,
    "send_email_to_candidate": send_email_to_candidate
}

