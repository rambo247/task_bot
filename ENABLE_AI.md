# 🤖 3 BƯỚC KÍCH HOẠT AI (3 PHÚT)

Message bạn thấy: **"💡 Gửi tin nhắn tự do! Nhưng cần GitHub token để kích hoạt AI."**

## ⚡ Setup Nhanh

### 1️⃣ Lấy GitHub Token (1 phút)
🔗 **https://github.com/settings/tokens**

- Click: **Generate new token (classic)**
- Note: `Bot AI`
- Expiration: `No expiration`
- Scopes: **Không cần chọn gì** ✅
- Click: **Generate token**
- **COPY TOKEN** (có dạng `ghp_xxxx...`)

### 2️⃣ Thêm Token vào .env (1 phút)

#### Trên Windows:
```powershell
notepad .env
```
Paste:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
Save và đóng.

#### Trên Server:
```bash
ssh -p 5024 roo@15.235.210.238
cd task_bot
nano .env
```
Thêm dòng:
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
Lưu: `Ctrl+O`, Enter, `Ctrl+X`

### 3️⃣ Restart Bot (30 giây)

#### Windows:
```powershell
# Ctrl+C để stop
python task_bot.py
```

#### Server:
```bash
pkill -f task_bot.py
screen -dmS taskbot python3 task_bot.py
```

---

## ✅ Test AI

Gửi cho bot:
```
Mua sữa 5h chiều
```

**Nếu có AI**: Bot tạo task + reminder lúc 17:00 🤖  
**Nếu không AI**: Bot vẫn reply message về token

---

## 🎁 AI Có Gì Hay?

### ✅ Với AI:
```
"Nhắc tôi họp team 9h sáng mai"
→ Bot tự động tạo task + reminder ✨
```

### ❌ Không AI:
```
/add Họp team
→ Chọn ngày
→ Chọn giờ 9:00
→ /remind 1 09:00 mai
```

**AI tiện hơn NHIỀU!** 🚀

---

## 💰 Chi Phí

- GitHub Token: **MIỄN PHÍ** ✅
- GitHub Models API: **MIỄN PHÍ** ✅
- Rate Limit: 60 req/phút - **MIỄN PHÍ** ✅

**Total: $0/tháng** 🎉

---

## 📄 Hướng Dẫn Chi Tiết

Xem **[AI_SETUP.md](AI_SETUP.md)** để biết:
- Troubleshooting
- Test cases đầy đủ
- Debug commands

---

## ⚠️ Lưu Ý

- Token chỉ hiển thị 1 lần → Save ngay!
- KHÔNG share token công khai
- Bot vẫn hoạt động tốt không có AI (dùng commands)

---

**3 phút để có AI - đáng thử!** 🤖✨
