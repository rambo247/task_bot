# 🎤 HƯỚNG DẪN TÍNH NĂNG VOICE TO TEXT

## ✨ Tính năng mới: Chuyển đổi giọng nói thành văn bản

Bot giờ có thể **nghe giọng nói** và **chuyển thành văn bản**, lưu thành file txt!

### 🎯 Cách sử dụng

1. **Ghi âm giọng nói** trong Telegram (nhấn giữ icon micro)
2. **Gửi voice message** cho bot
3. **Đợi vài giây** - Bot sẽ xử lý
4. **Nhận file .txt** với nội dung đã chuyển đổi

### 📱 Demo

```
Bạn: [Gửi voice message: "Xin chào, hôm nay tôi cần mua sữa và đi họp lúc 3 giờ"]
Bot: 🎤 Đang xử lý giọng nói...
Bot: 🤖 Đang chuyển đổi giọng nói thành văn bản...
Bot: ✅ [Gửi file transcription.txt]
     📝 Nội dung: "Xin chào, hôm nay tôi cần mua sữa và đi họp lúc 3 giờ"
```

---

## 🔧 Setup (Cần OpenAI API Key)

### Bước 1: Tạo OpenAI API Key

#### Option 1: Tạo tài khoản OpenAI
1. Truy cập: **https://platform.openai.com/**
2. Sign up / Log in
3. Add payment method (cần thẻ tín dụng)
4. Vào **API Keys**: https://platform.openai.com/api-keys
5. Click **"Create new secret key"**
6. Copy key: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

⚠️ **Lưu ý:** OpenAI Whisper API **KHÔNG MIỄN PHÍ** (nhưng rất rẻ)
- Chi phí: ~$0.006 / phút audio
- Ví dụ: 1 phút voice = $0.006 (≈ 150 VND)
- 100 phút voice = $0.60 (≈ 15,000 VND)

### Bước 2: Thêm API Key vào .env

#### Trên Windows:
```powershell
notepad .env
```

Thêm dòng:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Trên Server Linux:
```bash
ssh -p 5024 root@15.235.210.238
cd task_bot
nano .env
```

Thêm:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Lưu: `Ctrl+O`, Enter, `Ctrl+X`

### Bước 3: Restart Bot

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

### Bước 4: Test

1. Mở Telegram, tìm bot
2. Ghi âm voice message (tiếng Việt hoặc English)
3. Gửi cho bot
4. Đợi và nhận file txt!

---

## 🎯 Tính năng

### ✅ Hỗ trợ
- **Tiếng Việt** (chính)
- **English** và nhiều ngôn ngữ khác
- File format: `.ogg` (Telegram voice)
- Output: `.txt` file với UTF-8 encoding

### 📄 File txt format
```
=== CHUYỂN ĐỔI GIỌNG NÓI THÀNH VĂN BẢN ===
Thời gian: 25/07/2026 15:30:00
Người dùng: John Doe
==================================================

[Nội dung văn bản đã chuyển đổi]
```

### ⚡ Performance
- Audio 10 giây: ~2-3 giây xử lý
- Audio 1 phút: ~5-8 giây xử lý
- Độ chính xác: ~95% (tiếng Việt rõ ràng)

---

## 💰 Chi phí

### OpenAI Whisper Pricing

| Duration | Cost | VND (≈) |
|----------|------|---------|
| 10 giây | $0.001 | 25 VND |
| 1 phút | $0.006 | 150 VND |
| 10 phút | $0.06 | 1,500 VND |
| 1 giờ | $0.36 | 9,000 VND |

**Rất rẻ!** Một người dùng gửi 100 voice messages (mỗi cái 30 giây) chỉ tốn ~$0.30 (7,500 VND).

### Free Alternative?

Hiện tại **KHÔNG CÓ** alternative hoàn toàn miễn phí với chất lượng tương đương. Options:
- **OpenAI Whisper** (paid, tốt nhất) ✅
- **Google Cloud Speech-to-Text** (paid, cũng tốt)
- **Azure Speech Services** (paid)
- **Local Whisper** (free nhưng cần GPU, không phù hợp hosting)

---

## 🆘 Troubleshooting

### ❌ "Không thể gửi file txt vào chat riêng!"

**Nguyên nhân:** Bạn chưa start bot trong private chat

**Fix:**
1. Mở chat riêng với bot (click vào bot name)
2. Gửi `/start`
3. Quay lại group và gửi voice message lại

**Tại sao cần start bot?**
- Telegram không cho phép bot gửi message đầu tiên cho user
- User phải start conversation trước
- Sau khi start, bot có thể gửi message vào private chat

### ❌ "Tính năng chuyển đổi giọng nói cần OpenAI API key"

**Nguyên nhân:** Chưa có OPENAI_API_KEY trong .env

**Fix:**
```bash
# Check .env
cat .env | grep OPENAI_API_KEY

# Nếu không có, thêm:
echo "OPENAI_API_KEY=sk-proj-xxx" >> .env

# Restart bot
pkill -f task_bot.py
screen -dmS taskbot python3 task_bot.py
```

### ❌ "Không thể chuyển đổi giọng nói"

**Possible causes:**
1. **API key sai hoặc expired**
   - Check tại: https://platform.openai.com/api-keys
   - Tạo key mới nếu cần

2. **Hết credits OpenAI**
   - Check balance: https://platform.openai.com/account/usage
   - Add payment method và credits

3. **Network issue**
   - Bot cần internet để call OpenAI API
   - Check server internet connection

4. **File audio lỗi**
   - Thử gửi voice message mới
   - Voice phải ngắn hơn 25MB

### ❌ Bot xử lý chậm

