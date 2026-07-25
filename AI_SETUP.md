# 🤖 Hướng Dẫn Kích Hoạt AI (GitHub Models)

## ✨ Tính năng AI mới

Bot giờ đã có **AI thông minh** để hiểu ngôn ngữ tự nhiên!

### Ví dụ sử dụng:
```
❌ Trước đây (phức tạp):
   /add Họp team
   Chọn ngày → Chọn giờ 9:00

✅ Bây giờ (đơn giản):
   "Nhắc tôi họp team sáng mai 9h"
   → Bot tự động tạo task + đặt nhắc nhở!
```

### Các câu AI có thể hiểu:
- **"Nhắc tôi họp team sáng mai 9h"** → Task + reminder 9:00 ngày mai
- **"Gọi khách hàng chiều nay 2h"** → Task + reminder 14:00 hôm nay
- **"Nộp báo cáo tối nay"** → Task + reminder 20:00
- **"Mua sữa"** → Chỉ tạo task (không có reminder)

## 🔧 Cách kích hoạt AI

### Bước 1: Tạo GitHub Token (MIỄN PHÍ - 2 phút)

#### Option A: Sử dụng GitHub Models (KHUYẾN NGHỊ)
1. Truy cập: **https://github.com/marketplace/models**
2. Click vào model bất kỳ (ví dụ: GPT-4o-mini)
3. Click **"Get started"** 
4. GitHub sẽ tự động tạo token hoặc dẫn đến trang tạo token

#### Option B: Tạo Token Thủ Công
1. Truy cập: **https://github.com/settings/tokens**
2. Nhấn **"Generate new token"** → **"Generate new token (classic)"**
3. Điền thông tin:
   - **Note**: `Telegram Task Bot AI`
   - **Expiration**: `No expiration` hoặc `90 days`
   - **Scopes**: ✅ **Không cần chọn scope nào** (GitHub Models free)
4. Nhấn **"Generate token"**
5. **🔴 SAO CHÉP TOKEN NGAY!** (Token có dạng: `ghp_xxxxxxxxxxxx`)

⚠️ **LƯU Ý**: Token chỉ hiển thị 1 lần, save vào notepad!

### Bước 2: Thêm token vào .env file

#### Trên máy local (Windows)
```powershell
# Mở file .env (hoặc tạo mới nếu chưa có)
notepad .env
```

Thêm/cập nhật:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Lưu file và đóng notepad.

#### Trên server Linux
```bash
# SSH vào server
ssh -p 5024 roo@15.235.210.238

# Navigate to bot folder
cd task_bot

# Edit .env file
nano .env
```

Thêm dòng GitHub token:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Lưu file**: `Ctrl+O` → Enter → `Ctrl+X`

### Bước 3: Restart bot để áp dụng thay đổi

#### Trên Windows (Local)
```powershell
# Nếu bot đang chạy, nhấn Ctrl+C để stop
# Sau đó start lại:
python task_bot.py
```

#### Trên Server Linux
```bash
# Stop bot cũ
pkill -f task_bot.py

# Start bot mới với screen (KHUYẾN NGHỊ)
screen -dmS taskbot python3 task_bot.py

# Hoặc dùng nohup
nohup python3 task_bot.py > bot.log 2>&1 &

# Check bot đang chạy
ps aux | grep task_bot
```

**Verify bot started:**
```bash
# Xem logs (nếu dùng screen)
screen -r taskbot
# Press Ctrl+A then D to detach

# Xem logs (nếu dùng nohup)
tail -f bot.log
```

## ✅ Kiểm tra AI đã hoạt động

### Test 1: Tin nhắn đơn giản
Gửi cho bot:
```
Mua sữa
```

**Nếu có AI**: Bot sẽ tạo task "Mua sữa" ✅  
**Nếu không AI**: Bot reply "💡 Gửi tin nhắn tự do! Nhưng cần GitHub token để kích hoạt AI."

