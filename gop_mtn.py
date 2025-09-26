import json
from collections import defaultdict

def group_majors_by_code(input_file, output_file):
    """
    Gộp các chuyên ngành có cùng mã ngành thành một tập hợp
    
    Args:
        input_file (str): Đường dẫn file JSON đầu vào
        output_file (str): Đường dẫn file JSON đầu ra
    """
    
    # Đọc dữ liệu từ file JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tạo cấu trúc dữ liệu mới
    grouped_data = {}
    
    # Duyệt qua từng trường/khoa
    for khoa_name, khoa_data in data.items():
        # Sử dụng mã ngành làm key
        grouped_majors = {}
        
        # Duyệt qua từng ngành trong khoa
        for i, nganh_info in enumerate(khoa_data["nganh"]):
            try:
                nganh_name = nganh_info.get("Ngành", "")
                ma_nganh = nganh_info.get("Mã Ngành", "")
                
                if not ma_nganh:
                    print(f"Cảnh báo: Thiếu mã ngành tại khoa {khoa_name}, record {i+1}")
                    continue
                
                # Nếu mã ngành chưa tồn tại trong grouped_majors, tạo mới
                if ma_nganh not in grouped_majors:
                    grouped_majors[ma_nganh] = {
                        "Ngành": nganh_name,
                        "Mã Ngành": ma_nganh,
                        "Chuyên Ngành": []
                    }
                
                # Thêm chuyên ngành vào danh sách
                chuyen_nganh_info = {
                    "Chuyên Ngành": nganh_info.get("Chuyên Ngành", ""),
                    "Mã CN": nganh_info.get("Mã CN", ""),
                    "Giới Thiệu": nganh_info.get("Giới Thiệu", ""),
                    "Mục Tiêu": nganh_info.get("Mục Tiêu", ""),
                    "Chương Trình": nganh_info.get("Chương Trình", ""),
                    "Cơ Hội": nganh_info.get("Cơ Hội", "")
                }
                
                grouped_majors[ma_nganh]["Chuyên Ngành"].append(chuyen_nganh_info)
                
            except Exception as e:
                print(f"Lỗi tại khoa {khoa_name}, ngành thứ {i+1}: {e}")
                print(f"Keys có sẵn: {list(nganh_info.keys()) if isinstance(nganh_info, dict) else 'Không phải dict'}")
                continue
        
        # Lưu vào cấu trúc chính
        grouped_data[khoa_name] = {
            "nganh": grouped_majors
        }
    
    # Ghi dữ liệu ra file mới
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(grouped_data, f, ensure_ascii=False, indent=2)
    
    print(f"Đã gộp dữ liệu thành công! File kết quả: {output_file}")
    
    # In thống kê
    print("\n=== THỐNG KÊ ===")
    total_majors = 0
    total_specializations = 0
    
    for khoa_name, khoa_data in grouped_data.items():
        print(f"\n{khoa_name}:")
        khoa_majors = 0
        khoa_specializations = 0
        
        for ma_nganh, nganh_info in khoa_data["nganh"].items():
            so_chuyen_nganh = len(nganh_info["Chuyên Ngành"])
            print(f"  - {nganh_info['Ngành']} (Mã: {ma_nganh}): {so_chuyen_nganh} chuyên ngành")
            khoa_majors += 1
            khoa_specializations += so_chuyen_nganh
        
        print(f"    Tổng: {khoa_majors} ngành, {khoa_specializations} chuyên ngành")
        total_majors += khoa_majors
        total_specializations += khoa_specializations
    
    print(f"\n=== TỔNG KẾT ===")
    print(f"Tổng cộng: {total_majors} ngành, {total_specializations} chuyên ngành")

# Sử dụng script
if __name__ == "__main__":
    input_file = "mo_ta_nganh.json"  # File gốc của bạn
    output_file = "mo_ta_nganh_gop.json"  # File kết quả
    
    try:
        group_majors_by_code(input_file, output_file)
    except FileNotFoundError:
        print(f"Không tìm thấy file {input_file}")
        print("Vui lòng đảm bảo file JSON tồn tại trong cùng thư mục với script này.")
    except json.JSONDecodeError:
        print(f"File {input_file} không đúng định dạng JSON")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")