**Nguyên nhân:**
- OpenAI API mất 2-8 giây tùy độ dài audio
- Network latency

**Normal processing time:**
- 10s audio → 2-3s
- 1 min audio → 5-8s
- 5 min audio → 15-30s

### ❌ Transcription không chính xác

**Tips để cải thiện:**
1. **Nói rõ ràng**, không quá nhanh
2. **Môi trường yên tĩnh** (ít noise)
3. **Giữ micro gần miệng**
4. **Không dùng trong môi trường ồn**

---

## 🎯 Use Cases

### 📝 Ghi chú nhanh
```
Voice: "Nhớ mua sữa, trứng, và bánh mì khi về nhà"
→ File txt: "Nhớ mua sữa, trứng, và bánh mì khi về nhà"
```

### 📞 Ghi chép cuộc họp
```
Voice: [5 phút thảo luận]
→ File txt với toàn bộ nội dung
```

### 💬 Chuyển đổi interview
```
Voice: [Phỏng vấn 30 phút]
→ File txt transcript hoàn chỉnh
```

### 📚 Học tập
```
Voice: [Ghi âm bài giảng]
→ File txt để ôn tập
```

---

## 📋 Commands Summary

| Action | How to |
|--------|--------|
| Gửi voice | Giữ icon micro, ghi âm, thả ra |
| Check có AI key không | `/help` xem hướng dẫn |
| Setup OpenAI key | Thêm vào .env, restart bot |
| Test transcription | Gửi voice message ngắn |

---

## 🔒 Privacy & Security

### ✅ Bot xử lý như thế nào?
1. Download voice từ Telegram
2. Gửi đến OpenAI Whisper API
3. Nhận text, tạo file txt
4. **Gửi file txt về PRIVATE CHAT của user** (không gửi vào group)
5. Xóa file voice tạm thời
6. Xóa file txt tạm thời

### 🛡️ Privacy Protection
- ✅ **Transcriptions luôn gửi về private chat**, kể cả khi bạn gửi voice từ group
- ✅ **Các thành viên khác trong group KHÔNG thấy nội dung** transcription của bạn
- ✅ Voice files được xóa ngay sau khi xử lý
- ✅ Txt files được xóa ngay sau khi gửi
- ✅ Mỗi file có tên unique: `transcription_{user_id}_{timestamp}.txt`

### 📱 Group Chat Behavior
**⚠️ QUAN TRỌNG: Trước khi dùng trong group**

Bạn PHẢI start bot trong private chat trước:
1. Mở chat riêng với bot
2. Gửi `/start`
3. Sau đó mới có thể dùng voice trong group

**Khi gửi voice trong group (sau khi đã start):**
1. Bot nhận voice message
2. Bot hiển thị "🎤 Đang xử lý..." trong group
3. Bot gửi file txt về **private chat** với bạn 🔒
4. Bot thông báo trong group: "✅ Đã gửi vào chat riêng"
5. **Members khác KHÔNG nhìn thấy nội dung**

**Nếu chưa start bot trong private chat:**
- Bot sẽ thông báo: "⚠️ Không thể gửi file txt vào chat riêng!"
- Hướng dẫn: Mở chat riêng → /start → Gửi lại voice

**Khi gửi voice trong private chat:**
1. Bot nhận voice message
2. Bot xử lý và gửi file txt trực tiếp
3. Chỉ có bạn nhìn thấy

### 🔐 Bảo mật
- ✅ Voice files được xóa sau khi xử lý
- ✅ Txt files được xóa sau khi gửi
- ✅ OpenAI **KHÔNG lưu trữ** audio (theo policy)
- ⚠️ Text được gửi qua OpenAI API (read policy)

**Privacy policy:** https://openai.com/policies/privacy-policy

---

## 📊 Technical Details

### API Used
- **OpenAI Whisper API v1**
- Endpoint: `https://api.openai.com/v1/audio/transcriptions`
- Model: `whisper-1`
- Language: `vi` (Vietnamese)
- Response format: `text`

### File Handling
```python
# Voice file format
Input: .ogg (Telegram voice)
Max size: 25MB
Max duration: Unlimited (but affects cost)

# Output file format
Output: .txt (UTF-8 encoded)
Name: transcription_<user_id>_<timestamp>.txt
```

### Dependencies
```
pyTelegramBotAPI<4.0.0    # Telegram Bot API
requests>=2.27.0          # HTTP requests
python-dotenv>=0.20.0     # Environment variables
```

---

## 🎉 Summary

**Setup trong 5 phút:**
1. 🔑 Lấy OpenAI API key (https://platform.openai.com/)
2. 📝 Thêm vào .env: `OPENAI_API_KEY=sk-proj-xxx`
3. 🔄 Restart bot
4. 🎤 Test bằng voice message

**Benefits:**
- ✅ Chuyển voice thành text tự động
- ✅ Lưu thành file txt
- ✅ Hỗ trợ tiếng Việt tốt
- ✅ Chi phí rất thấp (~150 VND/phút)
- ✅ Xử lý nhanh (2-8 giây)

**Limitations:**
- ❌ Không miễn phí (cần OpenAI credits)
- ❌ Cần internet connection
- ❌ Độ chính xác phụ thuộc vào chất lượng audio

---

## 📚 Resources

- **OpenAI Platform**: https://platform.openai.com/
- **Whisper API Docs**: https://platform.openai.com/docs/guides/speech-to-text
- **Pricing**: https://openai.com/api/pricing/
- **Bot Repository**: https://github.com/rambo247/task_bot

---

**Enjoy voice-to-text transcription!** 🎤✨

Questions? Check [SERVER_DEPLOY_GUIDE.md](SERVER_DEPLOY_GUIDE.md) or open an issue!
