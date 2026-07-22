import telebot
import os
import threading
import time
from datetime import datetime, timedelta
from telebot import types

# Lấy token từ biến môi trường hoặc sử dụng token mặc định
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8802370170:AAEGZU_Df5OnDQTO7kn9lyf2UzeIbbh2KPk')
bot = telebot.TeleBot(TOKEN)

# Lưu trữ danh sách task tạm thời theo Chat ID
user_tasks = {}

# Lưu trữ timezone offset của mỗi user (theo giờ, mặc định GMT+7 cho Việt Nam)
user_timezones = {}

# Lưu trữ trạng thái người dùng (đang thêm task, đặt reminder, etc.)
user_states = {}

# Các timezone phổ biến
TIMEZONES = {
    'VN': 7,    # Việt Nam (GMT+7)
    'TH': 7,    # Thái Lan
    'SG': 8,    # Singapore
    'JP': 9,    # Nhật Bản
    'KR': 9,    # Hàn Quốc
    'CN': 8,    # Trung Quốc
    'UTC': 0,   # UTC
    'GMT': 0,   # GMT
}

def get_user_timezone(chat_id):
    """Lấy timezone offset của user (mặc định GMT+7)"""
    return user_timezones.get(chat_id, 7)  # Mặc định Việt Nam GMT+7

def get_user_time(chat_id, utc_time=None):
    """Chuyển UTC time sang giờ của user"""
    if utc_time is None:
        utc_time = datetime.utcnow()
    offset = get_user_timezone(chat_id)
    return utc_time + timedelta(hours=offset)

def to_utc_time(chat_id, local_time):
    """Chuyển giờ local của user sang UTC"""
    offset = get_user_timezone(chat_id)
    return local_time - timedelta(hours=offset)

# Background thread để kiểm tra và gửi reminder
def reminder_checker():
    """Kiểm tra và gửi thông báo nhắc nhở"""
    while True:
        try:
            current_time = datetime.utcnow()  # Sử dụng UTC time
            for chat_id, tasks in list(user_tasks.items()):
                for task in tasks:
                    if task.get('remind_time') and not task.get('reminded'):
                        remind_time = task['remind_time']  # Đã lưu ở UTC
                        # Kiểm tra nếu đã đến giờ nhắc (trong vòng 1 phút)
                        if remind_time <= current_time < remind_time + timedelta(minutes=1):
                            try:
                                print(f"Sending reminder to chat_id {chat_id}: {task['content']}")
                                reminder_text = f"⏰ NHẮC NHỞ!\n\n📌 {task['content']}"
                                if task.get('done'):
                                    reminder_text += "\n\n✅ (Đã hoàn thành)"
                                bot.send_message(chat_id, reminder_text)
                                task['reminded'] = True
                                print(f"Reminder sent successfully to chat_id {chat_id}")
                            except Exception as e:
                                print(f"Error sending reminder: {e}")
            time.sleep(30)  # Kiểm tra mỗi 30 giây
        except Exception as e:
            print(f"Error in reminder_checker: {e}")
            time.sleep(30)

# Khởi động background thread
reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
reminder_thread.start()

def show_main_menu(chat_id, message_text="👋 Xin chào! Tôi là bot nhắc việc của bạn."):
    """Hiển thị menu chính với các nút"""
    tz = get_user_timezone(chat_id)
    text = f"{message_text}\n\n🌍 Múi giờ: GMT+{tz}\n\n📱 Chọn chức năng:"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_add = types.InlineKeyboardButton("➕ Thêm công việc", callback_data="menu_add")
    btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
    btn_timezone = types.InlineKeyboardButton("🌍 Đặt múi giờ", callback_data="menu_timezone")
    btn_help = types.InlineKeyboardButton("❓ Hướng dẫn", callback_data="menu_help")
    
    markup.add(btn_add, btn_list)
    markup.add(btn_timezone, btn_help)
    
    return text, markup

# Lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
    print(f"Received /start from chat_id: {bot_message.chat.id}")
    chat_id = bot_message.chat.id
    text, markup = show_main_menu(chat_id)
    bot.send_message(chat_id, text, reply_markup=markup)

