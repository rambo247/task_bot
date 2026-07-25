# ✅ CODE ĐÃ LÊN GITHUB - SẴN SÀNG DEPLOY

Repository: **https://github.com/rambo247/task_bot.git**

---

## 🚀 DEPLOY NGAY (Copy & Paste)

### Bước 1: SSH vào server
```bash
ssh -p 5024 roo@15.235.210.238
```

### Bước 2: Clone và deploy tự động
```bash
git clone https://github.com/rambo247/task_bot.git
cd task_bot
bash server_deploy.sh
```

Script sẽ hỏi bot token, bạn paste vào là xong!

---

## 🔄 UPDATE BOT SAU NÀY

Khi có code mới từ GitHub:
```bash
ssh -p 5024 roo@15.235.210.238
cd task_bot
git pull
pkill -f task_bot.py
screen -dmS taskbot python3 task_bot.py
```

---

## 👀 CHECK BOT STATUS

```bash
# Xem bot có chạy không
ps aux | grep task_bot

# Xem logs
screen -r taskbot
# (Nhấn Ctrl+A sau đó D để thoát)
```

---

## 📄 Chi Tiết Hơn

Xem file **[SERVER_DEPLOY_GUIDE.md](SERVER_DEPLOY_GUIDE.md)** để biết:
- Troubleshooting
- Monitor bot
- Restart bot
- Setup crontab

---

**Chỉ cần 2 phút là deploy xong!** 🎉
