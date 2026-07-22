# 🤖 Hướng Dẫn Kích Hoạt AI (GitHub Models)

## ✨ Tính năng AI mới

Bot giờ đã có **AI thông minh** để hiểu ngôn ngữ tự nhiên!

### Ví dụ sử dụng:
```
❌ Trước đây (phức tạp):
   /add Họp team
   Chọn ngày → Chọn giờ 9:00

✅ Bây giờ (đơn giản):
   "Nhắc tôi họp team sáng mai 9h"
   → Bot tự động tạo task + đặt nhắc nhở!
```

### Các câu AI có thể hiểu:
- **"Nhắc tôi họp team sáng mai 9h"** → Task + reminder 9:00 ngày mai
- **"Gọi khách hàng chiều nay 2h"** → Task + reminder 14:00 hôm nay
- **"Nộp báo cáo tối nay"** → Task + reminder 20:00
- **"Mua sữa"** → Chỉ tạo task (không có reminder)

## 🔧 Cách kích hoạt AI

### Bước 1: Tạo GitHub Token (MIỄN PHÍ)

1. Truy cập: https://github.com/settings/tokens
2. Nhấn **"Generate new token"** → **"Generate new token (classic)"**
3. Đặt tên: `Bot AI Token`
4. Chọn scope: **✅ model:inference** (hoặc chọn tất cả nếu không thấy)
5. Nhấn **"Generate token"**
6. **SAO CHÉP TOKEN** (chỉ hiển thị 1 lần!)

### Bước 2: Đặt token vào server

**Trên server CentOS:**
```bash
cd task_bot
nano .env
```

Thêm dòng này (thay YOUR_TOKEN bằng token vừa tạo):
```bash
GITHUB_TOKEN=github_pat_YOUR_TOKEN_HERE
```

Lưu file: `Ctrl+O` → Enter → `Ctrl+X`

### Bước 3: Khởi động lại bot
```bash
pkill -f task_bot.py
nohup python3 task_bot.py > bot.log 2>&1 &
```

## ✅ Kiểm tra AI đã hoạt động

Gửi tin nhắn cho bot:
```
Nhắc tôi họp team sáng mai 9h
```

Nếu thấy: **"✅ Đã thêm... 🤖 Phân tích bởi AI"** → Thành công! 🎉

## 💡 Lưu ý

- **GitHub Models hoàn toàn MIỄN PHÍ** (có giới hạn rate)
- Không cần thẻ tín dụng
- AI model: `gpt-4o-mini` (nhanh + chính xác)
- Nếu không có token → Bot vẫn hoạt động bình thường (không có AI)

## 🆘 Gặp lỗi?

**Lỗi API 401 Unauthorized:**
→ Token sai hoặc hết hạn. Tạo token mới.

**Lỗi API 429 Rate Limit:**
→ Đã dùng hết giới hạn miễn phí. Đợi 1 tiếng hoặc nâng cấp GitHub account.

**Bot không phản hồi AI:**
→ Kiểm tra file `.env` có đúng format không.
