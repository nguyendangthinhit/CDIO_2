import json
import os

# Danh sách các file JSON
files = [
    "chinh_sach_hoc_bong.json",
    "chi_tiet_nganh_dtu_2025.json",
    "chuyen_vien_tu_van.json",
    "chương_trình_đào_tạo_trong_và_sau_đại_học.json",
    "danh_sach_cac_khu_vuc_tai_cac_tinh_thanh.json",
    "de_xuat_nganh_hoc_theo_nang_luc_ca_nhan_y_chang.json",
    "de_xuat_viec_lam_theo_nang_luc_va_so_thich.json",
    "diem_trung_tuyen_theo_cac_phuong_thuc_xet_tuyen.json",
    "doi_tuong_uu_tien.json",
    "hoc_phi_full.json",
    "map_xu_huong_theo_CN_conf40.json",
    "thong_tin_dai_hoc_duy_tan.json",
    "truong_khoa_truc_thuoc.json",
    "xu_huong_viec_lam_2025.json"
]

merged_data = {}

for file in files:
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ File {file} không phải JSON hợp lệ, bỏ qua.")
                continue

            # Lấy tên file không có đuôi .json
            key = os.path.splitext(file)[0]
            merged_data[key] = data
    else:
        print(f"⚠️ File {file} không tồn tại, bỏ qua.")

# Ghi ra file data.json
with open("data.json", "w", encoding="utf-8") as out:
    json.dump(merged_data, out, ensure_ascii=False, indent=4)

print("✅ Đã gộp xong vào data.json")
