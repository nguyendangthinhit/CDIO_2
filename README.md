
# CDIO_2 — Chatbot Tuyển Sinh cho Đại học Duy Tân

## Giới thiệu

Đây là đồ án môn học xây dựng một chatbot tuyển sinh dành cho Đại học Duy Tân. Mục tiêu của dự án là tạo một kênh giao tiếp tự động, thân thiện và phản hồi nhanh cho thí sinh, phụ huynh và người quan tâm, giúp cung cấp thông tin tuyển sinh, chương trình đào tạo, học phí, lịch thi, và các câu hỏi thường gặp.

Chatbot có giao diện người dùng giống Messenger để tạo trải nghiệm quen thuộc cho người dùng. Hệ thống được triển khai dựa trên nền tảng n8n được host trên cloud làm framework orchestration, cho phép thiết kế luồng xử lý, tích hợp API và tự động hoá mà không cần quá nhiều mã nguồn tùy chỉnh.

Kiến trúc xử lý ngữ nghĩa của chatbot sử dụng phương pháp Retrieval-Augmented Generation (RAG) để nạp và truy vấn dữ liệu. Dữ liệu dùng cho RAG được thu thập và cập nhật động thông qua API (bao gồm cả việc kéo dữ liệu từ GitHub) và được tổ chức để chatbot có thể trả lời chính xác, dựa trên nguồn thông tin thực tế.

Dữ liệu đầu vào được tổng hợp từ nhiều nguồn:
- Nội dung chính thức và tư liệu từ thầy cô, phòng tuyển sinh.
- Thông tin công khai trên website trường và các trang liên quan.
- Nội dung và phản hồi từ mạng xã hội (kênh tuyển sinh, nhóm, fanpage) để bắt kịp các câu hỏi thường gặp và xu hướng người quan tâm.

### Điểm nổi bật
- Giao diện: dạng Messenger thân thiện, dễ tiếp cận.
- Framework orchestration: n8n chạy trên cloud để quản lý luồng dữ liệu và tích hợp API.
- Kiến trúc thông minh: RAG giúp kết hợp nguồn tri thức tĩnh và dữ liệu thời gian thực, cải thiện độ chính xác câu trả lời.
- Nguồn dữ liệu đa dạng: tổng hợp từ thầy cô, website, mạng xã hội và GitHub.

### Mục tiêu đồ án
- Xây dựng prototype chatbot có thể trả lời các câu hỏi tuyển sinh phổ biến.
- Thiết kế pipeline thu thập dữ liệu tự động và cập nhật cho mô hình RAG.
- Triển khai demo với UI Messenger và backend vận hành bằng n8n trên cloud.

---

Phần tiếp theo trong README có thể bao gồm: Hướng dẫn cài đặt & chạy nhanh, Kiến trúc chi tiết, Mô tả các luồng n8n, Cách nạp & làm mới dữ liệu từ GitHub/API, và Hướng dẫn đóng góp. Nếu bạn muốn, mình sẽ soạn tiếp các mục này theo cấu trúc chi tiết (cài đặt, cấu hình cloud, cách tạo credentials cho n8n, cấu trúc data ingestion, v.v.). 
