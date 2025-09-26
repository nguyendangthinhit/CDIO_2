import json
import re

def normalize_ma_cn(ma) -> str:
    """Chuẩn hóa mã CN: ép về str, bỏ dấu ngoặc () và khoảng trắng"""
    ma = str(ma)
    return re.sub(r"[()\s]", "", ma)

# Đọc dữ liệu từ file
with open("chi_tiet_nganh_dtu_2025.json", "r", encoding="utf-8") as f1:
    data1 = json.load(f1)["chi_tiet_nganh_dtu_2025"]

with open("mo_ta_nganh_gop.json", "r", encoding="utf-8") as f2:
    data2 = json.load(f2)

# Tạo mapping mã CN -> thông tin chuyên ngành từ file chi tiết
ma_cn_to_info = {}
for item in data1:
    ma_cn_normalized = normalize_ma_cn(item["Mã CN"])
    ma_cn_to_info[ma_cn_normalized] = {
        "ten_chuyen_nganh": item["Chuyên ngành"],
        "ten_nganh": item["Ngành"],
        "ma_nganh": item["Mã Ngành"]
    }

ma_cn_file1 = set(ma_cn_to_info.keys())

# Lấy tất cả mã CN từ file mo_ta_nganh.json
ma_cn_file2 = set()
for truong in data2.values():
    for nganh in truong["nganh"]:
        ma_cn_file2.add(normalize_ma_cn(nganh["Mã CN"]))

# So sánh
thieu_o_file1 = ma_cn_file2 - ma_cn_file1
thieu_o_file2 = ma_cn_file1 - ma_cn_file2

if thieu_o_file1:
    print("Các mã CN có trong mo_ta_nganh.json nhưng thiếu trong chi_tiet_nganh_dtu_2025.json:", thieu_o_file1)

if thieu_o_file2:
    print(f"Các mã CN có trong chi_tiet_nganh_dtu_2025.json nhưng thiếu trong mo_ta_nganh.json ({len(thieu_o_file2)} mã):")
    print("-" * 80)
    
    # Sắp xếp theo mã CN
    sorted_missing = sorted(thieu_o_file2, key=lambda x: (x.isdigit(), int(x) if x.isdigit() else 0, x))
    
    for ma_cn in sorted_missing:
        info = ma_cn_to_info[ma_cn]
        print(f"  Mã {ma_cn}: {info['ten_chuyen_nganh']} - Ngành: {info['ten_nganh']} ({info['ma_nganh']})")

if not thieu_o_file1 and not thieu_o_file2:
    print("Không thiếu mã CN nào, cả 2 file đều khớp.")

# Thống kê tổng quan
print(f"\nThống kê:")
print(f"- File chi tiết: {len(ma_cn_file1)} mã CN")
print(f"- File mô tả: {len(ma_cn_file2)} mã CN")
print(f"- Chung: {len(ma_cn_file1 & ma_cn_file2)} mã CN")
print(f"- Tỷ lệ hoàn thành: {len(ma_cn_file1 & ma_cn_file2)/len(ma_cn_file1)*100:.1f}%")