# Lệnh /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📚 HƯỚNG DẪN SỬ DỤNG BOT\n\n"
        "🎯 SỬ DỤNG MENU:\n"
        "• Nhấn các nút trên menu để thao tác nhanh\n"
        "• Không cần gõ lệnh phức tạp\n\n"
        "⏰ ĐỊNH DẠNG THỜI GIAN:\n"
        "• 14:30 - Hôm nay lúc 14:30\n"
        "• 2m - Sau 2 phút\n"
        "• 30m - Sau 30 phút\n"
        "• 2h - Sau 2 giờ\n"
        "• 2026-07-23 09:00 - Ngày giờ cụ thể\n\n"
        "🌍 MÚI GIỜ:\n"
        "• Bot tự động chuyển đổi thời gian\n"
        "• Đặt múi giờ: VN, TH, SG, JP, KR...\n\n"
        "💡 MẸO:\n"
        "• Dùng menu để thao tác nhanh hơn\n"
        "• Thời gian hiển thị theo múi giờ của bạn"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🔙 Quay lại menu", callback_data="menu_main")
    markup.add(btn_back)
    
    bot.send_message(message.chat.id, help_text, reply_markup=markup)

# Lệnh /timezone để đặt múi giờ
@bot.message_handler(commands=['timezone'])
def set_timezone(message):
    print(f"Received /timezone from chat_id: {message.chat.id}")
    chat_id = message.chat.id
    
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            # Hiển thị timezone hiện tại và hướng dẫn
            current_tz = get_user_timezone(chat_id)
            tz_list = "\n".join([f"   {code} = GMT+{offset}" for code, offset in sorted(TIMEZONES.items(), key=lambda x: x[1])])
            bot.reply_to(message,
                f"🌍 Múi giờ hiện tại: GMT+{current_tz}\n\n"
                f"📝 Cách đặt múi giờ:\n"
                f"/timezone VN (Việt Nam)\n"
                f"/timezone GMT+7\n"
                f"/timezone +8\n\n"
                f"🌐 Các múi giờ phổ biến:\n{tz_list}")
            return
        
        tz_input = args[1].strip().upper()
        
        # Kiểm tra nếu là mã quốc gia
        if tz_input in TIMEZONES:
            user_timezones[chat_id] = TIMEZONES[tz_input]
            bot.reply_to(message, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_input]} ({tz_input})")
            return
        
        # Kiểm tra định dạng GMT+X hoặc +X
        if tz_input.startswith('GMT'):
            tz_input = tz_input[3:]
        
        if tz_input.startswith('+') or tz_input.startswith('-'):
            offset = int(tz_input)
            if -12 <= offset <= 14:
                user_timezones[chat_id] = offset
                bot.reply_to(message, f"✅ Đã đặt múi giờ: GMT{tz_input:+d}")
            else:
                bot.reply_to(message, "⚠️ Múi giờ không hợp lệ! Vui lòng chọn từ GMT-12 đến GMT+14")
        else:
            bot.reply_to(message, 
                "⚠️ Định dạng không hợp lệ!\n\n"
                "Sử dụng: /timezone VN hoặc /timezone +7")
    
    except (ValueError, IndexError):
        bot.reply_to(message, 
            "⚠️ Lỗi định dạng!\n\n"
            "Ví dụ: /timezone VN hoặc /timezone +7")

# Lệnh /add để thêm task
@bot.message_handler(commands=['add'])
def add_task(message):
    print(f"Received /add from chat_id: {message.chat.id}")
    chat_id = message.chat.id
    # Lấy nội dung sau lệnh /add
    task_content = message.text[len('/add '):].strip()
    
    if not task_content:
        # Chuyển sang chế độ hỏi nội dung
        user_states[chat_id] = "waiting_task_content"
        bot.reply_to(message, 
            "✍️ Nhập nội dung công việc:\n\n"
            "(Ví dụ: Họp team lúc 9h sáng)")
        return

    if chat_id not in user_tasks:
        user_tasks[chat_id] = []
    
    user_tasks[chat_id].append({
        'content': task_content, 
        'done': False,
        'remind_time': None,
        'reminded': False
    })
    
    # Hiển thị với menu buttons
    markup = types.InlineKeyboardMarkup()
    btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{len(user_tasks[chat_id])-1}")
    btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
    btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="menu_add")
    markup.add(btn_remind)
    markup.add(btn_list, btn_add)
    
    bot.reply_to(message,
        f"✅ Đã thêm: '{task_content}'",
        reply_markup=markup
    )

