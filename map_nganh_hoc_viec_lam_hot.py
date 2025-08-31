import pandas as pd

# Load dữ liệu
vieclam_df = pd.read_excel("xu_huong_viec_lam_2025_full.xlsx")
dtu_df = pd.read_excel("nganh_hoc_dtu.xlsx")

# Các mã ngành thuộc CNTT, KHMT, KHDL, AI, Mạng
ma_nganh_it = ["7480101", "7480102", "7480103", "7480107", "7460108"]  

# Chuẩn hóa text
def normalize_text(text):
    if pd.isna(text):
        return ""
    return str(text).lower().strip()

# Hàm lấy toàn bộ chuyên ngành theo list mã ngành
def get_chuyen_nganh(ma_list, dtu_df):
    return dtu_df[dtu_df.iloc[:,1].astype(str).isin(ma_list)]

# Rule mapping
def map_nghe_to_nganh(nghe, dtu_df):
    nghe_norm = normalize_text(nghe)

    # Nếu thuộc nhóm CNTT/AI
    if any(key in nghe_norm for key in ["it", "ai", "blockchain", "cybersecurity", "data", "software", "technology"]):
        return get_chuyen_nganh(ma_nganh_it, dtu_df)

    # Nếu thuộc nhóm R&D
    if "r&d" in nghe_norm:
        return get_chuyen_nganh(ma_nganh_it, dtu_df)

    # Nếu Logistics
    if "logistics" in nghe_norm or "supply" in nghe_norm:
        return dtu_df[dtu_df.iloc[:,2].str.contains("Logistics", na=False)]

    # Nếu Marketing / Sales
    if "marketing" in nghe_norm or "sales" in nghe_norm:
        return dtu_df[dtu_df.iloc[:,3].str.contains("Marketing|Truyền thông", na=False)]

    # Nếu HR / tuyển dụng
    if "hr" in nghe_norm or "nhân lực" in nghe_norm or "tuyển dụng" in nghe_norm:
        return dtu_df[dtu_df.iloc[:,3].str.contains("Nhân lực", na=False)]

    # Nếu môi trường / năng lượng
    if "môi trường" in nghe_norm or "năng lượng" in nghe_norm or "green" in nghe_norm:
        return dtu_df[dtu_df.iloc[:,2].str.contains("Môi trường", na=False)]

    # Nếu Luật / Legal
    if "luật" in nghe_norm or "legal" in nghe_norm:
        return dtu_df[dtu_df.iloc[:,2].str.contains("Luật", na=False)]

    # Nếu Quản trị kinh doanh tổng hợp
    if "business" in nghe_norm or "quản trị" in nghe_norm or "kinh doanh" in nghe_norm:
        return dtu_df[dtu_df.iloc[:,2].str.contains("Quản trị Kinh doanh", na=False)]

    # Nếu không match thì trả về rỗng
    return pd.DataFrame(columns=dtu_df.columns)

# Xuất kết quả
results = []
for idx, row in vieclam_df.iterrows():
    matched_df = map_nghe_to_nganh(row["Nghề/ngành hot"], dtu_df)

    if matched_df.empty:
        results.append({
            "Nghề/ngành hot": row["Nghề/ngành hot"],
            "Nhu cầu / Chuyển biến xã hội": row["Nhu cầu / Chuyển biến xã hội"],
            "Mức lương ước tính": row["Mức lương ước tính"],
            "Số liệu tăng trưởng / Tuyển dụng": row["Số liệu tăng trưởng / Tuyển dụng"],
            "Mã CN": "",
            "Tên chuyên ngành": ""
        })
    else:
        for _, nganh in matched_df.iterrows():
            results.append({
                "Nghề/ngành hot": row["Nghề/ngành hot"],
                "Nhu cầu / Chuyển biến xã hội": row["Nhu cầu / Chuyển biến xã hội"],
                "Mức lương ước tính": row["Mức lương ước tính"],
                "Số liệu tăng trưởng / Tuyển dụng": row["Số liệu tăng trưởng / Tuyển dụng"],
                "Mã CN": nganh.iloc[4],   # Mã CN (cột 5 trong file DTU)
                "Tên chuyên ngành": nganh.iloc[3]  # Tên chuyên ngành
            })

# Xuất file Excel
final_df = pd.DataFrame(results)
final_df.to_excel("map_viec_lam_theo_CN.xlsx", index=False)

print("✅ Xuất file thành công: map_viec_lam_theo_CN.xlsx")
