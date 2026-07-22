# 🚀 Hướng dẫn Deploy lên Render.com

Hướng dẫn chi tiết từng bước để deploy Telegram Task Bot lên Render.com (miễn phí).

## 📋 Yêu cầu trước khi bắt đầu

- ✅ Repository GitHub: https://github.com/rambo247/task_bot
- ✅ Tài khoản Render.com (đăng ký tại https://render.com)
- ✅ Telegram Bot Token (lấy từ @BotFather)

---

## 🎯 Các bước thực hiện

### Bước 1: Đăng nhập Render.com

1. Truy cập: **https://render.com**
2. Click **Get Started** (hoặc **Sign In** nếu đã có tài khoản)
3. Chọn **Sign in with GitHub**
4. Cho phép Render truy cập GitHub của bạn

![Render Login](https://render.com/assets/login-screenshot.png)

---

### Bước 2: Kết nối GitHub Repository

1. Sau khi đăng nhập, click nút **New +** (góc trên bên phải)
2. Chọn **Background Worker**

![New Background Worker](https://render.com/assets/new-service.png)

3. Nếu chưa kết nối GitHub:
   - Click **Connect account** hoặc **Configure account**
   - Chọn **Install** cho tài khoản GitHub của bạn
   - Chọn repository **rambo247/task_bot**

---

### Bước 3: Cấu hình Service

Điền các thông tin sau:

#### **Name**
```
telegram-task-bot
```
(Hoặc tên bạn thích, phải là unique)

#### **Region**
Chọn region gần bạn nhất:
- 🇸🇬 **Singapore** (cho người Việt Nam - khuyến nghị)
- 🇺🇸 **Oregon**
- 🇪🇺 **Frankfurt**

#### **Branch**
```
main
```

#### **Runtime**
```
Python 3
```
(Render tự động detect)

#### **Build Command**
```bash
pip install -r requirements.txt
```

#### **Start Command**
```bash
python task_bot.py
```

#### **Instance Type**
Chọn: **Free** ($0/month)

⚠️ **Lưu ý về Free Plan:**
- Bot sẽ spin down sau 15 phút không hoạt động
- Mất ~30-60 giây để wake up khi có request
- 750 giờ free mỗi tháng (đủ chạy 24/7)

---

### Bước 4: Thêm Environment Variables ⚠️ QUAN TRỌNG!

Scroll xuống đến phần **Environment Variables**:

1. Click **Add Environment Variable**
2. Điền:
   - **Key:** `TELEGRAM_BOT_TOKEN`
   - **Value:** `8802370170:AAEGZU_Df5OnDQTO7kn9lyf2UzeIbbh2KPk`

3. Click **Add**

![Environment Variables](https://render.com/assets/env-vars.png)

**🔐 Bảo mật:** Đừng để token trong code, luôn dùng Environment Variables!

---

### Bước 5: Deploy

1. Kiểm tra lại tất cả thông tin
2. Click nút **Create Background Worker** ở cuối trang
3. Đợi Render deploy (2-3 phút):
   - ⏳ **Building** - Đang cài đặt dependencies
   - 🚀 **Live** - Bot đã chạy thành công!

---

### Bước 6: Kiểm tra Logs

1. Trong dashboard, click vào service vừa tạo
2. Click tab **Logs**
3. Bạn sẽ thấy:

```
🤖 Bot đang chạy...
📱 Bot name: @YourBotUsername
```

✅ Nếu thấy message này → **THÀNH CÔNG!**

---

### Bước 7: Test Bot

1. Mở Telegram
2. Tìm bot của bạn (username bot từ @BotFather)
3. Gửi: `/start`
4. Bot sẽ trả lời với welcome message

```
👋 Xin chào! Tôi là bot nhắc việc của bạn.

📋 Các lệnh hỗ trợ:
/add [Nội dung task] - Thêm công việc mới
/list - Xem danh sách công việc
...
```

✅ **Bot đã hoạt động!** 🎉

---

## 🔧 Troubleshooting

### ❌ Lỗi "Application failed to respond"

**Nguyên nhân:** Bot token không đúng

**Giải pháp:**
1. Kiểm tra token trong Environment Variables
2. Đảm bảo không có space thừa
3. Restart service: Dashboard → **Manual Deploy** → **Deploy latest commit**

---

### ❌ Lỗi "Build failed"

**Nguyên nhân:** Thiếu dependencies

**Giải pháp:**
1. Kiểm tra file `requirements.txt` có trong repository
2. Build Command phải là: `pip install -r requirements.txt`
3. Kiểm tra Python version compatibility

---

### ❌ Bot không phản hồi

**Nguyên nhân:** Service đang sleep (free plan)

**Giải pháp:**
- Đợi 30-60 giây để bot wake up
- Hoặc upgrade lên Paid plan ($7/month) để bot chạy 24/7

---

### ❌ Không tìm thấy repository

**Giải pháp:**
1. Vào **Account Settings** (góc trên phải)
2. Click **GitHub** 
3. Click **Configure GitHub App**
4. Chọn **All repositories** hoặc chọn **task_bot**
5. Click **Save**
6. Quay lại tạo service mới

---

## 📊 Monitoring

### Xem Logs
```
Dashboard → Your Service → Logs
```

### Restart Service
```
Dashboard → Your Service → Manual Deploy → Deploy latest commit
```

### Xem Metrics
```
Dashboard → Your Service → Metrics
- CPU usage
- Memory usage
- Request count
```

---

## 🔄 Cập nhật Code

Khi bạn push code mới lên GitHub:

1. Render sẽ **TỰ ĐỘNG** detect và deploy
2. Hoặc deploy thủ công:
   - Dashboard → **Manual Deploy** → **Deploy latest commit**

---

## 💡 Tips

### Giữ bot luôn wake
Tạo cron job ping bot mỗi 10 phút (để tránh sleep):
- Dùng service như **cron-job.org** hoặc **UptimeRobot**
- Ping endpoint health check (nếu có)

### Upgrade lên Paid Plan
Nếu cần bot chạy 24/7 không sleep:
- Chỉ **$7/month**
- Click **Upgrade** trong dashboard
- Bot sẽ luôn online, không bị restart

### Sao lưu dữ liệu
Bot hiện lưu task trong memory → Restart sẽ mất data

**Giải pháp:** Thêm database (MongoDB, PostgreSQL) - xem CHANGELOG.md

---

## 📞 Hỗ trợ

- 📖 [Render Docs](https://render.com/docs)
- 💬 [Render Community](https://community.render.com/)
- 🐛 [GitHub Issues](https://github.com/rambo247/task_bot/issues)

---

## ✅ Checklist

Đảm bảo đã làm đủ các bước:

- [ ] Đăng nhập Render.com bằng GitHub
- [ ] Tạo Background Worker
- [ ] Chọn repository **rambo247/task_bot**
- [ ] Cấu hình Build Command: `pip install -r requirements.txt`
- [ ] Cấu hình Start Command: `python task_bot.py`
- [ ] Thêm Environment Variable: `TELEGRAM_BOT_TOKEN`
- [ ] Deploy thành công
- [ ] Kiểm tra logs thấy "Bot đang chạy..."
- [ ] Test bot trên Telegram với `/start`

---

🎉 **Chúc mừng! Bot của bạn đã online!** 🤖

Nếu gặp vấn đề, hãy tạo [issue trên GitHub](https://github.com/rambo247/task_bot/issues/new).
