import re
import pandas as pd

# Đường dẫn
path_xuhuong = "xu_huong_viec_lam_mapped.xlsx"
path_dtu     = "chi_tiet_nganh_dtu_2025.xlsx"
out_path     = "map_xu_huong_theo_CN_conf40.xlsx"

# 1) Đọc dữ liệu
xu_huong_df = pd.read_excel(path_xuhuong)
dtu_df = pd.read_excel(path_dtu)

# Chuẩn hóa cột Mã CN về string
dtu_df["Mã CN"] = dtu_df["Mã CN"].astype(str).str.strip()

def parse_items(text):
    """
    Phân tích cột 'Các ngành DTU phù hợp' thành list item:
    '• Tên CN (Mã: 128) - Độ phù hợp: 0.623 ...'
    Trả: [{'ten':..., 'ma_cn':..., 'score':...}, ...]
    """
    if pd.isna(text):
        return []
    s = str(text)
    parts = [p.strip() for p in s.split('•') if p.strip()]
    items = []
    for p in parts:
        m_name = re.split(r"\(\s*Mã\s*:", p, maxsplit=1)
        ten = m_name[0].strip()
        ma_cn = ""
        m_code = re.search(r"\(\s*Mã\s*:\s*([^)]+)\)", p)
        if m_code:
            ma_cn = m_code.group(1).strip()
        score = None
        m_score = re.search(r"Độ\s*phù\s*hợp\s*:\s*([0-9]*\.?[0-9]+)", p, flags=re.IGNORECASE)
        if m_score:
            try:
                score = float(m_score.group(1))
            except:
                score = None
        items.append({"ten": ten, "ma_cn": ma_cn, "score": score})
    return items

rows = []

for _, r in xu_huong_df.iterrows():
    items = parse_items(r.get("Các ngành DTU phù hợp", ""))
    # Lọc theo ngưỡng: score>=0.4 (vì score đang là 0..1)
    items = [it for it in items if it["score"] is not None and it["score"] >= 0.40]

    for it in items:
        # Join theo Mã CN nếu có
        matched = dtu_df[dtu_df["Mã CN"].str.strip() == str(it["ma_cn"]).strip()]
        if matched.empty:
            # fallback: join theo Chuyên ngành chứa tên (nếu cần)
            matched = dtu_df[dtu_df["Chuyên ngành"].str.contains(it["ten"], na=False, case=False)]
        
        if matched.empty:
            rows.append({
                "Nghề/ngành hot": r.get("Nghề/ngành hot", ""),
                "Nhu cầu / Chuyển biến xã hội": r.get("Nhu cầu / Chuyển biến xã hội", ""),
                "Mức lương ước tính": r.get("Mức lương ước tính", ""),
                "Số liệu tăng trưởng / Tuyển dụng": r.get("Số liệu tăng trưởng / Tuyển dụng", ""),
                "Ngành học (gợi ý)": it["ten"],
                "Mã Ngành": "",
                "Ngành": "",
                "Chuyên ngành": it["ten"],
                "Mã CN": it["ma_cn"],
                "Tổ hợp xét tuyển": "",
                "Độ khớp (từ nguồn xu_hướng)": round(it["score"]*100, 2)
            })
        else:
            for _, d in matched.iterrows():
                rows.append({
                    "Nghề/ngành hot": r.get("Nghề/ngành hot", ""),
                    "Nhu cầu / Chuyển biến xã hội": r.get("Nhu cầu / Chuyển biến xã hội", ""),
                    "Mức lương ước tính": r.get("Mức lương ước tính", ""),
                    "Số liệu tăng trưởng / Tuyển dụng": r.get("Số liệu tăng trưởng / Tuyển dụng", ""),
                    "Ngành học (gợi ý)": it["ten"],
                    "Mã Ngành": d.get("Mã Ngành", ""),
                    "Ngành": d.get("Ngành", ""),
                    "Chuyên ngành": d.get("Chuyên ngành", ""),
                    "Mã CN": d.get("Mã CN", ""),
                    "Tổ hợp xét tuyển": d.get("Tổ hợp xét tuyển", ""),
                    "Độ khớp (từ nguồn xu_hướng)": round(it["score"]*100, 2)
                })

# Xuất file
out_df = pd.DataFrame(rows)
if not out_df.empty:
    out_df.sort_values(
        ["Nghề/ngành hot", "Ngành học (gợi ý)", "Độ khớp (từ nguồn xu_hướng)"],
        ascending=[True, True, False],
        inplace=True,
    )
out_df.to_excel(out_path, index=False)
