# 🤖 Telegram Task Bot

Bot Telegram quản lý công việc đơn giản và tiện lợi, giúp bạn theo dõi các task hàng ngày.

## ✨ Tính năng

- ➕ Thêm công việc mới
- ⏰ **Đặt nhắc nhở theo giờ** (MỚI!)
- 📝 Xem danh sách công việc
- ✅ Đánh dấu công việc hoàn thành
- 🗑️ Xóa công việc cụ thể
- 🧹 Xóa toàn bộ danh sách (có xác nhận)
- 💾 Lưu trữ riêng biệt cho từng người dùng
- 🔔 Tự động gửi thông báo khi đến giờ nhắc

## 📋 Yêu cầu

- Python 3.7 trở lên
- Telegram Bot Token (lấy từ [@BotFather](https://t.me/BotFather))

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/rambo247/task_bot.git
cd task_bot
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình Bot Token

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Mở file `.env` và thay thế `your_bot_token_here` bằng token của bạn:

```
TELEGRAM_BOT_TOKEN=your_actual_bot_token
```

### 4. Chạy bot

```bash
python task_bot.py
```

## 📱 Cách sử dụng

### Các lệnh cơ bản:

- `/start` - Bắt đầu sử dụng bot
- `/help` - Xem hướng dẫn chi tiết
- `/add [nội dung]` - Thêm công việc mới
  - Ví dụ: `/add Họp lúc 9h sáng`
- `/remind [số thứ tự] [thời gian]` - Đặt nhắc nhở ⏰ **MỚI!**
  - Ví dụ: `/remind 1 14:30`
  - Ví dụ: `/remind 1 30m` (sau 30 phút)
  - Ví dụ: `/remind 1 2026-07-23 09:00`
- `/list` - Xem danh sách công việc
- `/done [số thứ tự]` - Đánh dấu hoàn thành
  - Ví dụ: `/done 1`
- `/delete [số thứ tự]` - Xóa một công việc
  - Ví dụ: `/delete 2`
### Thêm task và đặt nhắc nhở

```
User: /add Họp với khách hàng
Bot: ✅ Đã thêm công việc: 'Họp với khách hàng'
     💡 Đặt nhắc nhở với: /remind 1 [thời gian]

User: /remind 1 14:30
Bot: ⏰ Đã đặt nhắc nhở!
     📌 Công việc: Họp với khách hàng
     🕐 Thời gian: 22/07/2026 14:30
```

**Vào 14:30, bot tự động gửi:**
```
⏰ NHẮC NHỞ!

📌 Họp với khách hàng
```

### Quản lý nhiều task

```
User: /add Mua sữa
Bot: ✅ Đã thêm công việc: 'Mua sữa'

User: /add Làm bài tập
Bot: ✅ Đã thêm công việc: 'Làm bài tập'

User: /remind 1 18:00
Bot: ⏰ Đã đặt nhắc nhở! ...

User: /remind 2 2h
Bot: ⏰ Đã đặt nhắc nhở! (sau 2 giờ)

User: /list
Bot: 📋 Danh sách công việc:

1. ⏳ Mua sữa
   ⏰ Nhắc lúc: 22/07/2026 18:00
2. ⏳ Làm bài tập
   ⏰ Nhắc lúc: 22/07/2026 17:30

User: /done 1
Bot: ✅ Đã đánh dấu hoàn thành: 'Mua sữa'

User: /list
Bot: 📋 Danh sách công việc:

1. ✅ Mua sữa
   ⏰ Nhắc lúc: 22/07/2026 18:00
2. ⏳ Làm bài tập
   ⏰ Nhắc lúc: 22/07/2026 17:30
```

### Các định dạng thời gian hỗ trợ

```
/remind 1 14:30              # Hôm nay lúc 14:30
/remind 1 2026-07-23 09:00   # Ngày giờ cụ thể
/remind 1 30m                # Sau 30 phút
/remind 1 2h                 # Sau 2 giờ
```

📖 **Xem hướng dẫn chi tiết:** [REMINDER_GUIDE.md](REMINDER_GUIDE.md): 📋 Danh sách công việc:

1. ✅ Mua sữa
2. ⏳ Làm bài tập
```

## 🔧 Triển khai (Deployment)

### Deploy lên Heroku

1. Tạo file `Procfile`:
```
worker: python task_bot.py
```

2. Push lên Heroku:
```bash
heroku create your-app-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token_here
git push heroku main
heroku ps:scale worker=1
```

### Deploy lên VPS

1. Clone repository về VPS
2. Cài đặt dependencies
3. Sử dụng `screen` hoặc `tmux` để chạy bot:
```bash
screen -S taskbot
python task_bot.py
# Ctrl+A, D để detach
```

Hoặc sử dụng systemd service để chạy tự động.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo pull request hoặc mở issue nếu bạn có ý tưởng cải thiện.

## 📝 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## � Quick Deploy lên Render.com

Xem hướng dẫn chi tiết tại: [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

**Tóm tắt:**
1. Đăng nhập [Render.com](https://render.com) bằng GitHub
2. Tạo **Background Worker** từ repo này
3. Thêm Environment Variable: `TELEGRAM_BOT_TOKEN`
4. Deploy và test bot!

## 👨‍💻 Tác giả

Tạo bởi **Lương Văn Hiếu** ([@rambo247](https://github.com/rambo247))

## 📧 Liên hệ

- GitHub: [@rambo247](https://github.com/rambo247)
- Repository: [github.com/rambo247/task_bot](https://github.com/rambo247/task_bot)

---

⭐ Nếu bạn thấy project hữu ích, hãy cho một star nhé!
