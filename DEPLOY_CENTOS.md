# 🐧 Hướng dẫn Deploy lên CentOS 7

Hướng dẫn chi tiết để deploy Telegram Task Bot lên máy chủ CentOS 7.

---

## 📋 Yêu cầu

- ✅ Máy chủ CentOS 7 với quyền root hoặc sudo
- ✅ Kết nối SSH vào server
- ✅ Repository GitHub: https://github.com/rambo247/task_bot
- ✅ Telegram Bot Token

---

## 🚀 Các bước thực hiện

### BƯỚC 1: Kết nối SSH vào Server

```bash
ssh root@your_server_ip
# Hoặc
ssh your_username@your_server_ip
```

---

### BƯỚC 2: Cài đặt Python 3 và Git

CentOS 7 mặc định có Python 2.7, cần cài Python 3:

```bash
# Cập nhật hệ thống
sudo yum update -y

# Cài đặt EPEL repository
sudo yum install -y epel-release

# Cài đặt Python 3 và pip
sudo yum install -y python3 python3-pip

# Cài đặt Git
sudo yum install -y git

# Kiểm tra phiên bản
python3 --version
pip3 --version
git --version
```

**Kết quả mong đợi:**
```
Python 3.6.8 (hoặc cao hơn)
pip 9.0.3 (hoặc cao hơn)
git version 1.8.3 (hoặc cao hơn)
```

---

### BƯỚC 3: Clone Code từ GitHub

```bash
# Di chuyển đến thư mục home
cd ~

# Clone repository
git clone https://github.com/rambo247/task_bot.git

# Vào thư mục project
cd task_bot

# Kiểm tra file
ls -la
```

**Bạn sẽ thấy các file:**
```
task_bot.py
requirements.txt
README.md
.env.example
...
```

---

### BƯỚC 4: Cài đặt Dependencies

```bash
# Nâng cấp pip
sudo pip3 install --upgrade pip

# Cài đặt các package cần thiết
pip3 install -r requirements.txt

# Hoặc cài từng package nếu có lỗi
pip3 install pyTelegramBotAPI requests
```

**Kiểm tra cài đặt thành công:**
```bash
pip3 list | grep pyTelegramBotAPI
```

---

### BƯỚC 5: Cấu hình Bot Token

```bash
# Tạo file .env từ template
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

**Trong file .env, thay đổi:**
```
TELEGRAM_BOT_TOKEN=8802370170:AAEGZU_Df5OnDQTO7kn9lyf2UzeIbbh2KPk
```

**Lưu file:**
- Nhấn `Ctrl + X`
- Nhấn `Y` để confirm
- Nhấn `Enter`

---

### BƯỚC 6: Test Bot (Chạy thử)

```bash
python3 task_bot.py
```

**Nếu thành công, bạn sẽ thấy:**
```
🤖 Bot đang chạy...
📱 Bot name: @YourBotUsername
```

**Test trên Telegram:**
1. Mở Telegram
2. Tìm bot của bạn
3. Gửi `/start`
4. Bot phải trả lời!

**Dừng bot tạm thời:**
- Nhấn `Ctrl + C`

---

### BƯỚC 7: Chạy Bot 24/7 với Systemd Service (Khuyến nghị)

#### 7.1. Tạo Systemd Service File

```bash
sudo nano /etc/systemd/system/taskbot.service
```

#### 7.2. Thêm nội dung sau vào file:

```ini
[Unit]
Description=Telegram Task Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/task_bot
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /root/task_bot/task_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**⚠️ Lưu ý:** Nếu bạn không dùng user `root`, thay đổi:
- `User=root` → `User=your_username`
- `/root/task_bot` → `/home/your_username/task_bot`

**Lưu file:** `Ctrl + X` → `Y` → `Enter`

#### 7.3. Kích hoạt và chạy service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Kích hoạt service tự động chạy khi boot
sudo systemctl enable taskbot.service

# Khởi động service
sudo systemctl start taskbot.service

# Kiểm tra trạng thái
sudo systemctl status taskbot.service
```

**Kết quả mong đợi:**
```
● taskbot.service - Telegram Task Bot
   Loaded: loaded (/etc/systemd/system/taskbot.service; enabled)
   Active: active (running) since ...
   ...
   🤖 Bot đang chạy...
```

#### 7.4. Các lệnh quản lý service

```bash
# Xem logs
sudo journalctl -u taskbot.service -f

# Dừng bot
sudo systemctl stop taskbot.service

# Khởi động lại bot
sudo systemctl restart taskbot.service

# Xem trạng thái
sudo systemctl status taskbot.service

# Tắt auto-start
sudo systemctl disable taskbot.service
```

---

### BƯỚC 8: Chạy Bot với Screen (Phương án thay thế)

Nếu không muốn dùng systemd, có thể dùng `screen`:

```bash
# Cài đặt screen
sudo yum install -y screen

# Tạo session mới
screen -S taskbot

# Chạy bot
python3 task_bot.py

# Detach khỏi screen (bot vẫn chạy background)
# Nhấn: Ctrl + A, sau đó nhấn D
```

**Quản lý screen:**
```bash
# Xem danh sách screen
screen -ls

# Quay lại screen
screen -r taskbot

