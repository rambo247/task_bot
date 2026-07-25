# 🎬 TEST SCENARIOS - Demo Privacy Features

## Scenario 1: Private Chat Test (5 phút)

### Mục đích
Kiểm tra bot hoạt động cơ bản trong private chat

### Các bước
1. Mở Telegram, tìm bot của bạn
2. Gửi: `/start`
3. Gửi: `/add Mua sữa lúc 5 giờ chiều`
4. Gửi: `/list`
5. Gửi: `/remind 1 17:00`
6. Đợi đến 5 giờ chiều, kiểm tra reminder

### Expected Results
- ✅ Bot reply với menu buttons
- ✅ Task được thêm thành công
- ✅ List hiển thị đúng task
- ✅ Reminder được đặt thành công
- ✅ Reminder được gửi đúng giờ

---

## Scenario 2: Group Privacy Test (10 phút) ⭐ QUAN TRỌNG

### Mục đích
**Kiểm tra privacy**: Verify mỗi user chỉ thấy tasks của mình

### Setup
- Tạo một group test mới
- Thêm bot vào group
- Cần 2 Telegram accounts khác nhau (User A và User B)

### Các bước

#### Phase 1: User A thêm tasks
```
User A gửi trong group: /start
User A gửi: /add Họp với CEO lúc 9h sáng
User A gửi: /add Gửi báo cáo tài chính
User A gửi: /list
```

**Expected**: User A thấy 2 tasks của mình

#### Phase 2: User B join và check
```
User B gửi trong group: /start
User B gửi: /list
```

**Expected**: User B thấy "📭 Danh sách trống!"
**❌ KHÔNG được thấy tasks của User A!**

#### Phase 3: User B thêm tasks của mình
```
User B gửi: /add Đi gym lúc 6 giờ chiều  
User B gửi: /add Mua quà sinh nhật bạn
User B gửi: /list
```

**Expected**: User B chỉ thấy 2 tasks của mình

#### Phase 4: Verify User A không thấy tasks của B
```
User A gửi: /list
```

**Expected**: User A vẫn chỉ thấy 2 tasks của mình (Họp CEO, Gửi báo cáo)
**❌ KHÔNG thấy tasks của User B (Gym, Mua quà)!**

### ✅ Test PASSED nếu:
- User A chỉ thấy tasks của A
- User B chỉ thấy tasks của B
- Không ai thấy được tasks của người khác

### ❌ Test FAILED nếu:
- User A thấy được tasks của User B
- User B thấy được tasks của User A
- Tasks bị trộn lẫn

---

## Scenario 3: Reminder Test trong Group (15 phút)

### Mục đích
Kiểm tra reminders được gửi đúng user

### Các bước

#### Setup reminders
```
User A gửi: /add Task A - Test reminder
User A gửi: /remind 1 1m  (reminder sau 1 phút)

User B gửi: /add Task B - Test reminder 2
User B gửi: /remind 1 2m  (reminder sau 2 phút)
```

#### Chờ và verify
- Sau 1 phút: Kiểm tra có reminder cho "Task A" xuất hiện trong group
- Sau 2 phút: Kiểm tra có reminder cho "Task B" xuất hiện trong group

### Expected Results
- ✅ Cả 2 reminders đều xuất hiện trong group
- ✅ Mỗi reminder đúng content của user đó
- ✅ Không bị nhầm lẫn reminders

---

## Scenario 4: Multi-user Operations Test (10 phút)

### Mục đích
Test các operations khác nhau của nhiều users

### Các bước

#### User A actions
```
/start
/add Task A1
/add Task A2
/add Task A3
/done 2  (mark task A2 as done)
/list
```
**Expected**: Thấy Task A1, ✅ Task A2, Task A3

#### User B actions (cùng lúc)
```
/start
/add Task B1
/list
```
**Expected**: Chỉ thấy Task B1

#### User A delete task
```
/delete 1  (delete Task A1)
/list
```
**Expected**: Thấy ✅ Task A2, Task A3 (Task A1 đã bị xóa)

#### User B check
```
/list
```
**Expected**: Vẫn thấy Task B1 (không ảnh hưởng bởi User A)

### ✅ Test PASSED nếu:
- Operations của User A không ảnh hưởng đến User B
- Mỗi user có state độc lập

---

## Scenario 5: Timezone Test (Optional)

### Các bước
```
User A: /timezone VN    (GMT+7)
User B: /timezone JP    (GMT+9)

User A: /add Task với reminder 14:00
User B: /add Task với reminder 14:00
```

### Expected Results
- User A nhận reminder lúc 14:00 giờ Việt Nam
- User B nhận reminder lúc 14:00 giờ Nhật Bản (khác 2 tiếng)

---

## Quick Checklist Test

Sử dụng checklist này để test nhanh:

### Private Chat
- [ ] `/start` hoạt động
- [ ] `/add` thêm task được
- [ ] `/list` hiển thị đúng
- [ ] `/done` mark task được
- [ ] `/delete` xóa task được
- [ ] `/remind` đặt reminder được

### Group Chat - Privacy
- [ ] User A thêm task
- [ ] User B không thấy task của A
- [ ] User B thêm task riêng
- [ ] User A không thấy task của B
- [ ] `/done` của A không ảnh hưởng B
- [ ] `/delete` của A không ảnh hưởng B

### Reminders
- [ ] Reminder được đặt thành công
- [ ] Reminder được gửi đúng giờ
- [ ] Reminder của A không gửi cho B
- [ ] Reminder của B không gửi cho A

---

## Nếu Test Fail

### Issue: Users thấy được tasks của nhau
❌ **Nghiêm trọng!** Có thể code chưa được cập nhật đúng

**Fix**: 
1. Kiểm tra lại file task_bot.py
2. Chạy lại `test.ps1`
3. Verify tất cả `user_tasks[user_id]` không phải `user_tasks[chat_id]`

### Issue: Reminders không được gửi
**Check**:
1. Bot có đang chạy không?
2. reminder_thread có được start không?
3. Thời gian hệ thống đúng chưa?

### Issue: Bot không reply trong group
**Check**:
1. Group Privacy = OFF trong @BotFather
2. Bot có quyền đọc messages trong group
3. Bot còn trong group không?

---

## Summary

**Minimum test cần chạy trước deploy:**
1. ✅ Scenario 2 - Privacy test (MUST)
2. ✅ Scenario 1 - Basic functionality
3. ✅ Scenario 3 - Reminders

**Total time**: ~25 phút

Nếu tất cả passed → **Sẵn sàng deploy!** 🚀
