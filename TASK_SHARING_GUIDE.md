# 📤 Hướng Dẫn Chia Sẻ Task

## 🎯 Tổng Quan

Tính năng chia sẻ task cho phép bạn gửi danh sách công việc cho đồng nghiệp, bạn bè hoặc thành viên team qua Telegram bot.

---

## ✨ Tính Năng

### 1️⃣ **Multiselect Với Checkbox**
- Chọn nhiều task cùng lúc
- Toggle ☐/☑ bằng 1 click
- Hiển thị số task đã chọn real-time

### 2️⃣ **Flexible Recipient**
- Gửi qua @username
- Gửi qua user_id
- Hoặc forward tin nhắn của người nhận

### 3️⃣ **Beautiful Format**
- Task list được format đẹp
- Hiển thị progress bar
- Hiển thị deadline/reminder
- Branding với bot name

### 4️⃣ **Smart Buttons**
- ☑ Chọn tất cả
- ☐ Bỏ chọn tất cả
- ✅ Xong (hiển thị số đã chọn)
- ❌ Hủy

---

## 📖 Cách Sử Dụng

### 🔹 Phương Pháp 1: Button (Khuyến nghị)

#### Bước 1: Mở Task List
```
/list
hoặc Menu → 📋 Quản Lý Task
```

#### Bước 2: Click Nút Chia Sẻ
```
Click [📤 Chia sẻ]
```

#### Bước 3: Chọn Tasks
```
📤 CHIA SẺ TASK

Đã chọn: 0/5

👇 Click để chọn/bỏ chọn task:

☐ 1. ⏳ Viết báo cáo Q4
☐ 2. ⏳ Họp team planning
☑ 3. ⏳ Review code PR #123  ← Đã chọn
☐ 4. ✅ Deploy production
☐ 5. ⏳ Testing tính năng X

[☑ Chọn tất cả]
[✅ Xong (1)] [❌ Hủy]
```

#### Bước 4: Hoàn Tất Chọn
```
Click [✅ Xong (3)] khi đã chọn đủ
```

#### Bước 5: Nhập Người Nhận
```
📤 GỬI TASK

Đã chọn 3 task.

Nhập username người nhận:
• Nhập: @username
• Hoặc: user_id (số)
• Hoặc: Forward tin nhắn của họ

Ví dụ: @john_doe
```

#### Bước 6: Xác Nhận
```
You: @john_doe

Bot: ✅ Đã gửi thành công!

📤 Gửi tới: @john_doe
📦 Số task: 3

Người nhận sẽ thấy danh sách task trong chat với bot.
```

---

### 🔹 Phương Pháp 2: Command

#### Quick Share
```
/share
```

Sau đó làm theo các bước tương tự như phương pháp 1.

---

## 📋 Format Khi Gửi

Người nhận sẽ thấy:

```
📋 DANH SÁCH CÔNG VIỆC ĐƯỢC CHIA SẺ

1. ⏳ Viết báo cáo Q4
   📊 █████░░░░░ 50%
   ⏰ Deadline: 25/08/2026 14:00

2. ⏳ Họp team planning
   📊 ░░░░░░░░░░ 0%
   ⏰ Deadline: 20/08/2026 09:00

3. ⏳ Review code PR #123
   📊 ███░░░░░░░ 30%

📤 Được chia sẻ bởi @PHT_TASK_BOT
```

---

## 🎯 Use Cases

### 1. **Team Collaboration**
```
Scenario: PM chia sẻ sprint tasks cho dev team

1. PM chọn các task trong sprint
2. Gửi cho @dev_team_lead
3. Lead review và assign
```

### 2. **Daily Standup**
```
Scenario: Share tasks đang làm với team

1. Chọn tasks "Đang làm"
2. Gửi vào group chat
3. Team members biết bạn đang làm gì
```

### 3. **Client Reporting**
```
Scenario: Báo cáo tiến độ cho khách hàng

1. Chọn tasks của project X
2. Gửi cho client
3. Client thấy progress real-time
```

### 4. **Task Delegation**
```
Scenario: Manager delegate tasks

1. Chọn tasks cần assign
2. Gửi cho team member
3. Member nhận và thực hiện
```

---

## 🔒 Điều Kiện & Giới Hạn

### ✅ Có thể gửi cho:
- ✅ User đã /start bot
- ✅ User trong danh bạ bot (user_chat_mapping)
- ✅ User có username công khai

### ❌ Không gửi được cho:
- ❌ User chưa /start bot
- ❌ User đã block bot
- ❌ User không có trong danh bạ
- ❌ Username không tồn tại

### 💡 Giải pháp:
Yêu cầu người nhận gửi `/start` cho bot trước khi share.

---

## 🛠️ Advanced Features

### Select All
```
Click [☑ Chọn tất cả]

Kết quả:
☑ 1. ⏳ Task A
☑ 2. ⏳ Task B
☑ 3. ⏳ Task C
☑ 4. ✅ Task D
☑ 5. ⏳ Task E

Đã chọn: 5/5
```

### Deselect All
```
Click [☐ Bỏ chọn tất cả]

Kết quả:
☐ 1. ⏳ Task A
☐ 2. ⏳ Task B
☐ 3. ⏳ Task C
☐ 4. ✅ Task D
☐ 5. ⏳ Task E

Đã chọn: 0/5
```

### Toggle Individual
```
Click vào từng task để toggle:

☐ → ☑ (chọn)
☑ → ☐ (bỏ chọn)
```

---

## 📊 Demo Flow

### Ví Dụ Đầy Đủ:

