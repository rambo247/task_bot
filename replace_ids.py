import re

# Đọc file
with open('f:/workspace12/task_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Tìm và thay thế trong callback_handler
# Chỉ thay thế từ dòng callback_handler trở đi
parts = content.split('@bot.callback_query_handler', 1)
if len(parts) == 2:
    before_callback = parts[0] + '@bot.callback_query_handler'
    callback_and_after = parts[1]
    
    # Tìm handler tiếp theo (message_handler hoặc function def ở level 0)
    next_handler_match = re.search(r'\n@bot\.message_handler', callback_and_after)
    if next_handler_match:
        callback_part = callback_and_after[:next_handler_match.start()]
        after_callback = callback_and_after[next_handler_match.start():]
    else:
        callback_part = callback_and_after
        after_callback = ''
    
    # Thay thế trong callback_part
    replacements = [
        (r'user_tasks\[chat_id\]', 'user_tasks[user_id]'),
        (r'user_states\[chat_id\]', 'user_states[user_id]'),
        (r'get_user_time\(chat_id', 'get_user_time(user_id'),
        (r'to_utc_time\(chat_id', 'to_utc_time(user_id'),
        (r'create_calendar\(chat_id', 'create_calendar(user_id'),
        (r'create_time_picker\(chat_id', 'create_time_picker(user_id'),
        (r'get_user_timezone\(chat_id\)', 'get_user_timezone(user_id)'),
    ]
    
    for pattern, replacement in replacements:
        callback_part = re.sub(pattern, replacement, callback_part)
    
    # Ghi lại file
    new_content = before_callback + callback_part + after_callback
    with open('f:/workspace12/task_bot.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ Đã thay thế tất cả chat_id thành user_id trong callback_handler')
else:
    print('❌ Không tìm thấy callback_handler')
