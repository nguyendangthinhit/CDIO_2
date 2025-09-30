import json
import os

# Danh sách các file JSON
files = [
    "thong_tin_tuyen_sinh_DTU_2025.json",
    "chi_tiet_nganh_dtu_2025.json",
    "to_hop_xet_tuyen.json",
    "diem_trung_tuyen_theo_cac_phuong_thuc_xet_tuyen.json",
    "hoc_phi_full.json",
    "chinh_sach_hoc_bong.json",
    "doi_tuong_uu_tien.json",
    "danh_sach_cac_khu_vuc_tai_cac_tinh_thanh.json",
    "de_xuat_viec_lam_theo_nang_luc_va_so_thich.json",
    "de_xuat_nganh_hoc_theo_nang_luc_ca_nhan_y_chang.json",
    "map_xu_huong_theo_CN_conf40.json",
    "chuyen_vien_tu_van.json",
]

merged_data = {}

for file in files:
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print(f"✅ File {file} oke")
            except json.JSONDecodeError:
                print(f"⚠️ File {file} không phải JSON hợp lệ, bỏ qua.")
                continue

            # Lấy tên file không có đuôi .json
            key = os.path.splitext(file)[0]
            merged_data[key] = data
    else:
        print(f"⚠️ File {file} không tồn tại, bỏ qua.")

# Ghi ra file data.json
with open("data_thong_tin_tuyen_sinh.json", "w", encoding="utf-8") as out:
    json.dump(merged_data, out, ensure_ascii=False, indent=4)

print("✅ Đã gộp xong vào data.json")
