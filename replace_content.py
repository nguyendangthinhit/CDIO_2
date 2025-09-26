import json

def normalize_code(code):
    """
    Chuẩn hóa mã chuyên ngành: bỏ dấu cách và dấu ngoặc đơn
    """
    if not code:
        return ""
    return str(code).replace(" ", "").replace("(", "").replace(")", "").strip()

def extract_admission_info(data2):
    """
    Trích xuất thông tin tổ hợp xét tuyển từ data_2.json
    Trả về dict với key là mã CN đã chuẩn hóa và value là thông tin tổ hợp xét tuyển
    """
    admission_info = {}
    
    if "chi_tiet_nganh_dtu_2025" in data2:
        chi_tiet_nganh = data2["chi_tiet_nganh_dtu_2025"]
        
        # Duyệt qua từng phần tử trong danh sách
        for item in chi_tiet_nganh:
            if isinstance(item, dict) and "Mã CN" in item and "Tổ hợp xét tuyển" in item:
                ma_cn_raw = item["Mã CN"]
                ma_cn_normalized = normalize_code(ma_cn_raw)
                to_hop_xet_tuyen = item["Tổ hợp xét tuyển"]
                
                # Lưu cả mã gốc và mã chuẩn hóa để debug
                admission_info[ma_cn_normalized] = {
                    "to_hop": to_hop_xet_tuyen,
                    "ma_goc": ma_cn_raw
                }
    
    return admission_info

def add_admission_info_to_majors(mo_ta_nganh_gop, admission_info):
    """
    Thêm thông tin tổ hợp xét tuyển vào các chuyên ngành dựa theo mã CN (so sánh đã chuẩn hóa)
    """
    updated_count = 0
    not_found_count = 0
    not_found_codes = []
    debug_matches = []
    
    for khoa_name, khoa_data in mo_ta_nganh_gop.items():
        if "nganh" in khoa_data:
            for ma_nganh, nganh_info in khoa_data["nganh"].items():
                if "Chuyên Ngành" in nganh_info:
                    for chuyen_nganh in nganh_info["Chuyên Ngành"]:
                        ma_cn_raw = chuyen_nganh.get("Mã CN", "")
                        ma_cn_normalized = normalize_code(ma_cn_raw)
                        
                        if ma_cn_normalized in admission_info:
                            chuyen_nganh["Tổ hợp xét tuyển"] = admission_info[ma_cn_normalized]["to_hop"]
                            updated_count += 1
                            
                            # Debug: lưu thông tin ghép nối
                            debug_matches.append({
                                "ma_cn_goc": ma_cn_raw,
                                "ma_cn_chuan": ma_cn_normalized,
                                "ghep_voi": admission_info[ma_cn_normalized]["ma_goc"],
                                "chuyen_nganh": chuyen_nganh.get("Chuyên Ngành", "")
                            })
                        else:
                            not_found_count += 1
                            if ma_cn_raw and ma_cn_raw not in not_found_codes:
                                not_found_codes.append(ma_cn_raw)
    
    print(f"Đã thêm thông tin tổ hợp xét tuyển cho {updated_count} chuyên ngành")
    if not_found_count > 0:
        print(f"Không tìm thấy thông tin tổ hợp xét tuyển cho {not_found_count} chuyên ngành")
        print(f"Các mã CN không tìm thấy: {not_found_codes}")
    
    # Debug: hiển thị một số ví dụ ghép nối thành công
    if debug_matches:
        print("\n=== VÍ DỤ GHÉP NỐI THÀNH CÔNG (5 đầu tiên) ===")
        for i, match in enumerate(debug_matches[:5]):
            print(f"{i+1}. '{match['ma_cn_goc']}' -> '{match['ma_cn_chuan']}' ghép với '{match['ghep_voi']}' ({match['chuyen_nganh']})")
    
    return mo_ta_nganh_gop

