import re
import json
import sys
import subprocess

# Thử import, nếu chưa có thì cài
try:
    from docx import Document
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    from docx import Document


def read_docx(path: str) -> str:
    """Đọc toàn bộ nội dung từ file .docx thành chuỗi text."""
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def normalize_nganh_name(ten_nganh: str) -> str:
    """Chuẩn hóa tên ngành: viết hoa chữ cái đầu mỗi từ chính và xóa từ 'Ngành' thừa"""
    # Xóa từ "Ngành" thừa nếu xuất hiện 2 lần
    # Pattern: tìm "Ngành" + space + "Ngành"
    ten_nganh = re.sub(r'\bNgành\s+Ngành\b', 'Ngành', ten_nganh, flags=re.IGNORECASE)
    
    # Danh sách từ không viết hoa
    lowercase_words = {'và', 'của', '-'}
    
    words = ten_nganh.split()
    normalized = []
    
    for i, word in enumerate(words):
        # Giữ nguyên dấu gạch ngang
        if word == '-':
            normalized.append(word)
        # Từ đầu tiên luôn viết hoa
        elif i == 0:
            normalized.append(word.capitalize())
        # Các từ đặc biệt giữ nguyên chữ thường
        elif word.lower() in lowercase_words:
            normalized.append(word.lower())
        # Các từ khác viết hoa chữ cái đầu
        else:
            normalized.append(word.capitalize())
    
    return ' '.join(normalized)


def parse_structured_data(raw_text: str) -> dict:
    """Parse dữ liệu thành cấu trúc, gộp theo mã ngành."""
    
    # Tìm tất cả các pattern "Ngành ... Mã ngành: XXX"
    nganh_pattern = r'Ngành\s+(.+?)\s*-\s*Mã ngành:\s*(\d+)'
    
    nganh_matches = list(re.finditer(nganh_pattern, raw_text, re.IGNORECASE))
    
    if not nganh_matches:
        print("Không tìm thấy ngành nào!")
        return {}
    
    # Dictionary để lưu tạm theo mã ngành
    temp_dict = {}
    
    # Xử lý từng ngành
    for i, nganh_match in enumerate(nganh_matches):
        ten_nganh = nganh_match.group(1).strip()
        ma_nganh = nganh_match.group(2).strip()
        
        # Chuẩn hóa tên ngành
        ten_nganh_normalized = normalize_nganh_name(ten_nganh)
        
        # Tìm vị trí bắt đầu và kết thúc của ngành này
        start_pos = nganh_match.start()
        
        if i + 1 < len(nganh_matches):
            end_pos = nganh_matches[i + 1].start()
        else:
            end_pos = len(raw_text)
        
        # Lấy text của ngành này
        nganh_text = raw_text[start_pos:end_pos]
        
        # Tìm tất cả chuyên ngành trong text này
        chuyen_nganh_list = find_chuyen_nganh_in_text(nganh_text, ten_nganh_normalized, ma_nganh)
        
        # Gộp theo mã ngành
        if chuyen_nganh_list:
            if ma_nganh not in temp_dict:
                temp_dict[ma_nganh] = {
                    'ten_nganh': ten_nganh_normalized,
                    'chuyen_nganh': []
                }
            
            temp_dict[ma_nganh]['chuyen_nganh'].extend(chuyen_nganh_list)
    
    # Chuyển từ dict tạm sang dict cuối cùng với key là tên ngành
    result = {}
    for ma_nganh, data in temp_dict.items():
        ten_nganh = data['ten_nganh']
        # Xóa chữ "Ngành" ở đầu nếu có (vì sẽ thêm lại sau)
        ten_nganh = re.sub(r'^Ngành\s+', '', ten_nganh, flags=re.IGNORECASE)
        nganh_key = f"Ngành {ten_nganh}"
        result[nganh_key] = data['chuyen_nganh']
    
    return result


def find_chuyen_nganh_in_text(nganh_text: str, ten_nganh: str, ma_nganh: str) -> list:
    """Tìm tất cả chuyên ngành trong text của một ngành."""
    
    # Patterns để tìm chuyên ngành
    chuyen_nganh_patterns = [
        r'(?:Tên\s+)?Chuyên ngành[:\s]+(.+?)\s*-\s*Mã chuyên ngành[:\s]*([A-Za-z0-9\s\(\)]+?)(?=\s*[:\n]|$)',
        r'Chuyên ngành[:\s]+(.+?)\s*-\s*Mã[:\s]*([A-Za-z0-9\s\(\)]+?)(?=\s*[:\n]|$)'
    ]
    
    chuyen_nganh_matches = []
    
    # Tìm tất cả chuyên ngành trong text
    for pattern in chuyen_nganh_patterns:
        matches = list(re.finditer(pattern, nganh_text, re.IGNORECASE))
        if matches:
            chuyen_nganh_matches = matches
            break
    
    if not chuyen_nganh_matches:
        print(f"  Không tìm thấy chuyên ngành nào trong mã ngành {ma_nganh}")
        return []
    
    result = []
    
    # Xử lý từng chuyên ngành
    for i, match in enumerate(chuyen_nganh_matches):
        ten_chuyen_nganh = match.group(1).strip()
        ma_chuyen_nganh = match.group(2).strip()
        
        # Tìm nội dung của chuyên ngành này
        content_start = match.end()
        
        # Tìm điểm kết thúc
        if i + 1 < len(chuyen_nganh_matches):
            content_end = chuyen_nganh_matches[i + 1].start()
        else:
            next_nganh = re.search(r'Ngành\s+.+?\s*-\s*Mã ngành:', nganh_text[content_start:], re.IGNORECASE)
            if next_nganh:
                content_end = content_start + next_nganh.start()
            else:
                content_end = len(nganh_text)
        
        # Lấy nội dung
        content_text = nganh_text[content_start:content_end].strip()
        
        # Parse các field content
        content_fields = parse_content_fields(content_text)
        
        # Tạo object chuyên ngành - CHỈ GIỮ LẠI Chuyên Ngành và các field content
        chuyen_nganh_obj = {
            "Chuyên Ngành": ten_chuyen_nganh,
            **content_fields
        }
        
        result.append(chuyen_nganh_obj)
        print(f"  ✅ Mã {ma_nganh} - {ten_nganh} - CN: {ten_chuyen_nganh}")
    
    return result


