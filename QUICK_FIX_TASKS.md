# 🚀 Hướng Dẫn Nhanh - Sửa Lỗi Không Xem Được Task

## ⚡ TL;DR - Giải Pháp Ngay

```powershell
# Bước 1: Kiểm tra
cd f:\workspace12
python check_tasks.py

# Bước 2: Chạy bot
python task_bot.py

# Bước 3: Trên Telegram
# Gửi: /start
# Nhấn: ➕ Thêm mới
# Nhập task rồi xem danh sách
```

---

## 🎯 Vấn Đề Tìm Ra

✅ **Bot hoạt động tốt**  
✅ **Code không lỗi**  
⚠️ **Chưa có task trong hệ thống**

---

## 💡 Giải Pháp 3 Bước

### Cách 1: Thêm Task Thật (Khuyến Nghị)

1. **Chạy bot:**
   ```powershell
   python task_bot.py
   ```

2. **Trên Telegram:**
   - Gửi `/start`
   - Nhấn "➕ Thêm mới"
   - Nhập: `Họp team 9h`
   - Nhấn "📋 Xem danh sách"

### Cách 2: Test Với Dữ Liệu Mẫu

1. **Chạy bot và lấy User ID:**
   ```powershell
   python task_bot.py
   ```
   Gửi `/start` trên Telegram, xem log:
   ```
   user_id: 123456789
   ```

2. **Thêm task mẫu:**
   ```powershell
   python add_sample_tasks.py 123456789
   ```

3. **Restart bot:**
   ```powershell
   python task_bot.py
   ```

4. **Kiểm tra:**
   Gửi `/list` trên Telegram

---

## 🔍 Các Lệnh Hữu Ích

```powershell
# Kiểm tra dữ liệu
python check_tasks.py

# Thêm 4 task mẫu (thay YOUR_USER_ID)
python add_sample_tasks.py YOUR_USER_ID

# Xem nội dung file task
Get-Content data\user_tasks.json -Encoding UTF8

# Cài đặt dependencies nếu thiếu
pip install pyTelegramBotAPI python-dotenv requests beautifulsoup4 validators
```

---

## ✅ Checklist

- [ ] Chạy `check_tasks.py` ✓
- [ ] Bot đang chạy (`task_bot.py`)
- [ ] Đã gửi `/start`
- [ ] Đã thêm task
- [ ] Đã test `/list`

---

## 📁 Files Đã Tạo

1. **check_tasks.py** - Kiểm tra và sửa lỗi dữ liệu
2. **add_sample_tasks.py** - Thêm task mẫu để test
3. **FIX_TASK_VIEW_GUIDE.md** - Hướng dẫn chi tiết
4. **data/** - Thư mục chứa dữ liệu (đã tạo)

---

## ❓ Câu Hỏi Thường Gặp

**Q: Bot báo "Danh sách trống"?**  
A: Chưa có task, nhấn "➕ Thêm mới"

**Q: Làm sao lấy User ID?**  
A: Gửi `/start`, xem log bot: `user_id: XXX`

**Q: Task không lưu?**  
A: Check log có dòng `✅ Data saved successfully`

**Q: Lỗi import telebot?**  
A: `pip install pyTelegramBotAPI`

---

## 🎉 Kết Quả Mong Đợi

Sau khi làm theo hướng dẫn, gửi `/list` sẽ thấy:

```
📋 DANH SÁCH CÔNG VIỆC:

1. ⏳ Họp team lúc 9h

2. ⏳ Gửi email báo cáo

3. ✅ Hoàn thành dự án

4. ⏳ Đọc tài liệu

[Các nút: ✅ Đánh dấu | ⏰ Nhắc nhở | 🗑️ Xóa]
```

---

Xem thêm chi tiết: **FIX_TASK_VIEW_GUIDE.md** 📖