# Lệnh /list để xem danh sách task
@bot.message_handler(commands=['list'])
def list_tasks(message):
    chat_id = message.chat.id
    show_task_list(chat_id)

# Lệnh /done để đánh dấu hoàn thành
@bot.message_handler(commands=['done'])
def mark_done(message):
    chat_id = message.chat.id
    
    if chat_id not in user_tasks or not user_tasks[chat_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        task_number = int(message.text.split()[1])
        if 1 <= task_number <= len(user_tasks[chat_id]):
            user_tasks[chat_id][task_number - 1]['done'] = True
            bot.reply_to(message, f"✅ Đã đánh dấu hoàn thành: '{user_tasks[chat_id][task_number - 1]['content']}'")
        else:
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[chat_id])}")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Vui lòng nhập số thứ tự công việc.\n\nVí dụ: /done 1")

# Lệnh /remind để đặt nhắc nhở
@bot.message_handler(commands=['remind'])
def set_reminder(message):
    print(f"Received /remind from chat_id: {message.chat.id}")
    chat_id = message.chat.id
    
    if chat_id not in user_tasks or not user_tasks[chat_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, 
                "⚠️ Vui lòng nhập đúng định dạng:\n\n"
                "/remind [số] [thời gian]\n\n"
                "Ví dụ:\n"
                "/remind 1 14:30\n"
                "/remind 1 2026-07-23 09:00\n"
                "/remind 1 30m\n"
                "/remind 1 2h")
            return
        
        task_number = int(parts[1])
        time_str = parts[2]
        
        if task_number < 1 or task_number > len(user_tasks[chat_id]):
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[chat_id])}")
            return
        
        # Parse thời gian (với timezone của user)
        remind_time = parse_time(time_str, chat_id)
        
        if remind_time is None:
            bot.reply_to(message, 
                "⚠️ Định dạng thời gian không hợp lệ!\n\n"
                "Các định dạng hỗ trợ:\n"
                "• HH:MM (ví dụ: 14:30)\n"
                "• YYYY-MM-DD HH:MM\n"
                "• 30m (sau 30 phút)\n"
                "• 2h (sau 2 giờ)")
            return
        
        if remind_time <= datetime.utcnow():
            bot.reply_to(message, "⚠️ Thời gian nhắc nhở phải là thời điểm trong tương lai!")
            return
        
        # Cập nhật reminder (lưu ở UTC)
        user_tasks[chat_id][task_number - 1]['remind_time'] = remind_time
        user_tasks[chat_id][task_number - 1]['reminded'] = False
        
        task_content = user_tasks[chat_id][task_number - 1]['content']
        # Hiển thị theo giờ local của user
        user_time = get_user_time(chat_id, remind_time)
        remind_str = user_time.strftime("%d/%m/%Y %H:%M")
        
        bot.reply_to(message, 
            f"⏰ Đã đặt nhắc nhở!\n\n"
            f"📌 Công việc: {task_content}\n"
            f"🕐 Thời gian: {remind_str} (GMT+{get_user_timezone(chat_id)})")
        
    except (IndexError, ValueError) as e:
        bot.reply_to(message, 
            "⚠️ Lỗi định dạng!\n\n"
            "Sử dụng: /remind [số] [thời gian]\n"
            "Ví dụ: /remind 1 14:30")

