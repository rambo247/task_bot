# 🚀 HƯỚNG DẪN DEPLOY BOT

## ✅ Tests đã PASS

Tất cả tests logic đã passed:
- ✅ Data structures đúng
- ✅ Helper functions đầy đủ  
- ✅ Không còn chat_id sai chỗ
- ✅ Callback handler đúng
- ✅ Reminder system hoạt động

## 📦 Bước 1: Cài đặt Dependencies

```bash
pip install pyTelegramBotAPI python-dotenv requests
```

hoặc dùng requirements.txt:
```bash
pip install -r requirements.txt
```

Nội dung requirements.txt:
```
pyTelegramBotAPI
python-dotenv
requests
```

## 🔑 Bước 2: Tạo Bot Token

1. Mở Telegram, tìm @BotFather
2. Gửi `/newbot` (hoặc dùng bot cũ)
3. Làm theo hướng dẫn để lấy TOKEN
4. **QUAN TRỌNG**: Vào @BotFather → `/mybots` → Chọn bot → `Bot Settings` → `Group Privacy` → **TURN OFF** (để bot đọc được messages trong group)

## 📝 Bước 3: Tạo file .env

Tạo file `.env` trong thư mục f:\workspace12\:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GITHUB_TOKEN=your_github_token_here_optional
```

**Lưu ý**: 
- `TELEGRAM_BOT_TOKEN` là BẮT BUỘC
- `GITHUB_TOKEN` là TÙY CHỌN (chỉ cần nếu muốn dùng AI features)

## 🧪 Bước 4: Test Trước Khi Deploy Chính Thức

### Test 1: Chạy bot local
```bash
python task_bot.py
```

Nếu thành công, sẽ thấy:
```
🤖 Bot đang khởi động...
📱 Bot name: @your_bot_username
🆔 Bot ID: 123456789
✅ Bot đã sẵn sàng và đang lắng nghe tin nhắn...
```

### Test 2: Test trong Private Chat
1. Mở Telegram, tìm bot của bạn
2. Gửi `/start`
3. Thử các lệnh:
   - `/add Test task 1`
   - `/list`
   - `/add Test task 2` với reminder
   - Đợi reminder được gửi

✅ **Expected**: Bot hoạt động bình thường

### Test 3: Test trong Group (QUAN TRỌNG NHẤT)

#### Setup:
1. Tạo một group test
2. Thêm bot vào group
3. Cần ít nhất 2 users khác nhau để test

#### Test với User A:
```
User A gửi: /start
User A gửi: /add Task của A - họp team
User A gửi: /list
```
✅ **Expected**: User A thấy "Task của A - họp team"

#### Test với User B (cùng group):
```
User B gửi: /start
User B gửi: /list
```
✅ **Expected**: User B thấy "Danh sách trống!" (KHÔNG thấy task của A)

```
User B gửi: /add Task của B - gọi khách
User B gửi: /list
```
✅ **Expected**: User B chỉ thấy "Task của B - gọi khách"

#### Verify lại với User A:
```
User A gửi: /list
```
✅ **Expected**: User A vẫn chỉ thấy "Task của A - họp team"

### Test 4: Test Reminders trong Group

```
User A: /add Task A với reminder 1m
User B: /add Task B với reminder 2m
```

Sau 1 phút:
✅ **Expected**: Chỉ User A nhận reminder (hiện trong group)

Sau 2 phút:  
✅ **Expected**: Chỉ User B nhận reminder (hiện trong group)

## 🎯 Bước 5: Deploy Production

### Option 1: Chạy trên Server
```bash
# Sử dụng screen hoặc tmux để chạy background
screen -S telegram_bot
python task_bot.py

# Detach: Ctrl+A, D
# Reattach: screen -r telegram_bot
```

### Option 2: Sử dụng systemd (Linux)
Tạo file `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram Task Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/workspace12
ExecStart=/usr/bin/python3 task_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Chạy:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### Option 3: Deploy lên Cloud

#### Heroku:
```bash
# Procfile
web: python task_bot.py
```

#### Railway/Render:
- Start command: `python task_bot.py`
- Add environment variables

#### VPS (DigitalOcean, AWS, etc.):
1. Upload code lên server
2. Cài dependencies
3. Setup systemd service
4. Run

## ⚠️ Lưu Ý Quan Trọng

### 1. Group Privacy Settings
Bot PHẢI có Group Privacy = OFF trong @BotFather để đọc được messages trong group.

### 2. Data Persistence
Bot hiện lưu data trong memory. Khi restart sẽ mất dữ liệu. 

**Để lưu vĩnh viễn**, cần thêm:
- SQLite database
- JSON file
- Redis
- PostgreSQL

### 3. Rate Limits
Telegram có rate limits:
- 30 messages/giây
- 1 message/chat/giây

Bot hiện đã handle tốt, nhưng cần lưu ý khi có nhiều users.

### 4. Error Handling
Bot có basic error handling. Trong production, nên thêm:
- Logging (file logs)
- Error notifications
- Monitoring

### 5. Security
- ✅ Mỗi user có data riêng tư
- ✅ Không lưu passwords
- ⚠️ TELEGRAM_BOT_TOKEN phải được bảo mật
- ⚠️ Không commit .env vào git

## 📊 Monitoring

Theo dõi bot:
```bash
# Xem logs
tail -f bot.log

# Check process
ps aux | grep task_bot

# Check memory usage
top -p $(pgrep -f task_bot)
```

## 🐛 Troubleshooting

### Bot không reply
- Check token đúng chưa
- Check internet connection
- Check bot có bị ban không

### Group Privacy issues
- Vào @BotFather → Settings → Group Privacy → OFF

### Reminders không gửi
- Check reminder_thread đang chạy
- Check timezone settings
- Check system time

## ✅ Checklist Deploy

- [ ] Cài đặt dependencies
- [ ] Tạo .env với bot token
- [ ] Test private chat
- [ ] Test group chat với 2 users
- [ ] Test reminders
- [ ] Verify privacy (mỗi user chỉ thấy tasks của mình)
- [ ] Setup monitoring
- [ ] Setup auto-restart
- [ ] Backup plan

## 🎉 Kết Luận

Bot đã sẵn sàng deploy với:
- ✅ Privacy đảm bảo cho mỗi user
- ✅ Hoạt động trong cả private và group chat
- ✅ Reminder system hoạt động chính xác
- ✅ Multi-user support

**Happy Deploying!** 🚀