def parse_content_fields(content_text: str) -> dict:
    """Parse các field: Giới thiệu, Mục tiêu, Chương trình, Cơ hội."""
    
    keyword_map = {
        "Giới thiệu:": "Giới Thiệu",
        "Mục tiêu:": "Mục Tiêu",
        "Chương trình:": "Chương Trình", 
        "Cơ hội:": "Cơ Hội"
    }
    
    result = {}
    
    # Normalize content first
    content_text = re.sub(r'\n+', ' ', content_text)
    content_text = re.sub(r'\s+', ' ', content_text)
    
    # Tìm positions của tất cả keywords
    keyword_positions = []
    for keyword in keyword_map.keys():
        pattern = rf'\b{re.escape(keyword)}[:\s]'
        for match in re.finditer(pattern, content_text, re.IGNORECASE):
            keyword_positions.append((match.start(), match.end(), keyword))
    
    # Sort theo position
    keyword_positions.sort()
    
    # Extract content cho từng keyword
    for i, (start, end, keyword) in enumerate(keyword_positions):
        if i + 1 < len(keyword_positions):
            next_start = keyword_positions[i + 1][0]
            section_text = content_text[end:next_start].strip()
        else:
            section_text = content_text[end:].strip()
        
        # Clean section text
        section_text = clean_section_content(section_text, keyword)
        
        if section_text and keyword in keyword_map:
            result[keyword_map[keyword]] = section_text
    
    return result


def clean_section_content(text: str, keyword: str) -> str:
    """Clean và format nội dung của từng section."""
    if not text:
        return ""
    
    # Remove common prefixes
    prefixes_to_remove = [
        "đào tạo:",
        "nghề nghiệp:",
    ]
    
    text_lower = text.lower()
    for prefix in prefixes_to_remove:
        if text_lower.startswith(prefix):
            text = text[len(prefix):].strip()
            break
    
    # Remove bullet points
    text = re.sub(r'^\s*•\s*', '', text, flags=re.MULTILINE)
    
    # Truncate nếu có dấu hiệu của section tiếp theo
    skip_keywords = ["Liên hệ:", "Tuyển sinh:", "Website:", "Email:", "Điện thoại:"]
    for skip_kw in skip_keywords:
        pos = text.find(skip_kw)
        if pos > 0:
            text = text[:pos].strip()
            break
    
    # Truncate if text is too long
    if len(text) > 1000:
        for next_keyword in ["Ngành", "Chuyên ngành"]:
            pos = text.find(next_keyword)
            if pos > 100:
                text = text[:pos].strip()
                break
    
    return text.strip()


if __name__ == "__main__":
    files = [
        "TRƯỜNG CÔNG NGHỆ.docx",
        "KHOA ĐÀO TẠO QUỐC TẾ.docx",
        "TRƯỜNG DU LỊCH.docx", 
        "TRƯỜNG KHOA HỌC MÁY TÍNH.docx",
        "TRƯỜNG KINH TẾ&KINH DOANH.docx",
        "TRƯỜNG NGÔN NGỮ & XÃ HỘI NHÂN VĂN.docx",
        "TRUNG TÂM KT&CN VIỆT-NHẬT.docx",
        "KHOA Y-DƯỢC.docx"
    ]

    all_data = {}

    for file in files:
        try:
            print(f"\n🔍 Processing {file}...")
            text = read_docx(file)
            if text.strip():
                result = parse_structured_data(text)
                file_key = file.replace(".docx", "")
                
                # Chỉ thêm vào nếu có dữ liệu
                if result:
                    all_data[file_key] = result
                    
                    # Đếm số chuyên ngành
                    total_chuyen_nganh = sum(len(v) for v in result.values())
                    print(f"✅ {file}: {len(result)} ngành, {total_chuyen_nganh} chuyên ngành")
            else:
                print(f"⚠️  {file}: No content found")
        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

    # Lưu file JSON
    if all_data:
        with open("mo_ta_nganh.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Đã xử lý và lưu vào mo_ta_nganh.json")
        
        # Thống kê tổng
        total_truong = len(all_data)
        total_nganh = sum(len(school) for school in all_data.values())
        total_chuyen_nganh = sum(
            sum(len(v) for v in school.values()) 
            for school in all_data.values()
        )
        print(f"📊 Tổng cộng: {total_truong} trường, {total_nganh} ngành, {total_chuyen_nganh} chuyên ngành")
    else:
        print("❌ Không có dữ liệu được xử lý thành công")