def parse_time(time_str, chat_id=None):
    """Parse nhiều định dạng thời gian (trả về UTC time)"""
    try:
        # Định dạng: 30m, 2h, 1d (relative time)
        if time_str.endswith('m'):
            minutes = int(time_str[:-1])
            return datetime.utcnow() + timedelta(minutes=minutes)  # UTC
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            return datetime.utcnow() + timedelta(hours=hours)  # UTC
        elif time_str.endswith('d'):
            days = int(time_str[:-1])
            return datetime.utcnow() + timedelta(days=days)  # UTC
        
        # Định dạng: HH:MM (hôm nay, theo giờ local của user)
        if ':' in time_str and len(time_str.split()) == 1:
            time_parts = time_str.split(':')
            if len(time_parts) == 2:
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                # Lấy giờ local của user
                user_now = get_user_time(chat_id) if chat_id else datetime.utcnow()
                remind_time = user_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Nếu thời gian đã qua trong ngày hôm nay, chuyển sang ngày mai
                if remind_time <= user_now:
                    remind_time += timedelta(days=1)
                
                # Chuyển sang UTC
                return to_utc_time(chat_id, remind_time) if chat_id else remind_time
        
        # Định dạng: YYYY-MM-DD HH:MM (theo giờ local của user)
        if len(time_str.split()) == 2:
            local_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            return to_utc_time(chat_id, local_time) if chat_id else local_time
        
        # Định dạng: DD/MM/YYYY HH:MM (theo giờ local của user)
        if '/' in time_str:
            local_time = datetime.strptime(time_str, "%d/%m/%Y %H:%M")
            return to_utc_time(chat_id, local_time) if chat_id else local_time
        
        return None
    except:
        return None

# Lệnh /delete để xóa một task
@bot.message_handler(commands=['delete'])
def delete_task(message):
    chat_id = message.chat.id
    
    if chat_id not in user_tasks or not user_tasks[chat_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        task_number = int(message.text.split()[1])
        if 1 <= task_number <= len(user_tasks[chat_id]):
            deleted_task = user_tasks[chat_id].pop(task_number - 1)
            bot.reply_to(message, f"🗑️ Đã xóa công việc: '{deleted_task['content']}'")
        else:
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[chat_id])}")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Vui lòng nhập số thứ tự công việc.\n\nVí dụ: /delete 1")

# Lệnh /clear để xóa danh sách
@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    chat_id = message.chat.id
    
    if chat_id not in user_tasks or not user_tasks[chat_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đã trống!")
        return
        
    # Tạo inline keyboard để xác nhận
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Có", callback_data="clear_yes"),
        types.InlineKeyboardButton("❌ Không", callback_data="clear_no")
    )
    bot.reply_to(message, "⚠️ Bạn có chắc chắn muốn xóa toàn bộ danh sách công việc?", reply_markup=markup)

