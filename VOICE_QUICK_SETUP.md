# 🎤 QUICK GUIDE: Voice to Text

## ⚡ Setup trong 5 phút

### 1️⃣ Lấy OpenAI API Key (2 phút)
🔗 **https://platform.openai.com/api-keys**

- Sign up / Log in OpenAI
- Add payment method (cần thẻ)
- Create API key
- Copy: `sk-proj-xxxxxxxxxxxx`

### 2️⃣ Thêm vào .env (1 phút)

#### Windows:
```powershell
notepad .env
```

#### Server:
```bash
ssh -p 5024 root@15.235.210.238
cd task_bot
nano .env
```

Thêm dòng:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```

Lưu file (Ctrl+O, Enter, Ctrl+X)

### 3️⃣ Restart Bot (1 phút)

#### Windows:
```powershell
python task_bot.py
```

#### Server:
```bash
pkill -f task_bot.py
screen -dmS taskbot python3 task_bot.py
```

### 4️⃣ Test! (1 phút)
- Mở Telegram
- Tìm bot
- Ghi âm voice message
- Gửi cho bot
- Nhận file .txt ✅

---

## 💰 Chi phí

| Voice Duration | Cost |
|----------------|------|
| 10 giây | ~25 VND |
| 1 phút | ~150 VND |
| 10 phút | ~1,500 VND |

**Rất rẻ!** 100 voice messages (30s mỗi cái) = ~7,500 VND

---

## 🎯 Cách dùng

### Private Chat:
1. **Giữ icon micro** trong Telegram
2. **Nói** nội dung (tiếng Việt hoặc English)
3. **Thả tay** để gửi
4. **Đợi 2-8 giây**
5. **Nhận file .txt** ✅

### Group Chat (Riêng tư 🔒):

**⚠️ Bước đầu tiên (BẮT BUỘC):**
1. **Mở chat riêng với bot**
2. **Gửi `/start`** 
3. ✅ Xong! Giờ có thể dùng voice trong group

**Sau khi đã start:**
1. **Gửi voice message** trong group
2. Bot hiển thị "Đang xử lý..." trong group
3. **File .txt được gửi về PRIVATE CHAT** với bạn
4. **Members khác KHÔNG nhìn thấy** nội dung
5. Bot thông báo trong group: "Đã gửi vào chat riêng" ✅

**Nếu chưa start:**
- Bot thông báo: "Không thể gửi file txt vào chat riêng!"
- Làm theo hướng dẫn phía trên ↑

---

## 🛡️ Privacy

**✅ Đảm bảo riêng tư:**
- Transcriptions luôn gửi về private chat
- Members trong group không thấy nội dung của nhau
- Mỗi user chỉ nhìn thấy transcription của chính mình

---

## ❌ Lỗi thường gặp

### "Không thể gửi file txt vào chat riêng"
→ **Chưa start bot trong private chat**
- Fix: Mở chat riêng → `/start` → Gửi lại voice

### "Cần OpenAI API key"
→ Chưa thêm key vào .env, xem bước 2 ↑

### "Không thể chuyển đổi" / "Hết credits"
→ Check:
- API key đúng chưa?
- Hết credits OpenAI chưa? → Nạp thêm credits
- Internet có ok không?

### Bot xử lý chậm
→ Bình thường! OpenAI API cần 2-8 giây

---

## 📚 Chi tiết hơn

Xem **[VOICE_TO_TEXT_GUIDE.md](VOICE_TO_TEXT_GUIDE.md)** để biết:
- Technical details
- Troubleshooting đầy đủ
- Use cases
- Privacy policy

---

## ✅ Summary

**3 bước đơn giản:**
1. 🔑 Lấy OpenAI key → https://platform.openai.com/
2. 📝 Thêm vào .env → `OPENAI_API_KEY=sk-proj-xxx`
3. 🔄 Restart bot → `pkill -f task_bot.py && screen -dmS taskbot python3 task_bot.py`

**Done! 🎉** Gửi voice message để test!

---

**Need help?** Check:
- [VOICE_TO_TEXT_GUIDE.md](VOICE_TO_TEXT_GUIDE.md) - Full guide
- [AI_SETUP.md](AI_SETUP.md) - GitHub AI setup
- [SERVER_DEPLOY_GUIDE.md](SERVER_DEPLOY_GUIDE.md) - Server management
