# ⚡ START GUIDE - 5 PHÚT

## 🎯 BẮT ĐẦU NGAY!

### Bước 1: Cài Đặt (2 phút)
```bash
# Windows/Linux/macOS:
pip install -r requirements.txt
```

### Bước 2: Cấu Hình (.env)
```bash
# Copy file example
cp .env.example .env

# Sửa file .env, thêm:
TELEGRAM_BOT_TOKEN=your_token_from_botfather
GITHUB_TOKEN=your_github_token (optional)
```

**Lấy Telegram Token:**
1. Telegram → tìm @BotFather
2. Gửi: `/newbot`
3. Copy token

### Bước 3: Chạy! (1 giây)
```bash
python task_bot.py
```

### Bước 4: Test (30 giây)
```
1. Telegram → tìm bot của bạn
2. Gửi: /start
3. Thấy menu → ✅ Done!
```

---

## 🚀 QUICK SETUP ENTERPRISE

### 1. Tạo Organization (30s)
```
Menu → 🏢 Doanh Nghiệp → ➕ Tạo
Nhập tên: "ABC Company"
```

### 2. Import Data (1 phút)
```
Copy data này:

Địa chỉ? | 123 ABC Street, HCM
Email? | info@company.com
Hotline? | 1900-1234

[DEPT] IT | John | it@co.com | 101
[DEPT] Sales | Jane | sales@co.com | 102

[CONTACT] John | CTO | IT | john@co.com | 0901234567
[CONTACT] Jane | Sales Dir | Sales | jane@co.com | 0902345678

→ Menu → Import → Paste Text → Paste → Done!
```

### 3. Bật AI (10s)
```
Menu → 🤖 Trợ Lý AI → 🟢 Bật AI
```

### 4. Test AI (30s)
```
Hỏi: "Ai phụ trách IT?"
Bot: "🏛️ IT Department - John..."

Hỏi: "Liên hệ CTO"
Bot: "👤 John - john@co.com..."

✅ Hoạt động perfect!
```

---

## 📚 DOCS

| Cần gì? | Đọc file nào? |
|---------|--------------|
| Tổng quan | README_ENTERPRISE.md |
| Cài đặt chi tiết | INSTALL.md |
| Quick ref | QUICK_REFERENCE.md |
| User guide | ENTERPRISE_GUIDE.md |
| Demo | test_enterprise.py |
| Tìm docs | INDEX.md |

---

## 🐛 LỖI THƯỜNG GẶP

### "No module named 'telebot'"
```bash
pip install pyTelegramBotAPI
```

### "Enterprise features not enabled"
```bash
pip install beautifulsoup4 lxml validators
```

### Bot không phản hồi
```
Check .env file có đúng token không
Token format: 1234567890:ABC...
```

---

## ✅ CHECKLIST

```
[ ] Python 3.8+ installed
[ ] pip install -r requirements.txt
[ ] .env file configured
[ ] Telegram bot token valid
[ ] python task_bot.py runs
[ ] /start works in Telegram
[ ] 🏢 Doanh Nghiệp menu visible
```

All green? → ✅ You're ready! 🎉

---

## 🎯 NEXT STEPS

1. ✅ Import your real data
2. ✅ Setup departments
3. ✅ Add employees
4. ✅ Enable AI
5. ✅ Test features
6. ✅ Deploy to production
7. 🚀 Enjoy!

---

**That's it! 5 minutes from zero to hero! 🚀**

**Full docs:** INDEX.md  
**Quick ref:** QUICK_REFERENCE.md  
**Version:** v2.1.0 Enterprise
