# compare_major_codes.py
# pip install pandas openpyxl unidecode

import pandas as pd
from unidecode import unidecode

# ====== 1) Cấu hình tên file & cột ======
FILE_CHI_TIET = "chi_tiet_nganh_dtu_2025.xlsx"   # chú ý: .xlsx
FILE_HOC_PHI  = "hoc_phi_full.xlsx"

# Tên cột trong file chi_tiet_nganh_dtu_2025.xlsx
COL_CT_MA_CN        = "Mã CN"          # hoặc "Mã Chuyên ngành"
COL_CT_CHUYEN_NGANH = "Chuyên ngành"   # có thể có cả "Ngành", dùng cái này trước
COL_CT_NGANH        = "Ngành"          # phòng hờ nếu cần so sánh theo 'Ngành'

# Tên cột trong file hoc_phi_full.xlsx
COL_HP_MA_CN        = "Mã CN"
COL_HP_CHUYEN_NGANH = "Chuyên ngành"

# ====== 2) Hàm chuẩn hoá ======
def norm_code(x: str) -> str:
    if pd.isna(x): return ""
    # bỏ khoảng trắng, chuyển upper
    return str(x).strip().replace(" ", "").upper()

def norm_text(x: str) -> str:
    if pd.isna(x): return ""
    # bỏ khoảng trắng thừa, về lower, bỏ dấu để so tim-kiem
    t = " ".join(str(x).split()).lower()
    return unidecode(t)  # "Khoa học Dữ liệu" -> "khoa hoc du lieu"

# ====== 3) Đọc & chuẩn hoá dữ liệu ======
ct = pd.read_excel(FILE_CHI_TIET)
hp = pd.read_excel(FILE_HOC_PHI)

# Bảo vệ khi thiếu cột 'Chuyên ngành' ở file chi tiết: fallback dùng 'Ngành'
if COL_CT_CHUYEN_NGANH not in ct.columns and COL_CT_NGANH in ct.columns:
    ct[COL_CT_CHUYEN_NGANH] = ct[COL_CT_NGANH]

# Chỉ giữ cột cần thiết
ct = ct[[COL_CT_MA_CN, COL_CT_CHUYEN_NGANH]].copy()
hp = hp[[COL_HP_MA_CN, COL_HP_CHUYEN_NGANH]].copy()

# Thêm cột chuẩn hoá
ct["MA_CN_NORM"]  = ct[COL_CT_MA_CN].map(norm_code)
hp["MA_CN_NORM"]  = hp[COL_HP_MA_CN].map(norm_code)

ct["NAME_NORM"]   = ct[COL_CT_CHUYEN_NGANH].map(norm_text)
hp["NAME_NORM"]   = hp[COL_HP_CHUYEN_NGANH].map(norm_text)

# Loại dòng trống mã
ct = ct[ct["MA_CN_NORM"] != ""].drop_duplicates(subset=["MA_CN_NORM", "NAME_NORM"])
hp = hp[hp["MA_CN_NORM"] != ""].drop_duplicates(subset=["MA_CN_NORM", "NAME_NORM"])

# ====== 4) Tìm mã có nhiều tên (vi phạm 1–1) trong từng file ======
dups_ct = (ct.groupby("MA_CN_NORM")["NAME_NORM"]
             .nunique().reset_index(name="distinct_names")
             .query("distinct_names > 1"))
dups_hp = (hp.groupby("MA_CN_NORM")["NAME_NORM"]
             .nunique().reset_index(name="distinct_names")
             .query("distinct_names > 1"))

# ====== 5) So khớp theo Mã CN, kiểm tra lệch tên ======
merged = ct.merge(hp,
                  on="MA_CN_NORM",
                  how="outer",
                  suffixes=("_CT", "_HP"))

# Phát hiện các trường hợp:
missing_in_hp = merged[merged[COL_CT_MA_CN].notna() & merged[COL_HP_MA_CN].isna()].copy()
missing_in_ct = merged[merged[COL_CT_MA_CN].isna()  & merged[COL_HP_MA_CN].notna()].copy()

# Mã CN có ở cả 2 nhưng tên khác nhau (so trên NAME_NORM)
name_mismatch = merged[
    merged[COL_CT_MA_CN].notna() &
    merged[COL_HP_MA_CN].notna() &
    (merged["NAME_NORM_CT"] != merged["NAME_NORM_HP"])
].copy()

# ====== 6) Xuất báo cáo ======
with pd.ExcelWriter("doi_soat_maCN.xlsx", engine="openpyxl") as w:
    merged.rename(columns={
        COL_CT_CHUYEN_NGANH: "Chuyên ngành (CT)",
        COL_HP_CHUYEN_NGANH: "Chuyên ngành (HP)",
        COL_CT_MA_CN: "Mã CN (CT)",
        COL_HP_MA_CN: "Mã CN (HP)",
    }).to_excel(w, sheet_name="FULL_MERGE", index=False)

    missing_in_hp[[COL_CT_MA_CN, COL_CT_CHUYEN_NGANH]].to_excel(
        w, sheet_name="CT_thieu_trong_HP", index=False
    )
    missing_in_ct[[COL_HP_MA_CN, COL_HP_CHUYEN_NGANH]].to_excel(
        w, sheet_name="HP_thieu_trong_CT", index=False
    )

    # Hiển thị 2 tên để so sánh
    cols_mismatch = [
        "MA_CN_NORM",
        COL_CT_MA_CN, COL_CT_CHUYEN_NGANH,
        COL_HP_MA_CN, COL_HP_CHUYEN_NGANH
    ]
    name_mismatch[cols_mismatch].to_excel(
        w, sheet_name="Ten_khong_khop", index=False
    )

    # Duplicates (một mã nhiều tên)
    if not dups_ct.empty:
        (ct.merge(dups_ct[["MA_CN_NORM"]], on="MA_CN_NORM"))
        .to_excel(w, sheet_name="CT_maCN_da_ten", index=False)

    if not dups_hp.empty:
        (hp.merge(dups_hp[["MA_CN_NORM"]], on="MA_CN_NORM"))
        .to_excel(w, sheet_name="HP_maCN_da_ten", index=False)

print("✅ Đã xuất báo cáo: doi_soat_maCN.xlsx")
print("– CT_thieu_trong_HP: Mã có ở chi tiết nhưng không có trong học phí")
print("– HP_thieu_trong_CT: Mã có ở học phí nhưng không có trong chi tiết")
print("– Ten_khong_khop: Mã trùng nhưng tên chuyên ngành/ngành khác nhau")
print("– *_maCN_da_ten: cùng một Mã CN nhưng map ra nhiều tên (vi phạm 1–1)")
