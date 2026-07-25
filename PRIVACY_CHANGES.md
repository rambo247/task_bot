# Cập nhật Bảo mật: Privacy cho Người dùng trong Nhóm

## Vấn đề
Trước đây, bot lưu trữ tasks theo `chat_id`, nghĩa là:
- **Trong chat cá nhân**: Mỗi user có chat_id riêng ✅ OK
- **Trong nhóm**: Tất cả thành viên chia sẻ cùng một chat_id ❌ VẤN ĐỀ BẢO MẬT

Kết quả: Khi nhiều người dùng bot trong cùng một nhóm, họ có thể xem và quản lý tasks của nhau!

## Giải pháp
Thay đổi từ `chat_id` sang `user_id` để đảm bảo:
- ✅ Mỗi user có danh sách tasks riêng tư
- ✅ Ngay cả trong nhóm, không ai xem được tasks của người khác
- ✅ Reminders được gửi tới đúng user (có thể là private chat hoặc group chat)

## Những thay đổi đã thực hiện

### 1. Thêm Helper Functions
```python
def get_user_id(message):
    """Lấy user ID từ message"""
    return message.from_user.id

def update_user_chat_mapping(message):
    """Cập nhật mapping user_id -> chat_id để gửi reminder"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    user_chat_mapping[user_id] = chat_id
```

### 2. Cập nhật Data Structures
```python
# Thay đổi từ:
user_tasks = {}  # Theo chat_id

# Sang:
user_tasks = {}  # Theo user_id
user_chat_mapping = {}  # Map user_id -> chat_id để gửi reminder
```

### 3. Các Command Handlers đã cập nhật
- ✅ `/start` - Đã sửa
- ✅ `/help` - Không cần sửa (không dùng user_tasks)
- ✅ `/timezone` - Đã sửa
- ✅ `/add` - Đã sửa
- ✅ `/list` - Đã sửa
- ✅ `/done` - Đã sửa
- ✅ `/remind` - Đã sửa
- ✅ `/delete` - Đã sửa
- ✅ `/clear` - Đã sửa (partially)
- ✅ `/cancel` - Đã sửa

### 4. Reminder System
```python
def reminder_checker():
    # Đã thay đổi để lặp qua user_id thay vì chat_id
    for user_id, tasks in list(user_tasks.items()):
        # Lấy chat_id từ mapping để gửi message
        chat_id = user_chat_mapping.get(user_id)
```

### 5. Các hàm đã cập nhật
- ✅ `get_user_timezone(user_id)` - Đã sửa
- ✅ `get_user_time(user_id, utc_time)` - Đã sửa
- ✅ `to_utc_time(user_id, local_time)` - Đã sửa
- ✅ `create_calendar(user_id, year, month)` - Đã sửa
- ✅ `create_time_picker(user_id, selected_date, selected_hour)` - Đã sửa
- ✅ `show_main_menu(user_id, message_text)` - Đã sửa
- ✅ `show_task_list(user_id, chat_id, message_id)` - Đã sửa (thêm tham số chat_id)
- ✅ `parse_time(time_str, user_id)` - Đã sửa

## Những phần CẦN HOÀN THIỆN

### Callback Handler (callback_handler)
Trong hàm `@bot.callback_query_handler`, cần thay thế TẤT CẢ các:
- `user_tasks[chat_id]` → `user_tasks[user_id]`
- `user_states[chat_id]` → `user_states[user_id]`
- `get_user_time(chat_id` → `get_user_time(user_id`
- `to_utc_time(chat_id` → `to_utc_time(user_id`
- `get_user_timezone(chat_id)` → `get_user_timezone(user_id)`
- `show_task_list(chat_id, message_id)` → `show_task_list(user_id, chat_id, message_id)`

Các phần đã sửa trong callback_handler:
- ✅ Phần đầu hàm (lấy user_id, chat_id)
- ✅ menu_main, menu_add, menu_list - Đã sửa
- ✅ menu_timezone, tz_ handlers - Đã sửa  
- ✅ task_done, task_remind, task_delete - Đã sửa (partially)
- ⚠️ Calendar handlers - CẦN kiểm tra lại
- ⚠️ Time picker handlers - CẦN sửa
- ⚠️ Clear handlers - CẦN sửa

### Handle User Input (handle_user_input)
Trong hàm `@bot.message_handler(func=lambda...)`, cần thay thế:
- `user_tasks[chat_id]` → `user_tasks[user_id]`
- `user_states[chat_id]` → `user_states[user_id]`
- Và các hàm get_user_time, to_utc_time tương ứng

Đã sửa:
- ✅ Đầu hàm (lấy user_id, chat_id, update mapping)
- ⚠️ waiting_task_content - CẦN sửa
- ⚠️ manual_time_input - CẦN sửa
- ⚠️ manual_minute_input - CẦN sửa
- ⚠️ waiting_remind_time - CẦN sửa

### Natural Language Handler
Hàm `handle_natural_language` - CẦN cập nhật hoàn toàn

### AI Functions
- `parse_natural_language_task(user_text, user_id)` - CẦN kiểm tra

## Cách hoàn thiện phần còn lại

### Phương pháp 1: Tìm kiếm và thay thế thủ công
```bash
# Tìm tất cả các trường hợp còn lại
grep -n "user_tasks\[chat_id\]" task_bot.py
grep -n "user_states\[chat_id\]" task_bot.py
grep -n "get_user_time(chat_id" task_bot.py
grep -n "to_utc_time(chat_id" task_bot.py
grep -n "show_task_list(chat_id" task_bot.py
```

### Phương pháp 2: Tìm và thay thế trong Editor
1. Mở task_bot.py trong VS Code
2. Nhấn Ctrl+H để mở Find & Replace
3. Thay thế từng pattern một:
   - `user_tasks[chat_id]` → `user_tasks[user_id]`
   - `user_states[chat_id]` → `user_states[user_id]`
   - `get_user_time(chat_id` → `get_user_time(user_id`
   - `to_utc_time(chat_id` → `to_utc_time(user_id`
   - `show_task_list(chat_id, ` → `show_task_list(user_id, chat_id, `

⚠️ **LƯU Ý**: Trong callback_handler, cần đảm bảo:
```python
user_id = call.from_user.id
chat_id = call.message.chat.id
user_chat_mapping[user_id] = chat_id
```

## Kiểm tra sau khi hoàn thiện

### Test Cases

1. **Test trong Private Chat**
```
- Gửi /start
- Thêm task: "Task riêng tư 1"
- Đặt reminder
- Kiểm tra chỉ user này thấy task của mình
```

2. **Test trong Group Chat**
```
- User A: /start trong group
- User A: Thêm task "Task của A"
- User B: /start trong group  
- User B: /list (không được thấy task của A)
- User B: Thêm task "Task của B"
- User A: /list (chỉ thấy task của A, không thấy task của B)
```

3. **Test Reminder**
```
- Thêm task với reminder 1 phút
- Đợi 1 phút
- Kiểm tra reminder được gửi đúng user (có thể là private hoặc group chat tùy nơi user tương tác)
```

## Lợi ích

✅ **Privacy**: Mỗi user có danh sách riêng tư
✅ **Multi-user**: Nhiều người dùng bot trong cùng một group không bị xung đột
✅ **Flexibility**: User có thể dùng bot ở cả private chat và group chat
✅ **Correct Reminders**: Reminder được gửi đúng user qua mapping

## Xem thêm
- [task_bot.py](task_bot.py) - File chính đã được cập nhật
- [replace_ids.py](replace_ids.py) - Script hỗ trợ thay thế (nếu có Python)