```
👤 User A: /list
🤖 Bot:
📋 DANH SÁCH CÔNG VIỆC:

1. ⏳ Task Alpha
2. ⏳ Task Beta
3. ⏳ Task Gamma

[📤 Chia sẻ]

👤 User A: Click [📤 Chia sẻ]
🤖 Bot:
📤 CHIA SẺ TASK

Đã chọn: 0/3

☐ 1. ⏳ Task Alpha
☐ 2. ⏳ Task Beta
☐ 3. ⏳ Task Gamma

[☑ Chọn tất cả] [❌ Hủy]

👤 User A: Click Task 1
🤖 Bot:
Đã chọn: 1/3

☑ 1. ⏳ Task Alpha  ← Selected
☐ 2. ⏳ Task Beta
☐ 3. ⏳ Task Gamma

[✅ Xong (1)] [❌ Hủy]

👤 User A: Click Task 3
🤖 Bot:
Đã chọn: 2/3

☑ 1. ⏳ Task Alpha
☐ 2. ⏳ Task Beta
☑ 3. ⏳ Task Gamma  ← Selected

[✅ Xong (2)] [❌ Hủy]

👤 User A: Click [✅ Xong (2)]
🤖 Bot:
📤 GỬI TASK

Đã chọn 2 task.

Nhập username người nhận:
Ví dụ: @john_doe

👤 User A: @user_b
🤖 Bot:
✅ Đã gửi thành công!

📤 Gửi tới: @user_b
📦 Số task: 2

---

📱 User B receives:
🤖 Bot → User B:
📋 DANH SÁCH CÔNG VIỆC ĐƯỢC CHIA SẺ

1. ⏳ Task Alpha
   📊 █████░░░░░ 50%

2. ⏳ Task Gamma
   📊 ███░░░░░░░ 30%

📤 Được chia sẻ bởi @PHT_TASK_BOT
```

---

## 🔍 Xác Định Người Nhận

### Cách 1: @username
```
Input: @john_doe
Bot tìm user có username = "john_doe"
```

### Cách 2: user_id
```
Input: 123456789
Bot tìm user có user_id = 123456789
```

### Cách 3: Forward Message
```
Forward bất kỳ tin nhắn nào của người nhận
Bot tự động lấy user_id từ forward
```

---

## ⚠️ Error Handling

### Error 1: User Chưa Start Bot
```
❌ User @john_doe chưa từng chat với bot.

Lưu ý: Bot chỉ gửi được cho user đã từng chat với bot.

Vui lòng:
1. Yêu cầu họ gửi /start cho bot trước
2. Hoặc nhập user_id của họ
3. Hoặc forward tin nhắn của họ
```

**Giải pháp:**
Yêu cầu người nhận gửi `/start` cho @PHT_TASK_BOT

### Error 2: Username Không Tồn Tại
```
⚠️ Không tìm thấy user @john_doe

Lưu ý: Bot chỉ gửi được cho user đã từng chat với bot.
```

**Giải pháp:**
- Kiểm tra lại username
- Hoặc dùng user_id
- Hoặc forward message

### Error 3: Định Dạng Sai
```
⚠️ Định dạng không hợp lệ!

Vui lòng nhập:
• @username
• user_id (số)
• Hoặc forward tin nhắn của họ
```

**Giải pháp:**
Nhập đúng format theo hướng dẫn

### Error 4: Bot Bị Block
```
❌ Lỗi khi gửi:
Forbidden: bot was blocked by the user

Có thể người nhận đã block bot hoặc chưa start bot.
```

**Giải pháp:**
Yêu cầu người nhận unblock và /start bot

---

## 💡 Tips & Tricks

### Tip 1: Share Nhanh
```
/share → Select All → Done → @username
```

### Tip 2: Share Theo Filter
```
1. Filter tasks (menu → pending/done)
2. Share các task đã filter
```

### Tip 3: Share Template
```
Lưu list username thường dùng:
@team_lead
@dev_john
@qa_mary
```

### Tip 4: Batch Share
```
Share cùng 1 list cho nhiều người:
1. Select tasks
2. Share cho @person_a
3. /share lại
4. Select tương tự
5. Share cho @person_b
```

---

## 🎨 UI Components

### Checkbox States:
- ☐ = Not selected
- ☑ = Selected

### Task Status Icons:
- ⏳ = Pending
- ✅ = Done

### Progress Bar:
- █ = Completed portion
- ░ = Remaining portion

### Action Buttons:
- 📤 = Share
- ☑ = Select all
- ☐ = Deselect all
- ✅ = Done/Confirm
- ❌ = Cancel

---

## 🔧 Technical Details

### Data Flow:
```
User selects tasks
    ↓
Store selected_indices in callback_data
    ↓
User clicks Done
    ↓
Bot asks for recipient
    ↓
User inputs @username or user_id
    ↓
Bot resolves to chat_id via user_chat_mapping
    ↓
Format tasks with format_tasks_for_sharing()
    ↓
Send via bot.send_message(recipient_chat_id)
    ↓
Confirm to sender
```

### Callback Pattern:
```python
share_start           # Enter share mode
share_toggle_{idx}_   # Toggle task selection
share_all             # Select all
share_none            # Deselect all
share_done_{indices}  # Finish selection
```

### State Pattern:
```python
waiting_share_recipient_{indices}  # Waiting for recipient input
```

---

## 📚 Related Commands

- `/list` - View task list
- `/share` - Quick share
- `/add` - Add new task
- `/progress` - Update progress
- `/done` - Mark done

---

## 🚀 Version Info

- **Feature:** Task Sharing
- **Version:** 2.5.0
- **Commit:** 6a8fc7c
- **Deploy Date:** 2026-08-06
- **Status:** ✅ Production Ready

---

## 📞 Support

Có vấn đề? Gửi `/help` hoặc `/start`

---

**💡 Pro Tip:** Tạo group chat với bot + team members để share tasks dễ dàng hơn! 🎯✨
