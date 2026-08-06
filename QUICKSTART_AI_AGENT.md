# 🚀 AI Task Agent - Quick Start Guide

## ⚡ Bắt Đầu Nhanh (5 Phút)

### 1️⃣ Kiểm Tra Files

Đảm bảo bạn có các files sau:
```
✅ ai_task_agent.py          - Core module
✅ task_bot.py                - Telegram Bot (đã tích hợp AI)
✅ demo_ai_agent.py           - Demo & Testing
✅ AI_TASK_AGENT_GUIDE.md     - Hướng dẫn đầy đủ
```

---

### 2️⃣ Test AI Agent (Không cần Bot)

```bash
# Test nhanh
python ai_task_agent.py

# Demo đầy đủ
python demo_ai_agent.py
```

**Chọn option 7** để chạy tất cả demos hoặc **option 6** để test tự do.

---

### 3️⃣ Sử Dụng Trên Telegram Bot

#### A. Đảm bảo Bot đang chạy
```bash
python task_bot.py
```

#### B. Trên Telegram, thử các lệnh:

**Cách 1: Đầy đủ thông tin ngay**
```
/smart_add Tên: Thiết kế landing page
Người làm: Nguyễn Văn A
Deadline: 2026-08-15
Nhóm: Marketing
```

**Cách 2: Ngắn gọn (Bot sẽ hỏi thêm)**
```
/smart_add Tạo campaign marketing mới
```

**Cách 3: Qua Menu**
```
/start → 📋 Quản Lý Task → 🤖 AI Smart Add
```

---

## 📋 3 Format Input Chính

### Format 1: Key-Value (Structured)
```
Tên: Phát triển API v2
Người làm: Trần Dev
Deadline: 2026-08-20
Nhóm: Tech
Status: Đang làm
Tiến độ: 30%
```

### Format 2: Natural Language
```
Họp team với Nguyễn Manager deadline 10/08 cho dự án Website
```

### Format 3: Bổ Sung Dần
```
User: Tạo task marketing
Bot: Ai là người phụ trách?
User: Lê Marketing
Bot: Deadline khi nào?
User: 25/08/2026
Bot: ✅ Đã lưu!
```

---

## 🎯 Ví Dụ Thực Tế

### Ví Dụ 1: Đầy đủ thông tin
```
/smart_add Tên: Review code sprint 5
Người làm: Phạm Developer
Deadline: 2026-08-18
Nhóm: Tech
Chi tiết: Review toàn bộ code trước khi merge
```

**Kết quả:**
```
✅ Tuyệt vời! Tôi đã ghi nhận đầy đủ thông tin:

📋 Mã: TEC-897
🏷️ Tên: Review code sprint 5
👤 Người làm: Phạm Developer
📅 Deadline: 2026-08-18
📊 Nhóm: Tech
⚡ Trạng thái: Đang làm
📈 Tiến độ: 0%

💪 Chúc bạn làm việc hiệu quả!
```

### Ví Dụ 2: Thiếu thông tin
```
/smart_add Thiết kế logo mới
```

**Bot hỏi:**
```
👤 Ai sẽ là người phụ trách cho công việc 'Thiết kế logo mới'?
```

**User trả lời:**
```
Nguyễn Designer
```

**Bot hỏi tiếp:**
```
📅 Hạn chót (deadline) của công việc này là khi nào?
(Ví dụ: 2026-08-15 hoặc 15/08/2026)
```

**User trả lời:**
```
22/08/2026
```

**Bot xác nhận:**
```
✅ Tuyệt vời! Tôi đã ghi nhận đầy đủ thông tin:
📋 Mã: CHU-445
...
```

---

## 🔧 Các Lệnh Chính

| Lệnh | Mô Tả |
|------|-------|
| `/smart_add` | Thêm task với AI Agent |
| `/ai_add` | Alias của `/smart_add` |
| `/start` | Menu chính (có nút AI Smart Add) |
| `/list` | Xem danh sách tasks |

---

## 📊 So Sánh `/add` vs `/smart_add`

| Tính năng | `/add` | `/smart_add` |
|-----------|--------|--------------|
| Format | Tự do | Structured |
| Thông tin | Cơ bản | Chi tiết (8 fields) |
| Tự động hỏi | ❌ | ✅ |
| Mã task | ❌ | ✅ Auto |
| Tiến độ % | ❌ | ✅ |
| Phân nhóm | ❌ | ✅ |

---

## 🎓 Tips & Tricks

### Tip 1: Copy-Paste Template
Tạo template sẵn để dùng nhanh:
```
Tên: [TÊN TASK]
Người làm: [TÊN NGƯỜI]
Deadline: [YYYY-MM-DD]
Nhóm: [TÊN NHÓM]
```

### Tip 2: Dùng Ngắn Gọn
```
/smart_add Meeting với @User ngày 15/08
```
Bot sẽ tự parse và hỏi thêm nếu cần.

### Tip 3: JSON cho Dev
```
/smart_add {"task_name": "Deploy v2.0", "assignee": "DevOps", "deadline": "2026-08-30"}
```

---

## ❓ FAQ

**Q: Bot không nhận diện được thông tin?**  
A: Thử format Key-Value rõ ràng:
```
Tên: xxx
Người làm: yyy
Deadline: zzz
```

**Q: Deadline format nào được hỗ trợ?**  
A: 
- `YYYY-MM-DD` (2026-08-15)
- `DD/MM/YYYY` (15/08/2026)
- `DD/MM` (15/08 - năm hiện tại)

**Q: Có thể tùy chỉnh trạng thái?**  
A: Hiện hỗ trợ: "Đang làm", "Hoàn thành", "Bị trễ", "Cần hỗ trợ"

**Q: Task code tự tạo như thế nào?**  
A: Dùng 3 chữ cái đầu của task_group + số random (ví dụ: MAR-732, TEC-443)

---

## 🐛 Troubleshooting

### Lỗi: Bot không phản hồi
1. Check bot đang chạy: `python task_bot.py`
2. Check file `ai_task_agent.py` cùng thư mục
3. Check console logs

### Lỗi: Import Error
```bash
# Install dependencies
pip install pyTelegramBotAPI python-dotenv
```

### Lỗi: Parse sai thông tin
- Dùng format Key-Value rõ ràng
- Hoặc nhập từng phần qua conversation

---

## 📚 Tài Liệu Đầy Đủ

Đọc thêm:
- **AI_TASK_AGENT_GUIDE.md** - Hướng dẫn chi tiết
- **AI_TASK_AGENT_COMPLETE.md** - Tổng kết toàn bộ

---

## 🎉 Chúc Mừng!

Bạn đã sẵn sàng sử dụng AI Task Agent!

**Next Steps:**
1. ✅ Test với `demo_ai_agent.py`
2. ✅ Thử trên Telegram với `/smart_add`
3. ✅ Tạo task cho team của bạn
4. ✅ Tùy chỉnh theo nhu cầu

💪 **Chúc bạn làm việc hiệu quả!**

---

**Version:** 1.0.0  
**Last Updated:** 2026-08-06  
**Support:** [AI_TASK_AGENT_GUIDE.md](AI_TASK_AGENT_GUIDE.md)