### Test 2: Tin nhắn có thời gian
Gửi cho bot:
```
Nhắc tôi họp team sáng mai 9h
```

**Nếu có AI**: 
```
✅ Task "Họp team" đã được thêm!
⏰ Reminder: Ngày mai lúc 09:00
🤖 Phân tích bởi AI
```

### Test 3: Ngôn ngữ tự nhiên phức tạp
```
Gọi khách hàng lúc 3 giờ chiều hôm nay
→ AI parse: "Gọi khách hàng" + reminder 15:00 hôm nay

Nộp báo cáo tối nay 8 giờ
→ AI parse: "Nộp báo cáo" + reminder 20:00

Đi gym tuần sau
→ AI parse: "Đi gym" (không có specific time)
```

### 🎯 Dấu hiệu AI hoạt động:
- ✅ Có emoji 🤖 trong reply
- ✅ Bot tự động parse task name và time
- ✅ Không cần dùng commands /add, /remind

### ⚠️ Dấu hiệu AI CHƯA hoạt động:
- ❌ Thấy message: "Nhưng cần GitHub token để kích hoạt AI"
- ❌ Bot chỉ reply menu buttons
- ❌ Phải dùng commands /add thủ công

## 💡 Lưu ý quan trọng

### 🆓 Chi phí
- **GitHub Models 100% MIỄN PHÍ** cho developers
- Không cần thẻ tín dụng
- Rate limit: 60 requests/phút, 150,000 tokens/ngày
- AI model: `gpt-4o-mini` (nhanh + chính xác)

### 🎯 Khi nào dùng AI?
✅ **Nên dùng AI khi:**
- Muốn thêm task nhanh bằng ngôn ngữ tự nhiên
- Task có thời gian cụ thể ("5h chiều", "mai", "tuần sau")  
- Muốn trải nghiệm người dùng tốt hơn

✅ **Vẫn dùng Commands khi:**
- Cần chính xác 100% (AI đôi khi parse sai)
- Không có internet
- Không muốn setup GitHub token

### 🔒 Bảo mật
⚠️ **Token là bí mật - KHÔNG share công khai!**
- ❌ KHÔNG commit file `.env` lên GitHub
- ❌ KHÔNG paste token vào chat/forum công khai
- ✅ Thêm `.env` vào `.gitignore`
- ✅ Tạo token mới nếu bị leak

### 🤖 AI vs Commands
Bot vẫn hoạt động hoàn hảo **KHÔNG CẦN AI**:
- `/start` - Khởi động bot
- `/add` - Thêm task với menu
- `/list` - Xem danh sách
- `/remind` - Đặt reminder
- `/done`, `/delete`, `/clear` - Quản lý tasks

AI chỉ là **tính năng bổ sung** để UX tốt hơn!

## 🆘 Troubleshooting - Gặp lỗi?

### ❌ "GitHub token không hợp lệ" / API 401 Unauthorized

**Nguyên nhân:**
- Token sai format
- Token đã expired
- Token không có quyền

**Giải pháp:**
```bash
# 1. Check token trong .env
cat .env | grep GITHUB_TOKEN

# 2. Token phải bắt đầu bằng ghp_
# Ví dụ đúng: GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqr

# 3. Không có khoảng trắng thừa
# SAI:  GITHUB_TOKEN= ghp_xxx  (có space)
# ĐÚNG: GITHUB_TOKEN=ghp_xxx

# 4. Tạo token mới tại:
# https://github.com/settings/tokens
```

### ❌ API 429 - Rate Limit Exceeded

**Nguyên nhân:**
- Đã dùng hết 60 requests/phút
- Hoặc 150,000 tokens/ngày

**Giải pháp:**
```bash
# Đợi 1 phút hoặc 1 ngày
# Hoặc sử dụng commands thay vì AI tạm thời:
/add Task name
/remind [id] [time]
```

### ❌ Bot không phản hồi AI / Vẫn hiện "cần GitHub token"

