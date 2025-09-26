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


def format_ma_cn(ma_cn: str) -> str:
    """Format mã CN thành dạng compact: 116 (CMU) -> 116CMU"""
    if not ma_cn:
        return ""
    
    # Remove spaces and parentheses, keep only letters and numbers
    formatted = re.sub(r'[\s\(\)]', '', ma_cn.strip())
    return formatted


def parse_structured_data(raw_text: str) -> dict:
    """Parse dữ liệu thành cấu trúc ngành -> chuyên ngành."""
    
    # Tìm tất cả các pattern "Ngành ... Mã ngành: XXX"
    nganh_pattern = r'Ngành\s+(.+?)\s*-\s*Mã ngành:\s*(\d+)'
    
    nganh_matches = list(re.finditer(nganh_pattern, raw_text, re.IGNORECASE))
    
    if not nganh_matches:
        print("Không tìm thấy ngành nào!")
        return {"nganh": []}
    
    result = {"nganh": []}
    
    # Xử lý từng ngành
    for i, nganh_match in enumerate(nganh_matches):
        ten_nganh = nganh_match.group(1).strip()
        ma_nganh = nganh_match.group(2).strip()
        
        # Tìm vị trí bắt đầu và kết thúc của ngành này
        start_pos = nganh_match.start()
        
        if i + 1 < len(nganh_matches):
            end_pos = nganh_matches[i + 1].start()
        else:
            end_pos = len(raw_text)
        
        # Lấy text của ngành này
        nganh_text = raw_text[start_pos:end_pos]
        
        # Tìm tất cả chuyên ngành trong text này
        chuyen_nganh_list = find_chuyen_nganh_in_text(nganh_text, ten_nganh, ma_nganh)
        
        # Mỗi chuyên ngành tạo thành một object riêng biệt với keys chuẩn
        for chuyen_nganh_data in chuyen_nganh_list:
            nganh_obj = {
                "Ngành": ten_nganh,
                "Mã Ngành": ma_nganh,
                "Chuyên Ngành": chuyen_nganh_data["Tên"],
                "Mã CN": chuyen_nganh_data["Mã CN"],
                **{k: v for k, v in chuyen_nganh_data.items() if k not in ["Tên", "Mã CN"]}
            }
            result["nganh"].append(nganh_obj)
    
    return result


def find_chuyen_nganh_in_text(nganh_text: str, ten_nganh: str, ma_nganh: str) -> list:
    """Tìm tất cả chuyên ngành trong text của một ngành."""
    
    # Patterns để tìm chuyên ngành - Cải thiện để tránh lấy thêm text
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
        print(f"Không tìm thấy chuyên ngành nào trong ngành {ten_nganh}")
        return []
    
    result = []
    
    # Xử lý từng chuyên ngành
    for i, match in enumerate(chuyen_nganh_matches):
        ten_chuyen_nganh = match.group(1).strip()
        ma_chuyen_nganh = match.group(2).strip()
        
        # Format mã CN thành dạng compact
        ma_chuyen_nganh_formatted = format_ma_cn(ma_chuyen_nganh)
        
        # Tìm nội dung của chuyên ngành này
        content_start = match.end()
        
        # Tìm điểm kết thúc (trước chuyên ngành tiếp theo hoặc cuối text)
        if i + 1 < len(chuyen_nganh_matches):
            content_end = chuyen_nganh_matches[i + 1].start()
        else:
            # Tìm điểm kết thúc khác (ngành mới, hoặc cuối text)
            next_nganh = re.search(r'Ngành\s+.+?\s*-\s*Mã ngành:', nganh_text[content_start:], re.IGNORECASE)
            if next_nganh:
                content_end = content_start + next_nganh.start()
            else:
                content_end = len(nganh_text)
        
        # Lấy nội dung
        content_text = nganh_text[content_start:content_end].strip()
        
        # Parse các field content
        content_fields = parse_content_fields(content_text)
        
        # Tạo object chuyên ngành với keys có dấu viết hoa
        chuyen_nganh_obj = {
            "Tên": ten_chuyen_nganh,
            "Mã CN": ma_chuyen_nganh_formatted,
            **content_fields
        }
        
        # Xóa các trường không cần thiết
        fields_to_remove = ["Tuyển Sinh", "Liên Hệ"]
        for field in fields_to_remove:
            if field in chuyen_nganh_obj:
                del chuyen_nganh_obj[field]
        
        result.append(chuyen_nganh_obj)
        print(f"  ✅ Tìm thấy chuyên ngành: {ten_chuyen_nganh} ({ma_chuyen_nganh} -> {ma_chuyen_nganh_formatted})")
    
    return result


