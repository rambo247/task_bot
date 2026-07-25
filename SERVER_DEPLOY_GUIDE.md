# 🚀 HƯỚNG DẪN DEPLOY LÊN SERVER

## ✅ Code đã được push lên GitHub
Repository: https://github.com/rambo247/task_bot.git

---

## 📋 CÁCH 1: Deploy Tự Động (KHUYÊN DÙNG)

### Bước 1: SSH vào server
```bash
ssh -p 5024 roo@15.235.210.238
```
*Nhập password khi được yêu cầu*

### Bước 2: Download và chạy script deploy
```bash
# Download script
curl -O https://raw.githubusercontent.com/rambo247/task_bot/main/server_deploy.sh

# Hoặc nếu đã clone repo:
cd task_bot
bash server_deploy.sh
```

### Script sẽ tự động:
- ✅ Clone/pull code mới nhất
- ✅ Cài Python và pip
- ✅ Cài dependencies (pyTelegramBotAPI, python-dotenv, requests)
- ✅ Tạo .env file (sẽ hỏi bot token)
- ✅ Stop bot cũ
- ✅ Start bot mới trong screen session
- ✅ Verify bot đang chạy

---

## 📋 CÁCH 2: Deploy Từng Bước (Manual)

### Bước 1: SSH vào server
```bash
ssh -p 5024 roo@15.235.210.238
```

### Bước 2: Clone hoặc pull code
```bash
# Nếu chưa có repo
git clone https://github.com/rambo247/task_bot.git
cd task_bot

# Nếu đã có repo
cd task_bot
git pull
```

### Bước 3: Cài dependencies
```bash
pip3 install -r requirements.txt --user
```

### Bước 4: Tạo file .env
```bash
nano .env
```
Paste vào:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
Lưu: `Ctrl+O`, Enter, `Ctrl+X`

### Bước 5: Stop bot cũ (nếu có)
```bash
pkill -f task_bot.py
```

### Bước 6: Start bot
```bash
# Option A: Dùng screen (khuyên dùng)
screen -dmS taskbot python3 task_bot.py

# Option B: Dùng nohup
nohup python3 task_bot.py > bot.log 2>&1 &
```

### Bước 7: Verify bot đang chạy
```bash
ps aux | grep task_bot
```

---

## 🔧 Quản Lý Bot Trên Server

### Xem bot logs (nếu dùng screen)
```bash
screen -r taskbot
# Detach: Ctrl+A sau đó nhấn D
```

### Xem bot logs (nếu dùng nohup)
```bash
tail -f bot.log
```

### Stop bot
```bash
# Nếu dùng screen
screen -X -S taskbot quit

# Nếu dùng nohup
pkill -f task_bot.py
```

### Restart bot
```bash
# Stop
pkill -f task_bot.py

# Start lại
screen -dmS taskbot python3 task_bot.py
```

### Check bot status
```bash
ps aux | grep task_bot
# Nếu thấy process → bot đang chạy ✅
```

---

## 🧪 Test Bot Sau Deploy

### Test 1: Private Chat
```
1. Mở Telegram
2. Tìm bot của bạn
3. Gửi: /start
4. Gửi: /add Test task
5. Gửi: /list
```
**Expected**: Bot reply và hiển thị task ✅

### Test 2: Group Privacy (QUAN TRỌNG)
```
1. Tạo group test, thêm bot vào
2. User A: /start
3. User A: /add Task A
4. User B: /start  
5. User B: /list
```
**Expected**: User B KHÔNG thấy Task A ✅

---

## ⚠️ Troubleshooting

### Bot không khởi động
**Check logs:**
```bash
# Nếu dùng screen
screen -r taskbot

# Nếu dùng nohup
tail -50 bot.log
```

**Common issues:**
1. ❌ Token sai → Check .env file
2. ❌ Dependencies thiếu → Chạy lại: `pip3 install -r requirements.txt`
3. ❌ Python không có → Install: `sudo yum install python3 -y`
4. ❌ Port blocked → Check firewall

### Bot không reply trong group
**Fix:**
1. Vào @BotFather
2. Settings → Group Privacy → **OFF**
3. Remove bot khỏi group và add lại

### Bot bị stop khi logout SSH
**Solution:** Dùng screen hoặc nohup (đã có trong script)
```bash
# Screen (khuyên dùng)
screen -dmS taskbot python3 task_bot.py

# Nohup
nohup python3 task_bot.py > bot.log 2>&1 &
```

---

## 📊 Monitor Bot

### CPU và Memory usage
```bash
top -p $(pgrep -f task_bot.py)
```

### Bot uptime
```bash
ps -o etime= -p $(pgrep -f task_bot.py)
```

### Restart bot hàng ngày (optional)
Thêm vào crontab:
```bash
crontab -e
```
Paste:
```
0 3 * * * pkill -f task_bot.py && cd ~/task_bot && screen -dmS taskbot python3 task_bot.py
```
*(Restart bot lúc 3h sáng mỗi ngày)*

---

## 🎯 Summary Commands

```bash
# 1. SSH vào server
ssh -p 5024 roo@15.235.210.238

# 2. Deploy tự động
cd task_bot 2>/dev/null || git clone https://github.com/rambo247/task_bot.git
cd task_bot
bash server_deploy.sh

# 3. Hoặc deploy manual
git pull
pip3 install -r requirements.txt --user
pkill -f task_bot.py
screen -dmS taskbot python3 task_bot.py

# 4. Check status
screen -r taskbot
ps aux | grep task_bot
```

---

## ✅ Checklist Deploy

- [ ] SSH vào server thành công
- [ ] Code đã được pull/clone
- [ ] Dependencies đã cài
- [ ] File .env đã tạo với bot token
- [ ] Bot đã start (screen hoặc nohup)
- [ ] Bot process đang chạy (ps aux | grep)
- [ ] Test /start trong private chat
- [ ] Test privacy trong group (2 users)
- [ ] Bot reply đúng cho mỗi user

---

**Happy Deploying!** 🎉

Có vấn đề gì liên hệ hoặc check logs!
