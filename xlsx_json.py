import pandas as pd

def excel_to_json(name, sheet_name=0):
    input_file = f"{name}.xlsx"
    output_file = f"{name}.json"

    # Đọc file Excel
    df = pd.read_excel(input_file, sheet_name=sheet_name)

    # Chuyển thành JSON
    json_str = df.to_json(orient="records", force_ascii=False, indent=4)

    # Lưu ra file JSON
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json_str)

    print(f"Đã chuyển {input_file} → {output_file}")
    return json_str
# files = [
# "chinh_sach_hoc_bong",
# "chi_tiet_nganh_dtu_2025",
# "chuyen_vien_tu_van",
# "chương_trình_đào_tạo_trong_và_sau_đại_học",
# "danh_sach_cac_khu_vuc_tai_cac_tinh_thanh",
# "de_xuat_nganh_hoc_theo_nang_luc_ca_nhan_y_chang",
# "diem_trung_tuyen_theo_cac_phuong_thuc_xet_tuyen",
# "doi_tuong_uu_tien",
# "hoc_phi_full",
# "map_xu_huong_theo_CN_conf40",
# "thong_tin_dai_hoc_duy_tan",
# "truong_khoa_truc_thuoc",
# "xu_huong_viec_lam_2025",
# "de_xuat_viec_lam_theo_nang_luc_va_so_thich"
# ]
files = [
"xu_huong_viec_lam_2025",
"de_xuat_viec_lam_theo_nang_luc_va_so_thich"
]
for file in files:
    excel_to_json(file)
