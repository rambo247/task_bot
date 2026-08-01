# 🤖 HƯỚNG DẪN SỬ DỤNG AI TỰ ĐỘNG TRẢ LỜI

## 📋 Tổng Quan

Tính năng **AI Auto Response** cho phép bot tự động trả lời câu hỏi của bạn dựa trên:
1. **Dữ liệu đã học** (Knowledge Base) - Câu trả lời chính xác từ dữ liệu bạn nhập
2. **AI thông minh** (GitHub Models) - Tự suy luận khi không có dữ liệu

## ✨ Tính Năng Chính

### 🧠 Knowledge Base (Cơ Sở Dữ Liệu)
- Lưu trữ cặp Câu hỏi - Câu trả lời
- Tìm kiếm thông minh theo từ khóa
- Riêng tư cho từng user
- Không giới hạn số lượng

### 🤖 AI Chat Mode
- Bật/tắt chế độ AI tự động trả lời
- Khi BẬT: Bot trả lời mọi tin nhắn
- Khi TẮT: Bot chỉ xử lý commands và tạo task

### 🔍 Hệ Thống Tìm Kiếm
1. Tìm trong Knowledge Base trước (chính xác 100%)
2. Nếu không tìm thấy → Dùng AI suy luận
3. AI có context từ dữ liệu đã học

## 🎯 Cách Sử Dụng

### Bước 1: Thêm Dữ Liệu Q&A

1. Vào Menu Chính → **🤖 Trợ Lý AI**
2. Chọn **📚 Quản lý kiến thức AI**
3. Nhấn **➕ Thêm dữ liệu Q&A**
4. Nhập câu hỏi (VD: "Địa chỉ văn phòng là gì?")
5. Nhập câu trả lời (VD: "123 Đường ABC, Quận 1, TP.HCM")

**Ví dụ thêm dữ liệu:**
```
Q: Giờ làm việc của công ty?
A: 8:00 - 17:00, Thứ 2 đến Thứ 6

Q: Email liên hệ?
A: contact@company.com

Q: Số điện thoại hỗ trợ?
A: 0123-456-789
```

### Bước 2: Bật AI Chat Mode

1. Vào Menu Chính → **🤖 Trợ Lý AI**
2. Nhấn **🟢 Bật AI Chat**
3. Trạng thái hiển thị: **🟢 BẬT**

### Bước 3: Hỏi Đáp Tự Động

Bây giờ chỉ cần gửi tin nhắn, bot sẽ tự động trả lời!

**Ví dụ:**
```
User: Địa chỉ văn phòng là gì?
Bot: 📚 123 Đường ABC, Quận 1, TP.HCM
     [Từ dữ liệu đã học]

User: Làm sao để đến văn phòng?
Bot: 🤖 Bạn có thể đến văn phòng tại 123 Đường ABC...
     [Từ AI]
```

## 📊 Quản Lý Dữ Liệu

### Xem Danh Sách Q&A
- Menu AI → Quản lý kiến thức → **📋 Xem danh sách**
- Hiển thị tất cả cặp Q&A đã lưu
- Có thể xóa từng cặp

### Xóa Dữ Liệu
- **Xóa 1 cặp:** Chọn 🗑️ trong danh sách
- **Xóa tất cả:** Menu → 🗑️ Xóa tất cả

### Thống Kê
Menu AI hiển thị:
- Số lượng cặp Q&A
- Trạng thái AI Chat Mode
- Trạng thái GitHub AI

## 🔧 Cấu Hình

### Yêu Cầu Tối Thiểu (Chỉ dùng Knowledge Base)
- **Không cần** GitHub Token
- **Không cần** OpenAI Key
- Bot chỉ trả lời từ dữ liệu đã nhập

### Nâng Cao (AI Thông Minh)
Để AI tự suy luận khi không có dữ liệu:

1. **Tạo GitHub Token:**
   - Truy cập: https://github.com/settings/tokens
   - Tạo token mới (classic)
   - Chọn scopes: `repo`, `read:user`
   - Copy token

2. **Cấu hình trong .env:**
   ```env
   GITHUB_TOKEN=your_github_token_here
   ```

3. **Khởi động lại bot**

## 💡 Mẹo Sử Dụng

