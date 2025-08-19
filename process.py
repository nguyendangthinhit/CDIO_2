import pandas as pd

# Đọc file
ct = pd.read_excel("chi_tiet_nganh_dtu_2025.xlsx")
hp = pd.read_excel("hoc_phi_full.xlsx")

# Lấy 2 cột cần so sánh
ct_codes = ct[["Mã CN", "Ngành", "Chuyên ngành"]].dropna()
hp_codes = hp[["Mã CN", "Chuyên ngành"]].dropna()

# Chuẩn hóa mã CN: bỏ khoảng trắng, upper
ct_codes["Mã CN"] = ct_codes["Mã CN"].astype(str).str.strip().str.upper()
hp_codes["Mã CN"] = hp_codes["Mã CN"].astype(str).str.strip().str.upper()

# Tìm khác biệt
ma_ct = set(ct_codes["Mã CN"])
ma_hp = set(hp_codes["Mã CN"])

# Có ở CT nhưng không có ở HP
only_in_ct = ct_codes[ct_codes["Mã CN"].isin(ma_ct - ma_hp)]

# Có ở HP nhưng không có ở CT
only_in_hp = hp_codes[hp_codes["Mã CN"].isin(ma_hp - ma_ct)]

# In kết quả
print("=== Mã có ở chi_tiet nhưng không có ở hoc_phi ===")
print(only_in_ct.to_string(index=False))

print("\n=== Mã có ở hoc_phi nhưng không có ở chi_tiet ===")
print(only_in_hp.to_string(index=False))
