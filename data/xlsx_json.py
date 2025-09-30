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

files = [
    "thong_tin_tuyen_sinh_DTU_2025",
    "chi_tiet_nganh_dtu_2025",
    "to_hop_xet_tuyen",
    "diem_trung_tuyen_theo_cac_phuong_thuc_xet_tuyen",
    "hoc_phi_full",
    "chinh_sach_hoc_bong",
    "doi_tuong_uu_tien",
    "danh_sach_cac_khu_vuc_tai_cac_tinh_thanh.json",
    "de_xuat_viec_lam_theo_nang_luc_va_so_thich",
    "de_xuat_nganh_hoc_theo_nang_luc_ca_nhan_y_chang",
    "map_xu_huong_theo_CN_conf40",
    "chuyen_vien_tu_van",
]

for file in files:
    excel_to_json(file)