**Check list:**
```bash
# 1. Verify .env file tồn tại
ls -la .env

# 2. Check nội dung .env
cat .env

# 3. Verify bot đã restart sau khi update .env
ps aux | grep task_bot

# 4. Check logs để xem lỗi gì
tail -f bot.log  # hoặc screen -r taskbot
```

**Common issues:**
- File .env không ở cùng folder với task_bot.py
- Typo trong tên biến (GITHUB_TOKEN chứ không phải GITHUB_API_TOKEN)
- Bot chưa được restart sau khi thêm token
- Token đã expire

### ❌ Bot reply chậm khi dùng AI

**Nguyên nhân:** 
- API call đến GitHub Models mất 1-3 giây
- Network latency

**Giải pháp:**
- Đây là bình thường! AI cần time để process
- Nếu quá chậm (>10s), check internet connection
- Hoặc dùng commands cho tasks khẩn cấp

### ❌ AI parse sai task hoặc thời gian

**Ví dụ:**
```
User: "Gọi bác sĩ 5h"
AI parse: "Gọi" + "5h" (sai!)
Mong muốn: "Gọi bác sĩ" + "5h" (đúng)
```

**Giải pháp:**
1. Dùng câu rõ ràng hơn: "Nhắc tôi gọi bác sĩ lúc 5 giờ chiều"
2. Hoặc dùng commands để chính xác 100%:
   ```
   /add Gọi bác sĩ
   /remind 1 17:00
   ```

### 🔧 Debug Commands

```bash
# Check Python environment
python3 --version

# Check dependencies
pip3 list | grep -E "pyTelegramBotAPI|requests|python-dotenv"

# Check bot process
ps aux | grep task_bot

# View real-time logs
tail -f bot.log

# Test GitHub token manually (Linux)
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://models.inference.ai.azure.com/info

# Restart bot properly
pkill -f task_bot.py && sleep 2 && screen -dmS taskbot python3 task_bot.py
```

---

## 📋 Quick Setup Guide (Copy & Paste)

### Setup AI trong 3 phút:

```bash
# 1. Lấy GitHub Token
# Truy cập: https://github.com/settings/tokens
# Click: Generate new token (classic)
# Copy token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 2. SSH vào server
ssh -p 5024 roo@15.235.210.238

# 3. Navigate to bot folder
cd task_bot

# 4. Edit .env
nano .env

# 5. Thêm dòng này (paste token của bạn):
# GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 6. Save: Ctrl+O, Enter, Ctrl+X

# 7. Restart bot
pkill -f task_bot.py
screen -dmS taskbot python3 task_bot.py

# 8. Test
# Gửi tin nhắn: "Mua sữa 5h chiều"
# Nếu thấy 🤖 emoji → AI đã hoạt động!
```

---

## 🎯 Summary

| Step | Action | Time |
|------|--------|------|
| 1️⃣ | Lấy GitHub token | 1 phút |
| 2️⃣ | Thêm vào .env | 30 giây |
| 3️⃣ | Restart bot | 30 giây |
| 4️⃣ | Test AI | 30 giây |
| **TOTAL** | **~3 phút** | ⚡ |

**Benefits:**
- ✅ Parse ngôn ngữ tự nhiên
- ✅ Auto extract task name + time
- ✅ Better user experience
- ✅ 100% MIỄN PHÍ

**Không bắt buộc** - Bot vẫn hoạt động tốt không có AI!

---

## 📚 Resources

- **GitHub Models**: https://github.com/marketplace/models
- **Token Settings**: https://github.com/settings/tokens  
- **API Documentation**: https://docs.github.com/en/rest
- **Bot Repository**: https://github.com/rambo247/task_bot

---

**Happy AI-powered Task Management!** 🤖✨

Need help? Check [SERVER_DEPLOY_GUIDE.md](SERVER_DEPLOY_GUIDE.md) hoặc xem bot logs!