# Thoát và dừng bot
# Trong screen, nhấn Ctrl + C để dừng bot
# Sau đó gõ: exit
```

---

## 🔒 Bảo mật

### 1. Tạo user riêng cho bot (Khuyến nghị)

```bash
# Tạo user mới
sudo useradd -m -s /bin/bash botuser

# Chuyển quyền sở hữu folder
sudo mv ~/task_bot /home/botuser/
sudo chown -R botuser:botuser /home/botuser/task_bot

# Chỉnh sửa service file
sudo nano /etc/systemd/system/taskbot.service
# Đổi User=root thành User=botuser
# Đổi WorkingDirectory=/root/task_bot thành /home/botuser/task_bot
# Đổi ExecStart=/root/task_bot/task_bot.py thành /home/botuser/task_bot/task_bot.py

# Reload và restart
sudo systemctl daemon-reload
sudo systemctl restart taskbot.service
```

### 2. Cấu hình Firewall

```bash
# Kiểm tra firewall
sudo firewall-cmd --state

# Nếu đang chạy và cần mở port SSH (nếu chưa mở)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 3. Bảo vệ file .env

```bash
# Chỉ cho phép owner đọc
chmod 600 ~/task_bot/.env

# Kiểm tra
ls -la ~/task_bot/.env
# Kết quả: -rw------- (chỉ owner có quyền)
```

---

## 🔄 Cập nhật Code

Khi có code mới trên GitHub:

```bash
# Vào thư mục project
cd ~/task_bot

# Pull code mới
git pull origin main

# Cài đặt dependencies mới (nếu có)
pip3 install -r requirements.txt

# Restart bot
sudo systemctl restart taskbot.service

# Kiểm tra logs
sudo journalctl -u taskbot.service -f
```

---

## 📊 Monitoring

### Xem logs realtime

```bash
# Xem logs của systemd service
sudo journalctl -u taskbot.service -f

# Hoặc tạo log file riêng
# Chỉnh sửa task_bot.py để log ra file
```

### Kiểm tra tài nguyên

```bash
# Xem CPU và RAM usage
top
# Tìm process python3

# Hoặc dùng htop (cài nếu chưa có)
sudo yum install -y htop
htop
```

### Auto-restart khi crash

Systemd đã cấu hình `Restart=always`, bot sẽ tự động restart nếu crash.

---

## 🐛 Troubleshooting

### ❌ Lỗi "ModuleNotFoundError: No module named 'telebot'"

**Giải pháp:**
```bash
pip3 install pyTelegramBotAPI --upgrade
```

### ❌ Lỗi "Permission denied"

**Giải pháp:**
```bash
# Thêm sudo trước lệnh
sudo python3 task_bot.py

# Hoặc cấp quyền
chmod +x task_bot.py
```

### ❌ Bot không phản hồi

**Kiểm tra:**
1. Service đang chạy không?
```bash
sudo systemctl status taskbot.service
```

2. Xem logs có lỗi gì không?
```bash
sudo journalctl -u taskbot.service -n 50
```

3. Bot token đúng không?
```bash
cat .env
```

4. Kết nối internet ổn định không?
```bash
ping -c 4 8.8.8.8
```

### ❌ Port đã được sử dụng

Bot Telegram không cần mở port, chỉ cần kết nối internet ra ngoài.

---

## 💡 Tips & Best Practices

### 1. Backup định kỳ

```bash
# Tạo script backup
cat > /root/backup_bot.sh << 'EOF'
#!/bin/bash
tar -czf /root/task_bot_backup_$(date +%Y%m%d).tar.gz -C /root task_bot
# Xóa backup cũ hơn 7 ngày
find /root -name "task_bot_backup_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /root/backup_bot.sh

# Thêm vào crontab (chạy mỗi ngày 2AM)
echo "0 2 * * * /root/backup_bot.sh" | sudo crontab -
```

### 2. Giám sát uptime

```bash
# Cài đặt tool monitor
sudo yum install -y sysstat

# Xem system load
sar -u 1 5
```

### 3. Tối ưu hiệu suất

```bash
# Giới hạn memory cho service (trong service file)
MemoryLimit=512M

# Reload
sudo systemctl daemon-reload
sudo systemctl restart taskbot.service
```

---

## ✅ Checklist

- [ ] Python 3 và Git đã cài đặt
- [ ] Code đã clone từ GitHub
- [ ] Dependencies đã cài đặt (requirements.txt)
- [ ] File .env đã cấu hình với bot token
- [ ] Bot chạy thử thành công
- [ ] Systemd service đã tạo và enable
- [ ] Bot đang chạy và phản hồi trên Telegram
- [ ] Logs không có lỗi
- [ ] Đã test restart server, bot tự động chạy lại

---

## 🎉 Hoàn tất!

Bot của bạn đã chạy 24/7 trên VPS CentOS 7!

**Kiểm tra:**
```bash
sudo systemctl status taskbot.service
```

Nếu thấy `Active: active (running)` → **THÀNH CÔNG!** ✅

---

## 📞 Hỗ trợ

- 📖 [GitHub Repository](https://github.com/rambo247/task_bot)
- 🐛 [Report Issues](https://github.com/rambo247/task_bot/issues)
- 📝 [README](https://github.com/rambo247/task_bot/blob/main/README.md)