### 1. Thêm Dữ Liệu Hiệu Quả
- **Câu hỏi rõ ràng:** "Giờ làm việc?" thay vì "Khi nào làm?"
- **Từ khóa chính xác:** Dùng từ mọi người hay hỏi
- **Câu trả lời đầy đủ:** Càng chi tiết càng tốt

### 2. Tối Ưu Tìm Kiếm
Bot tìm kiếm bằng từ khóa, nên:
```
✅ TốT:
Q: giờ làm việc công ty
A: 8h-17h từ thứ 2 đến thứ 6

✅ CÒN TỐT HƠN (nhiều biến thể):
Q: giờ làm việc lịch làm việc work time
A: 8h-17h từ thứ 2 đến thứ 6
```

### 3. Kết Hợp AI
- Dữ liệu cơ bản → Knowledge Base
- Câu hỏi phức tạp → AI suy luận
- AI có context từ Knowledge Base!

### 4. Quản Lý Chat Mode
- **BẬT AI Chat:** Khi cần hỏi đáp nhiều
- **TẮT AI Chat:** Khi cần tập trung vào task

## 📌 Use Cases (Ứng Dụng Thực Tế)

### 1. Bot Hỗ Trợ Khách Hàng
```
Q: Cách đặt hàng?
A: Vào website → Chọn sản phẩm → Thêm vào giỏ → Thanh toán

Q: Chính sách đổi trả?
A: Đổi trả trong 7 ngày, còn nguyên tem mác
```

### 2. Bot Nội Bộ Công Ty
```
Q: Password WiFi văn phòng?
A: CompanyWiFi2024

Q: Quy trình nghỉ phép?
A: Gửi email trước 1 ngày → Chờ approve từ manager
```

### 3. Bot Học Tập
```
Q: Công thức diện tích hình tròn?
A: S = π × r²

Q: Thủ đô của Việt Nam?
A: Hà Nội
```

### 4. Bot Cá Nhân
```
Q: Mật khẩu Netflix?
A: mypassword123

Q: Ngày sinh nhật mẹ?
A: 15/03/1970
```

## 🔒 Bảo Mật & Riêng Tư

### Dữ Liệu Riêng Tư
- Mỗi user có Knowledge Base riêng
- Không ai thấy dữ liệu của bạn
- Dữ liệu lưu trên server bot

### Trong Group Chat
Khi bot trong group:
- Chỉ BẠN thấy menu và dữ liệu của bạn
- Members khác có dữ liệu riêng
- AI Chat Mode riêng cho từng người

### Không Lưu Lịch Sử Chat
- Bot KHÔNG lưu lịch sử hội thoại
- Chỉ lưu Knowledge Base bạn thêm
- Tin nhắn qua AI không được ghi lại

## 🚀 Tính Năng Sắp Có

- [ ] **Import/Export Q&A:** Backup dữ liệu ra file
- [ ] **Nhóm Q&A:** Phân loại theo chủ đề
- [ ] **Học tự động:** Bot tự học từ hội thoại
- [ ] **Multiple languages:** Hỗ trợ đa ngôn ngữ
- [ ] **Voice Q&A:** Hỏi bằng giọng nói

## ❓ Câu Hỏi Thường Gặp

**Q: AI Chat Mode tốn tiền không?**
A: MIỄN PHÍ! GitHub Models API free 100% (có giới hạn rate)

**Q: Có thể thêm bao nhiêu cặp Q&A?**
A: Không giới hạn, tùy bộ nhớ server

**Q: AI trả lời sai thì sao?**
A: Thêm câu trả lời đúng vào Knowledge Base, lần sau sẽ chính xác

**Q: Dữ liệu có mất khi restart bot không?**
A: HIỆN TẠI: Có thể mất (lưu trong RAM)
   SẮP CÓ: Lưu database, không bao giờ mất

**Q: Có thể share Knowledge Base với người khác?**
A: Chưa hỗ trợ, mỗi user phải tự thêm

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Thử tắt/bật lại AI Chat Mode
2. Kiểm tra GitHub Token trong .env
3. Xem log lỗi trong console
4. Liên hệ admin hoặc tạo issue trên GitHub

---

**Tài liệu cập nhật:** 01/08/2026  
**Phiên bản bot:** 2.0.0  
**Tính năng:** AI Auto Response
