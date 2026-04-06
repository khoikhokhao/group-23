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

TOOLS_MAP = {
    "search_candidates": search_candidates,
    "get_profile_text": get_profile_text
}