# Xử lý callback từ inline keyboard
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    print(f"Received callback: {call.data} from chat_id: {chat_id}")
    
    # Menu chính
    if call.data == "menu_main":
        text, markup = show_main_menu(chat_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    # Thêm công việc
    elif call.data == "menu_add":
        user_states[chat_id] = "waiting_task_content"
        bot.edit_message_text(
            "✍️ Nhập nội dung công việc:\n\n"
            "(Ví dụ: Họp team lúc 9h sáng)",
            chat_id=chat_id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    # Xem danh sách
    elif call.data == "menu_list":
        if chat_id not in user_tasks or not user_tasks[chat_id]:
            markup = types.InlineKeyboardMarkup()
            btn_add = types.InlineKeyboardButton("➕ Thêm công việc đầu tiên", callback_data="menu_add")
            btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_main")
            markup.add(btn_add)
            markup.add(btn_back)
            bot.edit_message_text(
                "📭 Danh sách công việc của bạn đang trống!",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            show_task_list(chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    # Đặt múi giờ
    elif call.data == "menu_timezone":
        current_tz = get_user_timezone(chat_id)
        markup = types.InlineKeyboardMarkup(row_width=3)
        
        # Các nút timezone
        for code in ['VN', 'TH', 'SG', 'JP', 'KR', 'CN']:
            offset = TIMEZONES[code]
            btn = types.InlineKeyboardButton(
                f"{code} (GMT+{offset})",
                callback_data=f"tz_{code}"
            )
            markup.add(btn)
        
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_main")
        markup.add(btn_back)
        
        bot.edit_message_text(
            f"🌍 Múi giờ hiện tại: GMT+{current_tz}\n\n"
            f"Chọn múi giờ của bạn:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    # Xử lý chọn timezone
    elif call.data.startswith("tz_"):
        tz_code = call.data[3:]
        if tz_code in TIMEZONES:
            user_timezones[chat_id] = TIMEZONES[tz_code]
            bot.answer_callback_query(call.id, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_code]}")
            text, markup = show_main_menu(chat_id, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_code]}")
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
    
    # Hướng dẫn
    elif call.data == "menu_help":
        help_text = (
            "📚 HƯỚNG DẪN SỬ DỤNG BOT\n\n"
            "🎯 SỬ DỤNG MENU:\n"
            "• Nhấn các nút trên menu để thao tác nhanh\n"
            "• Không cần gõ lệnh phức tạp\n\n"
            "⏰ ĐỊNH DẠNG THỜI GIAN:\n"
            "• 14:30 - Hôm nay lúc 14:30\n"
            "• 2m - Sau 2 phút\n"
            "• 30m - Sau 30 phút\n"
            "• 2h - Sau 2 giờ\n"
            "• 2026-07-23 09:00 - Ngày giờ cụ thể\n\n"
            "🌍 MÚI GIỜ:\n"
            "• Bot tự động chuyển đổi thời gian\n"
            "• Đặt múi giờ: VN, TH, SG, JP, KR...\n\n"
            "💡 MẸO:\n"
            "• Dùng menu để thao tác nhanh hơn\n"
            "• Thời gian hiển thị theo múi giờ của bạn"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại menu", callback_data="menu_main")
        markup.add(btn_back)
        bot.edit_message_text(help_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    # Xử lý action cho từng task
    elif call.data.startswith("task_"):
        parts = call.data.split("_")
        action = parts[1]
        task_idx = int(parts[2])
        
        if chat_id not in user_tasks or task_idx >= len(user_tasks[chat_id]):
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")
            return
        
        if action == "done":
            user_tasks[chat_id][task_idx]['done'] = True
            bot.answer_callback_query(call.id, "✅ Đã hoàn thành!")
            show_task_list(chat_id, call.message.message_id)
        
        elif action == "remind":
            user_states[chat_id] = f"waiting_remind_time_{task_idx}"
            task_content = user_tasks[chat_id][task_idx]['content']
            bot.edit_message_text(
                f"⏰ Đặt nhắc nhở cho:\n'{task_content}'\n\n"
                f"Nhập thời gian (VD: 14:30, 2m, 30m, 2h):",
                chat_id=chat_id,
                message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id)
        
        elif action == "delete":
            deleted_task = user_tasks[chat_id].pop(task_idx)
            bot.answer_callback_query(call.id, f"🗑️ Đã xóa: {deleted_task['content']}")
            if user_tasks[chat_id]:
                show_task_list(chat_id, call.message.message_id)
            else:
                text, markup = show_main_menu(chat_id, "✅ Đã xóa task cuối cùng!")
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        
        elif action == "back":
            show_task_list(chat_id, call.message.message_id)
            bot.answer_callback_query(call.id)
    
    # Xóa tất cả
    elif call.data == "clear_yes":
        user_tasks[chat_id] = []
        text, markup = show_main_menu(chat_id, "🧹 Đã xóa toàn bộ danh sách công việc!")
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "clear_no":
        show_task_list(chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif call.data == "clear_all":
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("✅ Có, xóa hết", callback_data="clear_yes")
        btn_no = types.InlineKeyboardButton("❌ Không, giữ lại", callback_data="clear_no")
        markup.add(btn_yes, btn_no)
        bot.edit_message_text(
            "⚠️ Bạn có chắc chắn muốn xóa toàn bộ danh sách?",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)

def show_task_list(chat_id, message_id=None):
    """Hiển thị danh sách task với các nút action"""
    if chat_id not in user_tasks or not user_tasks[chat_id]:
        text = "📭 Danh sách trống!"
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_main")
        markup.add(btn_back)
    else:
        text = "📋 DANH SÁCH CÔNG VIỆC:\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, task in enumerate(user_tasks[chat_id]):
            status = "✅" if task['done'] else "⏳"
            task_text = f"{idx+1}. {status} {task['content']}"
            
            if task.get('remind_time'):
                user_time = get_user_time(chat_id, task['remind_time'])
                remind_str = user_time.strftime("%d/%m %H:%M")
                task_text += f"\n   ⏰ {remind_str}"
            
            text += task_text + "\n\n"
            
            # Nút action cho từng task
            btn_row = []
            if not task['done']:
                btn_row.append(types.InlineKeyboardButton(f"✅ {idx+1}", callback_data=f"task_done_{idx}"))
                btn_row.append(types.InlineKeyboardButton(f"⏰ {idx+1}", callback_data=f"task_remind_{idx}"))
            btn_row.append(types.InlineKeyboardButton(f"🗑️ {idx+1}", callback_data=f"task_delete_{idx}"))
            markup.row(*btn_row)
        
        # Nút action chung
        btn_add = types.InlineKeyboardButton("➕ Thêm mới", callback_data="menu_add")
        btn_clear = types.InlineKeyboardButton("🧹 Xóa tất cả", callback_data="clear_all")
        btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.row(btn_add, btn_clear)
        markup.add(btn_back)
    
    if message_id:
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

# Xử lý tin nhắn text từ user (thêm task, đặt reminder)
@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id])
def handle_user_input(message):
    chat_id = message.chat.id
    state = user_states[chat_id]
    print(f"Handling user input, state: {state}, text: {message.text}")
    
    # Thêm task
    if state == "waiting_task_content":
        task_content = message.text.strip()
        if chat_id not in user_tasks:
            user_tasks[chat_id] = []
        
        user_tasks[chat_id].append({
            'content': task_content,
            'done': False,
            'remind_time': None,
            'reminded': False
        })
        
        user_states[chat_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{len(user_tasks[chat_id])-1}")
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="menu_add")
        markup.add(btn_remind)
        markup.add(btn_list, btn_add)
        
        bot.reply_to(message, 
            f"✅ Đã thêm: '{task_content}'\n\n"
            f"Bạn muốn làm gì tiếp theo?",
            reply_markup=markup
        )
    
    # Đặt reminder
    elif state.startswith("waiting_remind_time_"):
        task_idx = int(state.split("_")[-1])
        time_str = message.text.strip()
        
        remind_time = parse_time(time_str, chat_id)
        
        if remind_time is None:
            bot.reply_to(message,
                "⚠️ Định dạng thời gian không hợp lệ!\n\n"
                "Thử lại (VD: 14:30, 2m, 30m, 2h):"
            )
            return
        
        if remind_time <= datetime.utcnow():
            bot.reply_to(message, "⚠️ Thời gian phải là tương lai!\n\nThử lại:")
            return
        
        user_tasks[chat_id][task_idx]['remind_time'] = remind_time
        user_tasks[chat_id][task_idx]['reminded'] = False
        user_states[chat_id] = None
        
        task_content = user_tasks[chat_id][task_idx]['content']
        user_time = get_user_time(chat_id, remind_time)
        remind_str = user_time.strftime("%d/%m/%Y %H:%M")
        
        markup = types.InlineKeyboardMarkup()
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.add(btn_list, btn_menu)
        
        bot.reply_to(message,
            f"⏰ Đã đặt nhắc nhở!\n\n"
            f"📌 {task_content}\n"
            f"🕐 {remind_str} (GMT+{get_user_timezone(chat_id)})",
            reply_markup=markup
        )

# Chạy bot
if __name__ == "__main__":
    print("🤖 Bot đang khởi động...")
    try:
        bot_info = bot.get_me()
        print(f"📱 Bot name: @{bot_info.username}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print("✅ Bot đã sẵn sàng và đang lắng nghe tin nhắn...")
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Lỗi khởi động bot: {e}")