def parse_content_fields(content_text: str) -> dict:
    """Parse các field: Giới thiệu, Mục tiêu, Chương trình, etc."""
    
    keyword_map = {
        "Giới thiệu:": "Giới Thiệu",
        "Mục tiêu:": "Mục Tiêu",
        "Chương trình:": "Chương Trình", 
        "Cơ hội:": "Cơ Hội",
        "Liên hệ:": "Liên Hệ",
        "Tuyển sinh:": "Tuyển Sinh"
    }
    
    result = {}
    
    # Normalize content first
    content_text = re.sub(r'\n+', ' ', content_text)  # Replace multiple newlines with space
    content_text = re.sub(r'\s+', ' ', content_text)  # Normalize whitespace
    
    # Tạo pattern để tìm tất cả sections
    all_keywords = list(keyword_map.keys())
    
    # Tìm positions của tất cả keywords
    keyword_positions = []
    for keyword in all_keywords:
        pattern = rf'\b{re.escape(keyword)}[:\s]'
        for match in re.finditer(pattern, content_text, re.IGNORECASE):
            keyword_positions.append((match.start(), match.end(), keyword))
    
    # Sort theo position
    keyword_positions.sort()
    
    # Extract content cho từng keyword
    for i, (start, end, keyword) in enumerate(keyword_positions):
        # Tìm điểm kết thúc cho keyword này
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
    
    # Handle special cases for "Liên hệ"
    if keyword == "Liên hệ:":
        return format_contact_info(text)
    
    # Truncate if text is too long and seems to contain next section
    if len(text) > 1000:
        # Look for signs of next section
        for next_keyword in ["Ngành", "Chuyên ngành", "Website:", "Email:", "Điện thoại:"]:
            pos = text.find(next_keyword)
            if pos > 100:  # Only truncate if found after reasonable content
                text = text[:pos].strip()
                break
    
    return text.strip()


def format_contact_info(text: str) -> str:
    """Format lại thông tin liên hệ."""
    # Extract contact details
    website_match = re.search(r'Website:\s*([^\s\n]+)', text, re.IGNORECASE)
    email_match = re.search(r'Email:\s*([^\s\n]+)', text, re.IGNORECASE)
    phone_match = re.search(r'Điện thoại:\s*([^\n\r]+?)(?=\s*(?:Ngành|Chuyên ngành|$))', text, re.IGNORECASE)
    
    if not (website_match or email_match or phone_match):
        return text.strip()
    
    formatted_parts = []
    if website_match:
        formatted_parts.append(f"Website: {website_match.group(1)}")
    if email_match:
        formatted_parts.append(f"Email: {email_match.group(1)}")
    if phone_match:
        phone_text = phone_match.group(1).strip()
        phone_text = re.sub(r'\s*–\s*', ' - ', phone_text)  # Normalize dashes
        formatted_parts.append(f"Điện thoại: {phone_text}")
    
    return " | ".join(formatted_parts)


if __name__ == "__main__":
    files = [
        "TRƯỜNG CÔNG NGHỆ.docx",
        "KHOA ĐTQT.docx",
        "TRƯỜNG DU LỊCH.docx", 
        "TRƯỜNG KHMT.docx",
        "TRƯỜNG KINH TẾ&KINH DOANH.docx",
        "TRƯỜNG NN&XHNV.docx",
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
                all_data[file_key] = result
                
                # Thống kê đúng - mỗi item trong nganh array là 1 chuyên ngành
                total_chuyen_nganh = len(result.get('nganh', []))
                print(f"✅ {file}: {total_chuyen_nganh} chuyên ngành")
            else:
                print(f"⚠️  {file}: No content found")
        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

    # Lưu file JSON
    if all_data:
        with open("mo_ta_nganh.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Đã xử lý và lưu vào mo_ta_nganh_final.json")
        
        # Thống kê tổng đúng
        total_chuyen_nganh = sum(len(school.get('nganh', [])) for school in all_data.values())
        print(f"📊 Tổng cộng: {len(all_data)} trường, {total_chuyen_nganh} chuyên ngành")
    else:
        print("❌ Không có dữ liệu được xử lý thành công")