def replace_content_in_data2(data2_file, mo_ta_nganh_gop_file, output_file=None):
    """
    Thay thế phần "chi_tiet_nganh_dtu_2025" trong data_2.json 
    bằng nội dung từ mo_ta_nganh_gop.json (đã bổ sung thông tin tổ hợp xét tuyển)
    
    Args:
        data2_file (str): Đường dẫn file data_2.json
        mo_ta_nganh_gop_file (str): Đường dẫn file mo_ta_nganh_gop.json
        output_file (str, optional): File đầu ra. Nếu None sẽ ghi đè lên data_2.json
    """
    
    # Đọc file data_2.json
    try:
        with open(data2_file, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        print(f"Đã đọc file {data2_file}")
    except FileNotFoundError:
        print(f"Không tìm thấy file {data2_file}")
        return
    except json.JSONDecodeError:
        print(f"File {data2_file} không đúng định dạng JSON")
        return
    
    # Đọc file mo_ta_nganh_gop.json
    try:
        with open(mo_ta_nganh_gop_file, 'r', encoding='utf-8') as f:
            mo_ta_nganh_gop = json.load(f)
        print(f"Đã đọc file {mo_ta_nganh_gop_file}")
    except FileNotFoundError:
        print(f"Không tìm thấy file {mo_ta_nganh_gop_file}")
        return
    except json.JSONDecodeError:
        print(f"File {mo_ta_nganh_gop_file} không đúng định dạng JSON")
        return
    
    # Kiểm tra xem có key "chi_tiet_nganh_dtu_2025" trong data_2 không
    if "chi_tiet_nganh_dtu_2025" not in data2:
        print("Không tìm thấy key 'chi_tiet_nganh_dtu_2025' trong data_2.json")
        print(f"Các key có sẵn: {list(data2.keys())}")
        return
    
    print("\n=== TRÍCH XUẤT THÔNG TIN TỔ HỢP XÉT TUYỂN ===")
    # Trích xuất thông tin tổ hợp xét tuyển từ data_2
    admission_info = extract_admission_info(data2)
    print(f"Đã trích xuất thông tin tổ hợp xét tuyển cho {len(admission_info)} chuyên ngành")
    
    print("\n=== THÊM THÔNG TIN VÀO CHUYÊN NGÀNH ===")
    # Thêm thông tin tổ hợp xét tuyển vào mo_ta_nganh_gop
    mo_ta_nganh_gop_updated = add_admission_info_to_majors(mo_ta_nganh_gop, admission_info)
    
    print("\n=== THAY THẾ NỘI DUNG ===")
    # Thay thế nội dung
    old_content = data2["chi_tiet_nganh_dtu_2025"]
    data2["chi_tiet_nganh_dtu_2025"] = mo_ta_nganh_gop_updated
    
    # Xác định file đầu ra
    if output_file is None:
        output_file = data2_file
    
    # Ghi file kết quả
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data2, f, ensure_ascii=False, indent=2)
        print(f"Đã thay thế nội dung thành công! File kết quả: {output_file}")
    except Exception as e:
        print(f"Lỗi khi ghi file: {e}")
        return
    
    # In thống kê
    print("\n=== THỐNG KÊ THAY ĐỔI ===")
    if isinstance(old_content, list):
        print(f"Nội dung cũ: danh sách có {len(old_content)} phần tử")
    elif isinstance(old_content, dict):
        print(f"Nội dung cũ: dict có {len(old_content)} key")
    else:
        print(f"Nội dung cũ: {type(old_content)}")
    
    if isinstance(mo_ta_nganh_gop_updated, dict):
        total_khoa = len(mo_ta_nganh_gop_updated)
        total_nganh = 0
        total_chuyen_nganh = 0
        total_with_admission = 0
        
        for khoa_name, khoa_data in mo_ta_nganh_gop_updated.items():
            if "nganh" in khoa_data:
                khoa_nganh = len(khoa_data["nganh"])
                total_nganh += khoa_nganh
                
                for nganh_code, nganh_info in khoa_data["nganh"].items():
                    if "Chuyên Ngành" in nganh_info:
                        for chuyen_nganh in nganh_info["Chuyên Ngành"]:
                            total_chuyen_nganh += 1
                            if "Tổ hợp xét tuyển" in chuyen_nganh:
                                total_with_admission += 1
        
        print(f"Nội dung mới: {total_khoa} khoa, {total_nganh} ngành, {total_chuyen_nganh} chuyên ngành")
        print(f"Đã có thông tin tổ hợp xét tuyển: {total_with_admission}/{total_chuyen_nganh} chuyên ngành")
    else:
        print(f"Nội dung mới: {type(mo_ta_nganh_gop_updated)}")

def backup_original_file(original_file):
    """
    Tạo bản sao lưu của file gốc
    """
    backup_file = original_file.replace('.json', '_backup.json')
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Đã tạo bản sao lưu: {backup_file}")
        return True
    except Exception as e:
        print(f"Lỗi khi tạo bản sao lưu: {e}")
        return False

def preview_admission_info(data2_file):
    """
    Xem trước thông tin tổ hợp xét tuyển trong data_2.json
    """
    try:
        with open(data2_file, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        admission_info = extract_admission_info(data2)
        
        print(f"\n=== XEM TRƯỚC THÔNG TIN TỔ HỢP XÉT TUYỂN ===")
        print(f"Tổng số: {len(admission_info)} chuyên ngành có thông tin tổ hợp xét tuyển")
        
        # Hiển thị 5 ví dụ đầu tiên
        count = 0
        for ma_cn, to_hop in admission_info.items():
            if count < 5:
                print(f"Mã CN: {ma_cn} - Tổ hợp: {to_hop}")
                count += 1
            else:
                break
        
        if len(admission_info) > 5:
            print("...")
            
    except Exception as e:
        print(f"Lỗi khi xem trước: {e}")

# Sử dụng script
if __name__ == "__main__":
    data2_file = "data.json"
    mo_ta_nganh_gop_file = "mo_ta_nganh_gop.json"
    
    # Xem trước thông tin tổ hợp xét tuyển
    preview_admission_info(data2_file)
    
    # Tùy chọn: tạo bản sao lưu trước khi thay thế
    print("\n=== TẠO BẢN SAO LƯU ===")
    backup_success = backup_original_file(data2_file)
    
    # Thực hiện thay thế với thông tin bổ sung
    replace_content_in_data2(data2_file, mo_ta_nganh_gop_file)
    
    # Cách 2: Tạo file mới (uncomment dòng dưới nếu muốn tạo file mới)
    # replace_content_in_data2(data2_file, mo_ta_nganh_gop_file, "data_2_updated.json")