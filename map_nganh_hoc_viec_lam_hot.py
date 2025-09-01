import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class JobTrendMapper:
    def __init__(self):
        """
        Khởi tạo AI Tuyển Sinh Job Trend Mapper
        Sử dụng Sentence Transformer để tìm similarity giữa ngành nghề hot và ngành học DTU
        """
        print("🤖 Khởi tạo AI Tuyển Sinh Job Trend Mapper...")
        
        # Load model transformer (multilingual để hỗ trợ tiếng Việt)
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Đã load Sentence Transformer model")
        except Exception as e:
            print(f"⚠️ Không thể load transformer model: {e}")
            print("💡 Sử dụng fallback similarity method")
            self.model = None
        
        # Dữ liệu xu hướng việc làm 2025
        self.job_trends = [
            {
                "nghe": "Technology-driven roles (IT, AI, blockchain, cybersecurity)",
                "nhu_cau": "Chuyển đổi số, AI, blockchain và an ninh mạng phát triển → tạo nhiều việc làm mới, nhu cầu nhân lực thiếu hụt ~30%",
                "luong": "₫37,750,000/tháng (AI/Blockchain Engineer, ~4 năm KN)",
                "tang_truong": "Việc làm AI tăng ~74%/năm tại Mỹ; Machine Learning Engineer tăng ~344% từ 2015–2022",
                "nganh_goi_y": ["CNTT", "Khoa học máy tính", "Trí tuệ nhân tạo", "An toàn thông tin"]
            },
            {
                "nghe": "Green jobs – Năng lượng tái tạo, ESG, môi trường",
                "nhu_cau": "Biến đổi khí hậu, xu hướng năng lượng sạch, doanh nghiệp chú trọng ESG",
                "luong": "₫22,500,000/tháng (trung bình); ₫565M/năm (~₫47M/tháng)",
                "tang_truong": "70% công ty toàn cầu có kế hoạch tuyển green workforce từ 2025",
                "nganh_goi_y": ["Kỹ thuật môi trường", "Công nghệ kỹ thuật năng lượng tái tạo", "Quản lý tài nguyên môi trường"]
            },
            {
                "nghe": "Business/Sales, Marketing/Comms, Customer Service, HR",
                "nhu_cau": "Kinh tế tăng trưởng, nhu cầu kinh doanh – dịch vụ khách hàng cao",
                "luong": "₫8–20M/tháng (entry); >₫50M/tháng (quản lý)",
                "tang_truong": "TopCV: Business/Sales chiếm 47.6% nhu cầu tuyển, tăng 8.3% so với 2024",
                "nganh_goi_y": ["Marketing", "Quản trị kinh doanh", "Truyền thông đa phương tiện", "Quản trị nhân lực"]
            },
            {
                "nghe": "IT/Software",
                "nhu_cau": "Ngành cốt lõi trong nền kinh tế số, thiếu hụt kỹ sư phần mềm lớn",
                "luong": "₫9.7–47.5M/tháng",
                "tang_truong": "Việt Nam thiếu 150.000 lập trình viên/năm",
                "nganh_goi_y": ["CNTT", "Khoa học máy tính", "Kỹ thuật phần mềm"]
            },
            {
                "nghe": "E‑commerce, Logistics, Fintech, IT",
                "nhu_cau": "Thương mại điện tử, tài chính số và logistics bùng nổ",
                "luong": "₫12–25M/tháng",
                "tang_truong": "Nhu cầu nhân lực tăng mạnh nhờ e‑commerce & fintech",
                "nganh_goi_y": ["Logistics & Quản lý chuỗi cung ứng", "Tài chính – Ngân hàng", "Thương mại điện tử", "Công nghệ tài chính"]
            },
            {
                "nghe": "Manufacturing, Processing",
                "nhu_cau": "68% công ty sản xuất mở rộng tại VN → cần nhiều lao động kỹ thuật",
                "luong": "₫8–18M/tháng",
                "tang_truong": "68% công ty sản xuất có kế hoạch tuyển dụng thêm",
                "nganh_goi_y": ["Công nghệ kỹ thuật cơ khí", "Công nghệ chế tạo máy", "Kỹ thuật điện", "Tự động hóa"]
            },
            {
                "nghe": "Renewable Energy emergence",
                "nhu_cau": "Tăng trưởng năng lượng tái tạo, mở rộng tuyển dụng ngành liên quan",
                "luong": "₫20–47M/tháng",
                "tang_truong": "Nhu cầu tăng trưởng cao trong lĩnh vực năng lượng tái tạo",
                "nganh_goi_y": ["Kỹ thuật môi trường", "Công nghệ kỹ thuật năng lượng", "Kỹ thuật điện"]
            },
            {
                "nghe": "AI integration in business/sales, IT, marketing, customer service, HR",
                "nhu_cau": "AI thúc đẩy hiệu quả kinh doanh và dịch vụ → tạo việc làm mới",
                "luong": "AI Engineers: ₫20–50M/tháng + thưởng",
                "tang_truong": "Tuyển dụng AI Engineer tăng 60% trong Q1/2025",
                "nganh_goi_y": ["CNTT", "Quản trị kinh doanh", "Marketing", "Trí tuệ nhân tạo", "Khoa học dữ liệu"]
            },
            {
                "nghe": "Lãnh đạo cấp cao (C-suite, Legal Head, Business Director, Marketing Head)",
                "nhu_cau": "Doanh nghiệp VN thiếu quản lý cấp cao, đặc biệt trong lĩnh vực pháp lý, tài chính, marketing",
                "luong": "Head of Legal ~₫330M/năm; C‑suite ~₫230–490M/năm",
                "tang_truong": "Nhu cầu tăng trưởng 20%/năm cho các vị trí quản lý cấp cao",
                "nganh_goi_y": ["Luật", "Quản trị kinh doanh", "Marketing", "Tài chính ngân hàng"]
            }
        ]
        
    def load_dtu_programs(self, file_path: str) -> pd.DataFrame:
        """
        Load dữ liệu ngành học Đại học Duy Tân từ file Excel/CSV
        """
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                raise ValueError("File phải là .xlsx, .xls hoặc .csv")
            
            print(f"✅ Đã load {len(df)} ngành học từ file: {file_path}")
            return df
        
        except Exception as e:
            print(f"❌ Lỗi khi load file: {e}")
            return None

    def preprocess_text(self, text: str) -> str:
        """
        Tiền xử lý text để cải thiện matching
        """
        if pd.isna(text):
            return ""
        
        # Convert to lowercase và remove special chars
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Normalize một số từ khóa
        replacements = {
            'cntt': 'công nghệ thông tin',
            'it': 'công nghệ thông tin',
            'ai': 'trí tuệ nhân tạo',
            'ml': 'machine learning',
            'iot': 'internet of things'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text

    def calculate_similarity_transformer(self, job_suggestions: List[str], dtu_programs: List[str]) -> np.ndarray:
        """
        Tính similarity sử dụng Sentence Transformer
        """
        if self.model is None:
            return self.calculate_similarity_fallback(job_suggestions, dtu_programs)
        
        try:
            # Encode các text thành vectors
            job_embeddings = self.model.encode(job_suggestions)
            program_embeddings = self.model.encode(dtu_programs)
            
            # Tính cosine similarity
            similarity_matrix = cosine_similarity(
                job_embeddings.reshape(len(job_suggestions), -1),
                program_embeddings.reshape(len(dtu_programs), -1)
            )
            
            return similarity_matrix
            
        except Exception as e:
            print(f"⚠️ Lỗi khi tính similarity với transformer: {e}")
            return self.calculate_similarity_fallback(job_suggestions, dtu_programs)

    def calculate_similarity_fallback(self, job_suggestions: List[str], dtu_programs: List[str]) -> np.ndarray:
        """
        Fallback method: Tính similarity dựa trên keyword matching
        """
        similarity_matrix = np.zeros((len(job_suggestions), len(dtu_programs)))
        
        for i, job in enumerate(job_suggestions):
            job_processed = self.preprocess_text(job)
            job_words = set(job_processed.split())
            
            for j, program in enumerate(dtu_programs):
                program_processed = self.preprocess_text(program)
                program_words = set(program_processed.split())
                
                # Jaccard similarity
                intersection = job_words.intersection(program_words)
                union = job_words.union(program_words)
                
                if len(union) > 0:
                    similarity_matrix[i][j] = len(intersection) / len(union)
        
        return similarity_matrix

    def map_jobs_to_programs(self, dtu_df: pd.DataFrame, threshold: float = 0.3) -> pd.DataFrame:
        """
        Map các ngành nghề hot với ngành học DTU sử dụng AI
        """
        print("🔄 Đang thực hiện mapping với AI...")
        
        # Chuẩn bị dữ liệu DTU programs
        dtu_programs = []
        for _, row in dtu_df.iterrows():
            program_text = f"{row['Ngành']} {row['Chuyên ngành']}"
            dtu_programs.append(self.preprocess_text(program_text))
        
        results = []
        
        for job_trend in self.job_trends:
            print(f"📊 Mapping: {job_trend['nghe'][:50]}...")
            
            # Tính similarity giữa gợi ý ngành và DTU programs  
            job_suggestions_processed = [self.preprocess_text(suggestion) for suggestion in job_trend['nganh_goi_y']]
            similarity_matrix = self.calculate_similarity_transformer(job_suggestions_processed, dtu_programs)
            
            # Tìm matches tốt nhất
            matches = []
            for i, suggestion in enumerate(job_trend['nganh_goi_y']):
                # Lấy top 3 matches cho mỗi gợi ý
                similarities = similarity_matrix[i]
                top_indices = np.argsort(similarities)[::-1][:3]
                
                for idx in top_indices:
                    if similarities[idx] >= threshold:
                        matches.append({
                            'suggestion': suggestion,
                            'dtu_program': dtu_df.iloc[idx],
                            'similarity': similarities[idx]
                        })
            
            # Loại bỏ duplicate và sort theo similarity
            unique_matches = {}
            for match in matches:
                key = (match['dtu_program']['Mã CN'])
                if key not in unique_matches or match['similarity'] > unique_matches[key]['similarity']:
                    unique_matches[key] = match
            
            # Sort và lấy top matches
            sorted_matches = sorted(unique_matches.values(), key=lambda x: x['similarity'], reverse=True)[:5]
            
            # Tạo output
            matched_programs = []
            for match in sorted_matches:
                prog = match['dtu_program']
                matched_programs.append({
                    'chuyen_nganh': prog['Chuyên ngành'],
                    'ma_cn': prog['Mã CN'],
                    'similarity_score': round(match['similarity'], 3),
                    'matched_suggestion': match['suggestion']
                })
            
            results.append({
                'nghe_nganh_hot': job_trend['nghe'],
                'nhu_cau_chuyen_bien': job_trend['nhu_cau'], 
                'muc_luong_uoc_tinh': job_trend['luong'],
                'tang_truong_tuyen_dung': job_trend['tang_truong'],
                'cac_nganh_dtu_phu_hop': matched_programs
            })
        
        return pd.DataFrame(results)

    def export_results(self, results_df: pd.DataFrame, output_path: str = "xu_huong_viec_lam_mapped.xlsx"):
        """
        Xuất kết quả ra file Excel với format đẹp
        """
        print(f"📤 Đang xuất kết quả ra: {output_path}")
        
        # Tạo data cho export với format mới
        export_data = []
        
        for _, row in results_df.iterrows():
            programs = row['cac_nganh_dtu_phu_hop']
            
            if programs:  # Nếu có match
                programs_text = []
                for prog in programs:
                    programs_text.append(f"• {prog['chuyen_nganh']} (Mã: {prog['ma_cn']}) - Độ phù hợp: {prog['similarity_score']}")
                programs_str = "\n".join(programs_text)
            else:
                programs_str = "Chưa tìm thấy ngành phù hợp"
            
            export_data.append({
                'Nghề/ngành hot': row['nghe_nganh_hot'],
                'Nhu cầu / Chuyển biến xã hội': row['nhu_cau_chuyen_bien'],
                'Mức lương ước tính': row['muc_luong_uoc_tinh'],
                'Số liệu tăng trưởng / Tuyển dụng': row['tang_truong_tuyen_dung'],
                'Các ngành DTU phù hợp': programs_str
            })
        
        # Export to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            export_df = pd.DataFrame(export_data)
            export_df.to_excel(writer, sheet_name='Xu_huong_viec_lam_DTU', index=False)
            
            # Adjust column widths
            worksheet = writer.sheets['Xu_huong_viec_lam_DTU']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Đã xuất thành công: {output_path}")
        return output_path

    def generate_summary_report(self, results_df: pd.DataFrame) -> Dict:
        """
        Tạo báo cáo tóm tắt kết quả mapping
        """
        total_trends = len(results_df)
        total_matches = sum(len(row['cac_nganh_dtu_phu_hop']) for _, row in results_df.iterrows())
        
        # Thống kê ngành được match nhiều nhất
        all_programs = []
        for _, row in results_df.iterrows():
            all_programs.extend([p['chuyen_nganh'] for p in row['cac_nganh_dtu_phu_hop']])
        
        from collections import Counter
        top_programs = Counter(all_programs).most_common(5)
        
        summary = {
            'total_job_trends': total_trends,
            'total_matches_found': total_matches,
            'average_matches_per_trend': round(total_matches / total_trends, 2),
            'top_matched_programs': top_programs,
            'coverage_rate': f"{round((total_matches / total_trends) * 100, 1)}% xu hướng có match"
        }
        
        return summary

def main():
    """
    Hàm main để chạy toàn bộ process
    """
    print("🚀 Khởi động AI Tuyển Sinh Job Trend Mapper")
    print("=" * 60)
    
    # Khởi tạo mapper
    mapper = JobTrendMapper()
    
    # Load dữ liệu DTU (thay đổi path theo file thực tế)
    # Có thể dùng dữ liệu bạn cung cấp hoặc file Excel
    print("\n📁 Đang tạo dữ liệu mẫu DTU...")
    
    # Sample data từ dữ liệu bạn cung cấp
    sample_dtu_data = {
        'TT': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'Mã Ngành': ['7480103', '7480103', '7480202', '7480101', '7480101', '7480107', 
                     '7460108', '7460108', '7340101', '7340115', '7340201', '7340404'],
        'Ngành': ['Kỹ thuật Phần mềm', 'Kỹ thuật Phần mềm', 'An toàn Thông tin', 
                 'Khoa học Máy tính', 'Khoa học Máy tính', 'Trí tuệ Nhân tạo',
                 'Khoa học Dữ liệu', 'Khoa học Dữ liệu', 'Quản trị Kinh doanh',
                 'Marketing', 'Tài chính - Ngân hàng', 'Quản trị Nhân lực'],
        'Chuyên ngành': ['Công nghệ Phần mềm', 'Thiết kế Games và Multimedia', 'An toàn Thông tin',
                        'Khoa học Máy tính', 'Kỹ thuật Máy tính', 'Trí tuệ Nhân tạo',
                        'Khoa học Dữ liệu', 'Big Data & Machine Learning', 'Quản trị Kinh doanh Tổng hợp',
                        'Digital Marketing', 'Tài chính Doanh nghiệp', 'Quản trị Nhân lực'],
        'Mã CN': ['102', '122', '124', '130', '128', '121', '135', '115', '400', '402', '403', '417']
    }
    
    dtu_df = pd.DataFrame(sample_dtu_data)
    
    if dtu_df is not None:
        print(f"✅ Đã load {len(dtu_df)} ngành học DTU")
        
        # Thực hiện mapping
        print("\n🤖 Bắt đầu AI mapping process...")
        results = mapper.map_jobs_to_programs(dtu_df, threshold=0.2)
        
        # Xuất kết quả
        print("\n📊 Kết quả mapping:")
        for i, (_, row) in enumerate(results.iterrows(), 1):
            print(f"\n{i}. {row['nghe_nganh_hot'][:60]}...")
            matches = row['cac_nganh_dtu_phu_hop']
            if matches:
                for match in matches[:3]:  # Show top 3
                    print(f"   → {match['chuyen_nganh']} (Mã: {match['ma_cn']}) - Phù hợp: {match['similarity_score']}")
            else:
                print("   → Không tìm thấy ngành phù hợp")
        
        # Export to Excel
        output_file = mapper.export_results(results)
        
        # Tạo báo cáo tóm tắt
        summary = mapper.generate_summary_report(results)
        print(f"\n📋 BÁO CÁO TÓM TẮT:")
        print(f"   • Tổng xu hướng việc làm: {summary['total_job_trends']}")
        print(f"   • Tổng matches tìm được: {summary['total_matches_found']}")
        print(f"   • Trung bình matches/xu hướng: {summary['average_matches_per_trend']}")
        print(f"   • Tỷ lệ coverage: {summary['coverage_rate']}")
        
        print(f"\n🎉 Hoàn thành! File kết quả: {output_file}")
    
    else:
        print("❌ Không thể load dữ liệu DTU")

if __name__ == "__main__":
    # Cài đặt thư viện cần thiết
    print("📦 Cần cài đặt các thư viện sau:")
    print("pip install sentence-transformers pandas openpyxl scikit-learn numpy")
    print("\n" + "="*60)
    
    main()