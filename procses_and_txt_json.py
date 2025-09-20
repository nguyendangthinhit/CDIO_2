import re
import json

def clean_text(raw_text: str) -> dict:
    """
    Chuẩn hóa dữ liệu ngành học từ text sang dict JSON.
    """

    # Bảng map từ khóa thô -> key chuẩn
    keyword_map = {
        "Giới thiệu": "gioi_thieu",
        "Mục tiêu": "muc_tieu",
        "Chương trình": "chuong_trinh",
        "Cơ hội": "co_hoi",
        "Liên hệ": "lien_he",
        "Tuyển sinh": "tuyen_sinh"
    }

    # Regex tách các mục dựa theo từ khóa
    # (?=Giới thiệu|Mục tiêu|...) để giữ nguyên từ khóa trong split
    pattern = r"(?=(Giới thiệu:|Mục tiêu:|Chương trình:|Cơ hội:|Tuyển sinh:|Liên hệ:))"

    parts = re.split(pattern, raw_text)
    data = {}

    current_key = None
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Nếu là tiêu đề
        if part.rstrip(":") in keyword_map:
            current_key = keyword_map[part.rstrip(":")]
            data[current_key] = ""
        # Nếu là nội dung
        else:
            if current_key:
                # Ghép nội dung vào key hiện tại
                data[current_key] += part.strip() + " "

    # Xóa trường tuyển sinh
    if "tuyen_sinh" in data:
        del data["tuyen_sinh"]

    # Chuẩn hóa khoảng trắng
    for k in data:
        data[k] = re.sub(r"\s+", " ", data[k]).strip()

    return data


# === Ví dụ chạy thử ===
if __name__ == "__main__":
    with open("data_raw.txt", "r", encoding="utf-8") as f:  # file chứa đoạn text bạn gửi
        raw_text = f.read()

    result = clean_text(raw_text)

    # Xuất ra JSON
    with open("data_clean.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("✅ Đã xử lý và lưu vào data_clean.json")
