import telebot
import os
import threading
import time
import calendar
import requests
import json
from datetime import datetime, timedelta
from telebot import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Lấy token từ biến môi trường hoặc sử dụng token mặc định
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8802370170:AAEGZU_Df5OnDQTO7kn9lyf2UzeIbbh2KPk')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # GitHub token cho AI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # OpenAI API key cho Whisper (Speech-to-Text)
bot = telebot.TeleBot(TOKEN)

# Lưu trữ danh sách task theo User ID (riêng tư cho mỗi user)
user_tasks = {}

# Lưu trữ timezone offset của mỗi user (theo giờ, mặc định GMT+7 cho Việt Nam)
user_timezones = {}

# Lưu trữ trạng thái người dùng (đang thêm task, đặt reminder, etc.)
user_states = {}

# Lưu trữ mapping user_id -> chat_id để gửi reminder
user_chat_mapping = {}

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

def get_user_id(message):
    """Lấy user ID từ message (để đảm bảo privacy trong group)"""
    return message.from_user.id

def update_user_chat_mapping(message):
    """Cập nhật mapping user_id -> chat_id để gửi reminder"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    user_chat_mapping[user_id] = chat_id

def get_user_timezone(user_id):
    """Lấy timezone offset của user (mặc định GMT+7)"""
    return user_timezones.get(user_id, 7)  # Mặc định Việt Nam GMT+7

def get_user_time(user_id, utc_time=None):
    """Chuyển UTC time sang giờ của user"""
    if utc_time is None:
        utc_time = datetime.utcnow()
    offset = get_user_timezone(user_id)
    return utc_time + timedelta(hours=offset)

def to_utc_time(user_id, local_time):
    """Chuyển giờ local của user sang UTC"""
    offset = get_user_timezone(user_id)
    return local_time - timedelta(hours=offset)

def create_calendar(user_id, year=None, month=None):
    """Tạo calendar keyboard để chọn ngày"""
    user_now = get_user_time(user_id)
    
    if year is None:
        year = user_now.year
    if month is None:
        month = user_now.month
    
    markup = types.InlineKeyboardMarkup(row_width=7)
    
    # Header với tên tháng và năm
    month_name = calendar.month_name[month]
    header = types.InlineKeyboardButton(
        f"📅 {month_name} {year}",
        callback_data="calendar_ignore"
    )
    markup.row(header)
    
    # Navigation buttons
    btn_prev = types.InlineKeyboardButton("◀️", callback_data=f"calendar_prev_{year}_{month}")
    btn_today = types.InlineKeyboardButton("📍 Hôm nay", callback_data=f"calendar_today")
    btn_next = types.InlineKeyboardButton("▶️", callback_data=f"calendar_next_{year}_{month}")
    markup.row(btn_prev, btn_today, btn_next)
    
    # Days of week header
    week_days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    markup.row(*[types.InlineKeyboardButton(day, callback_data="calendar_ignore") for day in week_days])
    
    # Calendar days
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="calendar_ignore"))
            else:
                # Kiểm tra nếu là ngày trong quá khứ
                date = datetime(year, month, day)
                if date.date() < user_now.date():
                    row.append(types.InlineKeyboardButton(str(day), callback_data="calendar_ignore"))
                else:
                    row.append(types.InlineKeyboardButton(
                        str(day),
                        callback_data=f"calendar_day_{year}_{month}_{day}"
                    ))
        markup.row(*row)
    
    # Quick select buttons
    btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="calendar_cancel")
    markup.row(btn_cancel)
    
    return markup

def create_time_picker(user_id, selected_date=None, selected_hour=None):
    """Tạo time picker keyboard để chọn giờ"""
    markup = types.InlineKeyboardMarkup(row_width=6)
    
    if selected_date:
        date_str = selected_date.strftime("%d/%m/%Y")
        header = types.InlineKeyboardButton(
            f"🕐 Chọn giờ - {date_str}",
            callback_data="time_ignore"
        )
        markup.row(header)
    else:
        header = types.InlineKeyboardButton("🕐 Chọn giờ", callback_data="time_ignore")
        markup.row(header)
    
    if selected_hour is None:
        # Chọn giờ (0-23)
        user_now = get_user_time(user_id)
        current_hour = user_now.hour if selected_date and selected_date.date() == user_now.date() else -1
        
        # Hiển thị giờ theo nhóm
        markup.row(*[types.InlineKeyboardButton("Giờ", callback_data="time_ignore")])
        
        hours_rows = []
        for h in range(24):
            if selected_date and selected_date.date() == user_now.date() and h < current_hour:
                continue  # Skip past hours for today
            hours_rows.append(types.InlineKeyboardButton(
                f"{h:02d}h",
                callback_data=f"time_hour_{h}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
            ))
        
        # Chia thành các hàng 6 nút
        for i in range(0, len(hours_rows), 6):
            markup.row(*hours_rows[i:i+6])
    else:
        # Chọn phút (0, 15, 30, 45)
        markup.row(*[types.InlineKeyboardButton("Phút", callback_data="time_ignore")])
        
        minutes = [0, 15, 30, 45]
        min_buttons = []
        for m in minutes:
            min_buttons.append(types.InlineKeyboardButton(
                f"{m:02d}",
                callback_data=f"time_minute_{selected_hour}_{m}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
            ))
        markup.row(*min_buttons)
        
        # Thêm các phút khác (5, 10, 20, 25, 35, 40, 50, 55)
        other_minutes = [5, 10, 20, 25, 35, 40, 50, 55]
        other_min_buttons = []
        for m in other_minutes:
            other_min_buttons.append(types.InlineKeyboardButton(
                f"{m:02d}",
                callback_data=f"time_minute_{selected_hour}_{m}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
            ))
        # Chia thành 2 hàng
        markup.row(*other_min_buttons[:4])
        markup.row(*other_min_buttons[4:])
        
        # Nút nhập thủ công
        btn_manual = types.InlineKeyboardButton(
            "✍️ Nhập chính xác (VD: 27)",
            callback_data=f"time_manual_minute_{selected_hour}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
        )
        markup.row(btn_manual)
        
        # Nút quay lại chọn giờ
        btn_back = types.InlineKeyboardButton("🔙 Chọn lại giờ", callback_data=f"time_back_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}")
        markup.row(btn_back)
    
    # Quick time buttons
    markup.row(types.InlineKeyboardButton("⏱️ 5 phút", callback_data="time_quick_5m"),
               types.InlineKeyboardButton("⏱️ 15 phút", callback_data="time_quick_15m"),
               types.InlineKeyboardButton("⏱️ 30 phút", callback_data="time_quick_30m"))
    markup.row(types.InlineKeyboardButton("⏱️ 1 giờ", callback_data="time_quick_1h"),
               types.InlineKeyboardButton("⏱️ 2 giờ", callback_data="time_quick_2h"),
               types.InlineKeyboardButton("⏱️ 3 giờ", callback_data="time_quick_3h"))
    
    # Nút nhập thủ công (nếu chưa chọn giờ hoặc đã chọn ngày)
    if selected_date:
        btn_manual_time = types.InlineKeyboardButton(
            "✍️ Nhập giờ (VD: 14:30)",
            callback_data=f"time_manual_full_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
        )
        markup.row(btn_manual_time)
    
    btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="time_cancel")
    markup.row(btn_cancel)
    
    return markup

# Background thread để kiểm tra và gửi reminder
def reminder_checker():
    """Kiểm tra và gửi thông báo nhắc nhở"""
    while True:
        try:
            current_time = datetime.utcnow()  # Sử dụng UTC time
            for user_id, tasks in list(user_tasks.items()):
                for task in tasks:
                    if task.get('remind_time') and not task.get('reminded'):
                        remind_time = task['remind_time']  # Đã lưu ở UTC
                        # Kiểm tra nếu đã đến giờ nhắc (trong vòng 1 phút)
                        if remind_time <= current_time < remind_time + timedelta(minutes=1):
                            try:
                                # Lấy chat_id từ mapping (có thể là private chat hoặc group)
                                chat_id = user_chat_mapping.get(user_id)
                                if not chat_id:
                                    print(f"No chat_id mapping for user_id {user_id}")
                                    continue
                                
                                print(f"Sending reminder to user_id {user_id} (chat_id {chat_id}): {task['content']}")
                                reminder_text = f"⏰ NHẮC NHỞ!\n\n📌 {task['content']}"
                                if task.get('done'):
                                    reminder_text += "\n\n✅ (Đã hoàn thành)"
                                bot.send_message(chat_id, reminder_text)
                                task['reminded'] = True
                                print(f"Reminder sent successfully to user_id {user_id}")
                            except Exception as e:
                                print(f"Error sending reminder: {e}")
            time.sleep(30)  # Kiểm tra mỗi 30 giây
        except Exception as e:
            print(f"Error in reminder_checker: {e}")
            time.sleep(30)

# Khởi động background thread
reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
reminder_thread.start()

def show_main_menu(user_id, message_text="👋 Xin chào! Tôi là trợ lý đa chức năng của bạn."):
    """Hiển thị menu chính với các category"""
    tz = get_user_timezone(user_id)
    task_count = len(user_tasks.get(user_id, []))
    
    text = f"{message_text}\n\n"
    text += f"📊 **Thống kê:**\n"
    text += f"   • 📋 Tasks: {task_count}\n"
    text += f"   • 🌍 Múi giờ: GMT+{tz}\n\n"
    text += f"🎯 **Chọn chức năng:**"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Row 1: Task Management & Voice Tools
    btn_tasks = types.InlineKeyboardButton("📋 Quản Lý Task", callback_data="category_tasks")
    btn_voice = types.InlineKeyboardButton("🎤 Công Cụ Voice", callback_data="category_voice")
    markup.add(btn_tasks, btn_voice)
    
    # Row 2: AI Assistant & Quick Actions
    btn_ai = types.InlineKeyboardButton("🤖 Trợ Lý AI", callback_data="category_ai")
    btn_quick = types.InlineKeyboardButton("⚡ Thêm Nhanh", callback_data="menu_add")
    markup.add(btn_ai, btn_quick)
    
    # Row 3: Settings & Help
    btn_settings = types.InlineKeyboardButton("⚙️ Cài Đặt", callback_data="category_settings")
    btn_help = types.InlineKeyboardButton("❓ Trợ Giúp", callback_data="menu_help")
    markup.add(btn_settings, btn_help)
    
    return text, markup

def show_tasks_menu(user_id):
    """Hiển thị menu Task Management"""
    task_count = len(user_tasks.get(user_id, []))
    pending = sum(1 for t in user_tasks.get(user_id, []) if not t.get('done', False))
    completed = task_count - pending
    
    text = f"📋 **QUẢN LÝ CÔNG VIỆC**\n\n"
    text += f"📊 Thống kê:\n"
    text += f"   • Tổng: {task_count} tasks\n"
    text += f"   • Đang làm: {pending} tasks\n"
    text += f"   • Hoàn thành: {completed} tasks\n\n"
    text += f"🎯 Chọn thao tác:"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_add = types.InlineKeyboardButton("➕ Thêm task", callback_data="menu_add")
    btn_list = types.InlineKeyboardButton("📋 Xem tất cả", callback_data="menu_list")
    markup.add(btn_add, btn_list)
    
    if task_count > 0:
        btn_pending = types.InlineKeyboardButton("⏳ Tasks đang làm", callback_data="tasks_pending")
        btn_completed = types.InlineKeyboardButton("✅ Tasks hoàn thành", callback_data="tasks_completed")
        markup.add(btn_pending, btn_completed)
    
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_back)
    
    return text, markup

def show_voice_menu(user_id):
    """Hiển thị menu Voice Tools"""
    text = (
        "🎤 **CÔNG CỤ VOICE**\n\n"
        "✨ Chức năng:\n"
        "   • Chuyển giọng nói thành văn bản\n"
        "   • Hỗ trợ tiếng Việt & English\n"
        "   • Xuất file .txt\n"
        "   • Powered by OpenAI Whisper\n\n"
        "📱 Cách sử dụng:\n"
        "   1. Ghi âm voice message\n"
        "   2. Gửi cho bot\n"
        "   3. Nhận file .txt\n\n"
        "💰 Chi phí: ~150 VND/phút\n\n"
        "🎯 Thao tác:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_guide = types.InlineKeyboardButton("📖 Hướng dẫn chi tiết", callback_data="voice_guide")
    btn_demo = types.InlineKeyboardButton("🎬 Xem demo", callback_data="voice_demo")
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_guide, btn_demo, btn_back)
    
    return text, markup

def show_ai_menu(user_id):
    """Hiển thị menu AI Assistant"""
    has_github_token = bool(GITHUB_TOKEN)
    has_openai_key = bool(OPENAI_API_KEY)
    
    text = (
        "🤖 **TRỢ LÝ AI**\n\n"
        "✨ Tính năng AI:\n"
        "   • 💬 Tạo Task Từ Ngôn Ngữ Tự Nhiên\n"
        "   • 🎤 Chuyển Đổi Giọng Nói Thành Văn Bản\n"
        "   • 📊 Phân Tích Task Thông Minh (Sắp có)\n"
        "   • 🔮 Gợi Ý Từ AI (Sắp có)\n\n"
        "🔑 Trạng thái API:\n"
        f"   • GitHub AI: {'✅ Hoạt động' if has_github_token else '❌ Chưa cấu hình'}\n"
        f"   • OpenAI: {'✅ Hoạt động' if has_openai_key else '❌ Chưa cấu hình'}\n\n"
        "🎯 Thao tác:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    if has_github_token:
        btn_nl = types.InlineKeyboardButton("💬 Tạo task bằng ngôn ngữ tự nhiên", callback_data="ai_natural_language")
    else:
        btn_nl = types.InlineKeyboardButton("🔒 Setup GitHub AI", callback_data="ai_setup_github")
    markup.add(btn_nl)
    
    btn_features = types.InlineKeyboardButton("🚀 Tính năng sắp có", callback_data="ai_upcoming")
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_features, btn_back)
    
    return text, markup

def show_settings_menu(user_id):
    """Hiển thị menu Settings"""
    tz = get_user_timezone(user_id)
    
    text = (
        "⚙️ **CÀI ĐẶT**\n\n"
        f"🌍 **Múi giờ hiện tại:** GMT+{tz}\n"
        f"📋 **Tổng tasks:** {len(user_tasks.get(user_id, []))}\n\n"
        "🎯 Cấu hình:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_tz = types.InlineKeyboardButton("🌍 Đổi múi giờ", callback_data="menu_timezone")
    btn_clear = types.InlineKeyboardButton("🗑️ Xóa dữ liệu", callback_data="settings_clear_confirm")
    markup.add(btn_tz, btn_clear)
    
    btn_about = types.InlineKeyboardButton("ℹ️ Về bot", callback_data="settings_about")
    btn_stats = types.InlineKeyboardButton("📊 Thống kê", callback_data="settings_stats")
    markup.add(btn_about, btn_stats)
    
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_back)
    
    return text, markup

# Lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
    print(f"Received /start from chat_id: {bot_message.chat.id}, user_id: {bot_message.from_user.id}")
    user_id = get_user_id(bot_message)
    chat_id = bot_message.chat.id
    update_user_chat_mapping(bot_message)
    
    text, markup = show_main_menu(user_id)
    bot.send_message(chat_id, text, reply_markup=markup)

# Lệnh /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📚 **HƯỚNG DẪN SỬ DỤNG BOT**\n\n"
        "🎯 **MENU CHÍNH:**\n"
        "Bot được chia thành 6 danh mục:\n\n"
        "📋 **Quản Lý Task** - Quản lý công việc\n"
        "   • Thêm/Xem/Sửa/Xóa tasks\n"
        "   • Đặt nhắc nhở với lịch\n"
        "   • Lọc theo trạng thái\n\n"
        "🎤 **Công Cụ Voice** - Chuyển giọng nói thành văn bản\n"
        "   • Gửi voice → Nhận file .txt\n"
        "   • Hỗ trợ tiếng Việt & English\n"
        "   • Sử dụng OpenAI Whisper\n\n"
        "🤖 **Trợ Lý AI** - Trợ lý thông minh\n"
        "   • Tạo task từ ngôn ngữ tự nhiên\n"
        "   • AI phân tích và tạo nhắc nhở\n"
        "   • Gợi ý thông minh (sắp có)\n\n"
        "⚡ **Thêm Nhanh** - Thêm task nhanh\n"
        "   • Thêm task trực tiếp từ menu chính\n"
        "   • Không cần vào menu phụ\n\n"
        "⚙️ **Cài Đặt** - Cấu hình\n"
        "   • Đổi múi giờ\n"
        "   • Xóa dữ liệu\n"
        "   • Xem thống kê\n\n"
        "❓ **Trợ Giúp** - Hướng dẫn và hỗ trợ\n\n"
        "💡 **MẸO:**\n"
        "• Dùng nút menu để thao tác nhanh\n"
        "• Voice: Ghi âm cuộc họp → File văn bản\n"
        "• AI: Nói tự nhiên → Task + Nhắc nhở\n"
        "• Gửi /start để quay về menu chính"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
    markup.add(btn_menu)
    
    bot.send_message(message.chat.id, help_text, reply_markup=markup, parse_mode='Markdown')

# Lệnh /timezone để đặt múi giờ
@bot.message_handler(commands=['timezone'])
def set_timezone(message):
    print(f"Received /timezone from chat_id: {message.chat.id}, user_id: {message.from_user.id}")
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            # Hiển thị timezone hiện tại và hướng dẫn
            current_tz = get_user_timezone(user_id)
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
            user_timezones[user_id] = TIMEZONES[tz_input]
            bot.reply_to(message, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_input]} ({tz_input})")
            return
        
        # Kiểm tra định dạng GMT+X hoặc +X
        if tz_input.startswith('GMT'):
            tz_input = tz_input[3:]
        
        if tz_input.startswith('+') or tz_input.startswith('-'):
            offset = int(tz_input)
            if -12 <= offset <= 14:
                user_timezones[user_id] = offset
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
    print(f"Received /add from chat_id: {message.chat.id}, user_id: {message.from_user.id}")
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    # Lấy nội dung sau lệnh /add
    task_content = message.text[len('/add '):].strip()
    
    if not task_content:
        # Chuyển sang chế độ hỏi nội dung
        user_states[user_id] = "waiting_task_content"
        bot.reply_to(message, 
            "✍️ Nhập nội dung công việc:\n\n"
            "(Ví dụ: Họp team lúc 9h sáng)")
        return

    if user_id not in user_tasks:
        user_tasks[user_id] = []
    
    user_tasks[user_id].append({
        'content': task_content, 
        'done': False,
        'remind_time': None,
        'reminded': False
    })
    
    # Hiển thị với menu buttons
    markup = types.InlineKeyboardMarkup()
    btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{len(user_tasks[user_id])-1}")
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
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    show_task_list(user_id, chat_id)

# Lệnh /done để đánh dấu hoàn thành
@bot.message_handler(commands=['done'])
def mark_done(message):
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        task_number = int(message.text.split()[1])
        if 1 <= task_number <= len(user_tasks[user_id]):
            user_tasks[user_id][task_number - 1]['done'] = True
            bot.reply_to(message, f"✅ Đã đánh dấu hoàn thành: '{user_tasks[user_id][task_number - 1]['content']}'")
        else:
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[user_id])}")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Vui lòng nhập số thứ tự công việc.\n\nVí dụ: /done 1")

# Lệnh /remind để đặt nhắc nhở
@bot.message_handler(commands=['remind'])
def set_reminder(message):
    print(f"Received /remind from chat_id: {message.chat.id}, user_id: {message.from_user.id}")
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
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
        
        if task_number < 1 or task_number > len(user_tasks[user_id]):
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[user_id])}")
            return
        
        # Parse thời gian (với timezone của user)
        remind_time = parse_time(time_str, user_id)
        
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
        user_tasks[user_id][task_number - 1]['remind_time'] = remind_time
        user_tasks[user_id][task_number - 1]['reminded'] = False
        
        task_content = user_tasks[user_id][task_number - 1]['content']
        # Hiển thị theo giờ local của user
        user_time = get_user_time(user_id, remind_time)
        remind_str = user_time.strftime("%d/%m/%Y %H:%M")
        
        bot.reply_to(message, 
            f"⏰ Đã đặt nhắc nhở!\n\n"
            f"📌 Công việc: {task_content}\n"
            f"🕐 Thời gian: {remind_str} (GMT+{get_user_timezone(user_id)})")
        
    except (IndexError, ValueError) as e:
        bot.reply_to(message, 
            "⚠️ Lỗi định dạng!\n\n"
            "Sử dụng: /remind [số] [thời gian]\n"
            "Ví dụ: /remind 1 14:30")

def parse_time(time_str, user_id=None):
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
                user_now = get_user_time(user_id) if user_id else datetime.utcnow()
                remind_time = user_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Nếu thời gian đã qua trong ngày hôm nay, chuyển sang ngày mai
                if remind_time <= user_now:
                    remind_time += timedelta(days=1)
                
                # Chuyển sang UTC
                return to_utc_time(user_id, remind_time) if user_id else remind_time
        
        # Định dạng: YYYY-MM-DD HH:MM (theo giờ local của user)
        if len(time_str.split()) == 2:
            local_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            return to_utc_time(user_id, local_time) if user_id else local_time
        
        # Định dạng: DD/MM/YYYY HH:MM (theo giờ local của user)
        if '/' in time_str:
            local_time = datetime.strptime(time_str, "%d/%m/%Y %H:%M")
            return to_utc_time(user_id, local_time) if user_id else local_time
        
        return None
    except:
        return None

# ============= AI FEATURES với GitHub Models =============

def call_github_ai(user_message, system_prompt="You are a helpful assistant."):
    """Gọi GitHub Models AI API"""
    if not GITHUB_TOKEN:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"GitHub AI API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error calling GitHub AI: {e}")
        return None

def parse_natural_language_task(user_text, user_id):
    """Sử dụng AI để parse task và thời gian từ ngôn ngữ tự nhiên"""
    user_now = get_user_time(user_id)
    current_time_str = user_now.strftime("%Y-%m-%d %H:%M")
    
    system_prompt = f"""Bạn là trợ lý thông minh phân tích công việc và thời gian.
Thời gian hiện tại: {current_time_str}
Múi giờ: GMT+{get_user_timezone(user_id)}

Nhiệm vụ: Phân tích câu của user và trả về JSON với format:
{{
  "task": "nội dung công việc",
  "time": "thời gian nhắc nhở",
  "has_reminder": true/false
}}

Quy tắc phân tích thời gian:
- "sáng mai", "mai sáng" → ngày mai 9:00
- "chiều mai", "mai chiều" → ngày mai 14:00
- "tối nay", "tối" → hôm nay 20:00
- "9h sáng", "9h" → 09:00 gần nhất (hôm nay hoặc mai)
- "2h chiều", "14h" → 14:00 gần nhất
- Nếu không có thời gian cụ thể: has_reminder = false

Chỉ trả về JSON, không thêm text khác."""
    
    ai_response = call_github_ai(user_text, system_prompt)
    
    if not ai_response:
        return None
    
    try:
        # Parse JSON từ AI response
        result = json.loads(ai_response)
        return result
    except:
        # Nếu AI không trả về JSON chuẩn, fallback
        return None

# Lệnh /delete để xóa một task
@bot.message_handler(commands=['delete'])
def delete_task(message):
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        task_number = int(message.text.split()[1])
        if 1 <= task_number <= len(user_tasks[user_id]):
            deleted_task = user_tasks[user_id].pop(task_number - 1)
            bot.reply_to(message, f"🗑️ Đã xóa công việc: '{deleted_task['content']}'")
        else:
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[user_id])}")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Vui lòng nhập số thứ tự công việc.\n\nVí dụ: /delete 1")

# Lệnh /clear để xóa danh sách
@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đã trống!")
        return
        
    # Tạo inline keyboard để xác nhận
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Có", callback_data="clear_yes"),
        types.InlineKeyboardButton("❌ Không", callback_data="clear_no")
    )
    bot.reply_to(message, "⚠️ Bạn có chắc chắn muốn xóa toàn bộ danh sách công việc?", reply_markup=markup)

# Lệnh /cancel để hủy thao tác đang làm
@bot.message_handler(commands=['cancel'])
def cancel_action(message):
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    if user_id in user_states and user_states[user_id]:
        old_state = user_states[user_id]
        user_states[user_id] = None
        
        # Hiển thị menu hoặc task list tùy theo state
        if old_state.startswith("selecting_remind_") or old_state.startswith("manual_"):
            text, markup = show_main_menu(user_id, "❌ Đã hủy đặt nhắc nhở")
            bot.send_message(chat_id, text, reply_markup=markup)
        else:
            text, markup = show_main_menu(user_id, "❌ Đã hủy thao tác")
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.reply_to(message, "Không có thao tác nào đang thực hiện.")

# Xử lý callback từ inline keyboard
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    print(f"Received callback: {call.data} from chat_id: {chat_id}, user_id: {user_id}")
    
    # Cập nhật mapping
    user_chat_mapping[user_id] = chat_id
    
    # Menu chính
    if call.data == "menu_main":
        text, markup = show_main_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    # Thêm công việc
    elif call.data == "menu_add":
        user_states[user_id] = "waiting_task_content"
        bot.edit_message_text(
            "✍️ Nhập nội dung công việc:\n\n"
            "(Ví dụ: Họp team lúc 9h sáng)",
            chat_id=chat_id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    # Xem danh sách
    elif call.data == "menu_list":
        if user_id not in user_tasks or not user_tasks[user_id]:
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
            show_task_list(user_id, chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    # Đặt múi giờ
    elif call.data == "menu_timezone":
        current_tz = get_user_timezone(user_id)
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
            user_timezones[user_id] = TIMEZONES[tz_code]
            bot.answer_callback_query(call.id, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_code]}")
            text, markup = show_main_menu(user_id, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_code]}")
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
    
    # Hướng dẫn
    elif call.data == "menu_help":
        help_text = (
            "📚 **HƯỚNG DẪN SỬ DỤNG BOT**\n\n"
            "🎯 **SỬ DỤNG MENU:**\n"
            "• Nhấn các nút trên menu để thao tác nhanh\n"
            "• Không cần gõ lệnh phức tạp\n"
            "• Menu được chia thành các danh mục dễ tìm\n\n"
            "📋 **QUẢN LÝ TASK:**\n"
            "• Thêm, xem, sửa, xóa tasks\n"
            "• Đặt nhắc nhở cho từng task\n"
            "• Chọn ngày giờ bằng lịch\n\n"
            "🎤 **CÔNG CỤ VOICE:**\n"
            "• Gửi voice message → Nhận file .txt\n"
            "• Hỗ trợ tiếng Việt & English\n"
            "• Sử dụng OpenAI Whisper\n\n"
            "🤖 **TRỢ LÝ AI:**\n"
            "• Tạo task bằng ngôn ngữ tự nhiên\n"
            "• AI phân tích và tạo nhắc nhở tự động\n"
            "• Cần GitHub Token (miễn phí)\n\n"
            "⏰ **ĐỊNH DẠNG THỜI GIAN:**\n"
            "• 14:30 - Hôm nay lúc 14:30\n"
            "• 2m, 30m, 2h - Sau 2 phút, 30 phút, 2 giờ\n"
            "• Hoặc dùng lịch chọn ngày giờ\n\n"
            "🌍 **MÚI GIỜ:**\n"
            "• Vào Cài Đặt → Đổi múi giờ\n"
            "• Thời gian hiển thị theo múi giờ của bạn\n\n"
            "💡 **MẸO:**\n"
            "• Thêm Nhanh: Thêm task nhanh từ menu chính\n"
            "• Voice: Ghi âm cuộc họp → Chuyển thành văn bản\n"
            "• AI: Nói tự nhiên, AI tạo task cho bạn"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.add(btn_back)
        bot.edit_message_text(help_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== CATEGORY MENUS =====
    
    # Task Management Category
    elif call.data == "category_tasks":
        text, markup = show_tasks_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Voice Tools Category
    elif call.data == "category_voice":
        text, markup = show_voice_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # AI Assistant Category
    elif call.data == "category_ai":
        text, markup = show_ai_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Settings Category
    elif call.data == "category_settings":
        text, markup = show_settings_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== TASKS SUBMENU =====
    
    elif call.data == "tasks_pending":
        pending_tasks = [t for t in user_tasks.get(user_id, []) if not t.get('done', False)]
        if not pending_tasks:
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(
                "✅ Không có task nào đang làm!\n\nTất cả đã hoàn thành!",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            text = f"⏳ **TASKS ĐANG LÀM** ({len(pending_tasks)})\n\n"
            for i, task in enumerate(pending_tasks, 1):
                text += f"{i}. {task['content']}\n"
                if task.get('remind_time'):
                    remind_local = get_user_time(user_id, task['remind_time'])
                    text += f"   🕐 {remind_local.strftime('%d/%m %H:%M')}\n"
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "tasks_completed":
        completed_tasks = [t for t in user_tasks.get(user_id, []) if t.get('done', False)]
        if not completed_tasks:
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(
                "📭 Chưa có task nào hoàn thành!",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            text = f"✅ **TASKS ĐÃ HOÀN THÀNH** ({len(completed_tasks)})\n\n"
            for i, task in enumerate(completed_tasks, 1):
                text += f"{i}. ~~{task['content']}~~\n"
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== VOICE SUBMENU =====
    
    elif call.data == "voice_guide":
        guide_text = (
            "📖 **HƯỚNG DẪN CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN**\n\n"
            "🎯 **Cách sử dụng:**\n"
            "1. Nhấn giữ icon micro 🎤 trong Telegram\n"
            "2. Nói nội dung (tiếng Việt hoặc English)\n"
            "3. Thả tay để gửi\n"
            "4. Đợi 2-8 giây\n"
            "5. Nhận file .txt với nội dung đã chuyển đổi\n\n"
            "⚙️ **Cài đặt (lần đầu):**\n"
            "• Cần OpenAI API key\n"
            "• Xem: VOICE_QUICK_SETUP.md\n"
            "• Chi phí: ~150 VND/phút\n\n"
            "🔒 **Riêng tư:**\n"
            "• File txt luôn gửi về chat riêng\n"
            "• Thành viên khác không thấy nội dung\n"
            "• Mỗi user có dữ liệu riêng biệt\n\n"
            "💡 **Mẹo:**\n"
            "• Nói rõ ràng, không quá nhanh\n"
            "• Môi trường yên tĩnh → Độ chính xác cao\n"
            "• Hỗ trợ voice dài (cả phút)"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Công Cụ Voice", callback_data="category_voice")
        markup.add(btn_back)
        bot.edit_message_text(guide_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "voice_demo":
        demo_text = (
            "🎬 **DEMO: CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN**\n\n"
            "📝 **Ví dụ 1: Ghi chú cuộc họp**\n"
            "Voice: \"Cuộc họp ngày mai lúc 9 giờ sáng, thảo luận về dự án X\"\n"
            "→ File txt: Nội dung đầy đủ được chuyển đổi\n\n"
            "📝 **Ví dụ 2: Danh sách việc cần làm**\n"
            "Voice: \"Nhớ mua sữa, trứng, bánh mì khi về nhà\"\n"
            "→ File txt: Danh sách mua sắm\n\n"
            "📝 **Ví dụ 3: Phỏng vấn**\n"
            "Voice: [5 phút phỏng vấn]\n"
            "→ File txt: Bản ghi hoàn chỉnh\n\n"
            "🎯 **Thử ngay:**\n"
            "Gửi voice message cho bot để test!"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Công Cụ Voice", callback_data="category_voice")
        markup.add(btn_back)
        bot.edit_message_text(demo_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== AI SUBMENU =====
    
    elif call.data == "ai_natural_language":
        if not GITHUB_TOKEN:
            bot.answer_callback_query(call.id, "❌ Chưa cấu hình GitHub Token!", show_alert=True)
            return
        
        bot.edit_message_text(
            "💬 **TẠO TASK BẰNG NGÔN NGỮ TỰ NHIÊN**\n\n"
            "Nhập nội dung task theo cách tự nhiên, AI sẽ phân tích và tạo task + nhắc nhở cho bạn.\n\n"
            "📝 Ví dụ:\n"
            "• \"Họp team lúc 2 giờ chiều mai\"\n"
            "• \"Nhắc tôi mua sữa sau 30 phút\"\n"
            "• \"Deadline dự án X ngày 30/7\"\n\n"
            "✍️ Nhập nội dung:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        user_states[user_id] = "waiting_task_content"
        bot.answer_callback_query(call.id)
    
    elif call.data == "ai_setup_github":
        setup_text = (
            "🔑 **CÀI ĐẶT GITHUB AI**\n\n"
            "GitHub Models API hoàn toàn **MIỄN PHÍ** và rất mạnh!\n\n"
            "📝 **Cách cài đặt:**\n"
            "1. Truy cập: github.com/settings/tokens\n"
            "2. Tạo token mới (classic)\n"
            "3. Chọn scopes: repo, read:user\n"
            "4. Copy token\n"
            "5. Thêm vào .env: GITHUB_TOKEN=your_token\n"
            "6. Khởi động lại bot\n\n"
            "📖 **Xem hướng dẫn chi tiết:**\n"
            "→ AI_SETUP.md trong repository\n\n"
            "✨ **Tính năng khi có GitHub AI:**\n"
            "• Tạo task từ ngôn ngữ tự nhiên\n"
            "• Tự động phân tích thời gian\n"
            "• Gợi ý thông minh"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Trợ Lý AI", callback_data="category_ai")
        markup.add(btn_back)
        bot.edit_message_text(setup_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "ai_upcoming":
        upcoming_text = (
            "🚀 **TÍNH NĂNG SẮP CÓ**\n\n"
            "📊 **Phân Tích Task Thông Minh:**\n"
            "• AI phân tích mô hình năng suất\n"
            "• Gợi ý thời gian làm việc tốt nhất\n"
            "• Ước lượng thời gian hoàn thành\n\n"
            "🔮 **Gợi Ý Từ AI:**\n"
            "• Gợi ý task dựa trên lịch sử\n"
            "• Tự động phân loại tasks\n"
            "• Đề xuất độ ưu tiên\n\n"
            "🎯 **Nhắc Nhở Thông Minh:**\n"
            "• Thông báo theo ngữ cảnh\n"
            "• Tự điều chỉnh thời gian nhắc\n"
            "• Nhắc nhở theo vị trí\n\n"
            "🤝 **Cộng Tác Nhóm:**\n"
            "• Chia sẻ tasks trong nhóm\n"
            "• Phân công công việc\n"
            "• Theo dõi tiến độ\n\n"
            "⏰ **Ra mắt:** Q4 2026\n"
            "💡 **Đề xuất tính năng?** Liên hệ admin!"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Trợ Lý AI", callback_data="category_ai")
        markup.add(btn_back)
        bot.edit_message_text(upcoming_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== SETTINGS SUBMENU =====
    
    elif call.data == "settings_clear_confirm":
        text = (
            "⚠️ **XÁC NHẬN XÓA DỮ LIỆU**\n\n"
            f"Bạn có {len(user_tasks.get(user_id, []))} tasks.\n\n"
            "Xóa sẽ mất:\n"
            "• Tất cả tasks\n"
            "• Tất cả reminders\n"
            "• Cài đặt múi giờ (về mặc định)\n\n"
            "⚠️ **Không thể khôi phục!**\n\n"
            "Bạn chắc chắn?"
        )
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("🗑️ Có, xóa hết", callback_data="settings_clear_yes")
        btn_no = types.InlineKeyboardButton("❌ Không, giữ lại", callback_data="category_settings")
        markup.add(btn_yes, btn_no)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "settings_clear_yes":
        # Xóa tất cả dữ liệu của user
        user_tasks[user_id] = []
        user_timezones[user_id] = 7  # Reset về GMT+7
        user_states[user_id] = None
        
        text, markup = show_main_menu(user_id, "🗑️ Đã xóa toàn bộ dữ liệu!")
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id, "✅ Đã xóa toàn bộ dữ liệu!")
    
    elif call.data == "settings_about":
        about_text = (
            "ℹ️ **VỀ BOT**\n\n"
            "🤖 **Tên:** PHT Task Bot\n"
            "📦 **Phiên bản:** 2.0.0 (Đa Chức Năng)\n"
            "👨‍💻 **Phát triển bởi:** PHT Team\n"
            "📅 **Cập nhật:** 25/07/2026\n\n"
            "✨ **Tính năng chính:**\n"
            "• Quản lý công việc với nhắc nhở thông minh\n"
            "• Chuyển đổi giọng nói thành văn bản\n"
            "• Tạo task bằng AI\n"
            "• Hỗ trợ đa múi giờ\n"
            "• Thiết kế ưu tiên riêng tư\n\n"
            "🔗 **Liên kết:**\n"
            "• GitHub: github.com/rambo247/task_bot\n"
            "• Tài liệu: Repository README.md\n\n"
            "💡 **Công nghệ:**\n"
            "• Python 3.6+\n"
            "• pyTelegramBotAPI\n"
            "• OpenAI Whisper API\n"
            "• GitHub Models API"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Cài Đặt", callback_data="category_settings")
        markup.add(btn_back)
        bot.edit_message_text(about_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "settings_stats":
        total_tasks = len(user_tasks.get(user_id, []))
        pending = sum(1 for t in user_tasks.get(user_id, []) if not t.get('done', False))
        completed = total_tasks - pending
        with_reminder = sum(1 for t in user_tasks.get(user_id, []) if t.get('remind_time'))
        
        stats_text = (
            f"📊 **THỐNG KÊ CỦA BẠN**\n\n"
            f"📋 **Tasks:**\n"
            f"   • Tổng: {total_tasks}\n"
            f"   • Đang làm: {pending}\n"
            f"   • Hoàn thành: {completed}\n"
            f"   • Có reminder: {with_reminder}\n\n"
            f"⚙️ **Cài đặt:**\n"
            f"   • Múi giờ: GMT+{get_user_timezone(user_id)}\n"
            f"   • GitHub AI: {'✅ Bật' if GITHUB_TOKEN else '❌ Tắt'}\n"
            f"   • OpenAI: {'✅ Bật' if OPENAI_API_KEY else '❌ Tắt'}\n\n"
            f"💪 **Tỷ Lệ Hoàn Thành:**\n"
            f"   {f'{completed}/{total_tasks} ({int(completed/total_tasks*100)}%)' if total_tasks > 0 else 'Chưa có dữ liệu'}"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Cài Đặt", callback_data="category_settings")
        markup.add(btn_back)
        bot.edit_message_text(stats_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Xử lý action cho từng task
    elif call.data.startswith("task_"):
        parts = call.data.split("_")
        action = parts[1]
        task_idx = int(parts[2])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")
            return
        
        if action == "done":
            user_tasks[user_id][task_idx]['done'] = True
            bot.answer_callback_query(call.id, "✅ Đã hoàn thành!")
            show_task_list(user_id, chat_id, call.message.message_id)
        
        elif action == "remind":
            user_states[user_id] = f"selecting_remind_date_{task_idx}"
            task_content = user_tasks[user_id][task_idx]['content']
            
            # Hiển thị calendar picker
            calendar_markup = create_calendar(user_id)
            bot.edit_message_text(
                f"📅 Chọn ngày nhắc nhở cho:\n'{task_content}'",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=calendar_markup
            )
            bot.answer_callback_query(call.id)
        
        elif action == "delete":
            deleted_task = user_tasks[user_id].pop(task_idx)
            bot.answer_callback_query(call.id, f"🗑️ Đã xóa: {deleted_task['content']}")
            if user_tasks[user_id]:
                show_task_list(user_id, chat_id, call.message.message_id)
            else:
                text, markup = show_main_menu(user_id, "✅ Đã xóa task cuối cùng!")
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        
        elif action == "back":
            show_task_list(user_id, chat_id, call.message.message_id)
            bot.answer_callback_query(call.id)
    
    # Calendar picker handlers
    elif call.data.startswith("calendar_"):
        parts = call.data.split("_")
        action = parts[1]
        
        if action == "ignore":
            bot.answer_callback_query(call.id)
        
        elif action == "prev":
            year, month = int(parts[2]), int(parts[3])
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            calendar_markup = create_calendar(user_id, year, month)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=calendar_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "next":
            year, month = int(parts[2]), int(parts[3])
            month += 1
            if month > 12:
                month = 1
                year += 1
            calendar_markup = create_calendar(user_id, year, month)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=calendar_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "today":
            user_now = get_user_time(user_id)
            # Chuyển sang chọn giờ cho hôm nay
            time_markup = create_time_picker(user_id, user_now)
            
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_date_"):
                task_idx = int(state.split("_")[-1])
                task_content = user_tasks[user_id][task_idx]['content']
                bot.edit_message_text(
                    f"🕐 Chọn giờ cho hôm nay:\n'{task_content}'",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=time_markup
                )
                user_states[user_id] = f"selecting_remind_time_{task_idx}_{user_now.strftime('%Y_%m_%d')}"
            bot.answer_callback_query(call.id)
        
        elif action == "day":
            year, month, day = int(parts[2]), int(parts[3]), int(parts[4])
            selected_date = datetime(year, month, day)
            
            # Chuyển sang chọn giờ
            time_markup = create_time_picker(user_id, selected_date)
            
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_date_"):
                task_idx = int(state.split("_")[-1])
                task_content = user_tasks[user_id][task_idx]['content']
                bot.edit_message_text(
                    f"🕐 Chọn giờ - {selected_date.strftime('%d/%m/%Y')}:\n'{task_content}'",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=time_markup
                )
                user_states[user_id] = f"selecting_remind_time_{task_idx}_{selected_date.strftime('%Y_%m_%d')}"
            bot.answer_callback_query(call.id)
        
        elif action == "cancel":
            show_task_list(user_id, chat_id, call.message.message_id)
            user_states[user_id] = None
            bot.answer_callback_query(call.id)
    
    # Time picker handlers
    elif call.data.startswith("time_"):
        parts = call.data.split("_")
        action = parts[1]
        
        if action == "ignore":
            bot.answer_callback_query(call.id)
        
        elif action == "hour":
            hour = int(parts[2])
            date_str = parts[3]
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Hiển thị minute picker
            time_markup = create_time_picker(user_id, selected_date, hour)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=time_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "minute":
            hour = int(parts[2])
            minute = int(parts[3])
            date_str = parts[4]
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Tạo datetime với giờ local
            remind_local = selected_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            remind_utc = to_utc_time(user_id, remind_local)
            
            # Lưu reminder
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_time_"):
                task_idx = int(state.split("_")[3])
                
                user_tasks[user_id][task_idx]['remind_time'] = remind_utc
                user_tasks[user_id][task_idx]['reminded'] = False
                
                task_content = user_tasks[user_id][task_idx]['content']
                remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
                
                markup = types.InlineKeyboardMarkup()
                btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
                btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
                markup.add(btn_list, btn_menu)
                
                bot.edit_message_text(
                    f"⏰ Đã đặt nhắc nhở!\n\n"
                    f"📌 {task_content}\n"
                    f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                user_states[user_id] = None
                bot.answer_callback_query(call.id, "✅ Đã đặt nhắc nhở!")
        
        elif action == "quick":
            # Quick time selection (5m, 15m, 30m, 1h, 2h, 3h)
            duration = parts[2]
            
            if duration.endswith('m'):
                minutes = int(duration[:-1])
                remind_utc = datetime.utcnow() + timedelta(minutes=minutes)
            elif duration.endswith('h'):
                hours = int(duration[:-1])
                remind_utc = datetime.utcnow() + timedelta(hours=hours)
            else:
                bot.answer_callback_query(call.id, "❌ Lỗi!")
                return
            
            # Lưu reminder
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_"):
                # Extract task_idx from state
                if state.startswith("selecting_remind_date_"):
                    task_idx = int(state.split("_")[-1])
                elif state.startswith("selecting_remind_time_"):
                    task_idx = int(state.split("_")[3])
                else:
                    bot.answer_callback_query(call.id, "❌ Lỗi!")
                    return
                
                user_tasks[user_id][task_idx]['remind_time'] = remind_utc
                user_tasks[user_id][task_idx]['reminded'] = False
                
                task_content = user_tasks[user_id][task_idx]['content']
                remind_local = get_user_time(user_id, remind_utc)
                remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
                
                markup = types.InlineKeyboardMarkup()
                btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
                btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
                markup.add(btn_list, btn_menu)
                
                bot.edit_message_text(
                    f"⏰ Đã đặt nhắc nhở!\n\n"
                    f"📌 {task_content}\n"
                    f"🕐 {remind_str} (sau {duration})",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                user_states[user_id] = None
                bot.answer_callback_query(call.id, f"✅ Nhắc sau {duration}!")
        
        elif action == "manual":
            # Nhập thời gian thủ công
            sub_action = parts[2]
            
            if sub_action == "full":
                # Nhập giờ đầy đủ HH:MM
                # date_str có thể có dấu _ (VD: 2026_07_25) nên phải join từ parts[3] trở đi
                date_str = "_".join(parts[3:])
                
                state = user_states.get(user_id, "")
                if state.startswith("selecting_remind_"):
                    # Extract task_idx from state
                    if state.startswith("selecting_remind_date_"):
                        task_idx = int(state.split("_")[-1])
                    elif state.startswith("selecting_remind_time_"):
                        task_idx = int(state.split("_")[3])
                    else:
                        bot.answer_callback_query(call.id, "❌ Lỗi!")
                        return
                    
                    # Đổi state để đợi input
                    user_states[user_id] = f"manual_time_input_{task_idx}_{date_str}"
                    
                    task_content = user_tasks[user_id][task_idx]['content']
                    bot.edit_message_text(
                        f"✍️ Nhập giờ cho:\n'{task_content}'\n\n"
                        f"Định dạng: HH:MM (ví dụ: 14:27, 9:05)\n"
                        f"Hoặc gửi /cancel để hủy",
                        chat_id=chat_id,
                        message_id=call.message.message_id
                    )
                    bot.answer_callback_query(call.id)
            
            elif sub_action == "minute":
                # Nhập chỉ phút
                hour = int(parts[3])
                # date_str có thể có dấu _ (VD: 2026_07_25) nên phải join từ parts[4] trở đi
                date_str = "_".join(parts[4:])
                
                state = user_states.get(user_id, "")
                if state.startswith("selecting_remind_time_"):
                    task_idx = int(state.split("_")[3])
                    
                    # Đổi state để đợi input phút
                    user_states[user_id] = f"manual_minute_input_{task_idx}_{hour}_{date_str}"
                    
                    task_content = user_tasks[user_id][task_idx]['content']
                    bot.edit_message_text(
                        f"✍️ Nhập phút cho {hour}:??\n'{task_content}'\n\n"
                        f"Nhập số phút (0-59), ví dụ: 27, 8, 42\n"
                        f"Hoặc gửi /cancel để hủy",
                        chat_id=chat_id,
                        message_id=call.message.message_id
                    )
                    bot.answer_callback_query(call.id)
        
        elif action == "back":
            # date_str có thể có dấu _ (VD: 2026_07_25) nên phải join từ parts[2] trở đi
            date_str = "_".join(parts[2:])
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Quay lại chọn giờ
            time_markup = create_time_picker(user_id, selected_date)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=time_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "cancel":
            show_task_list(user_id, chat_id, call.message.message_id)
            user_states[user_id] = None
            bot.answer_callback_query(call.id)
    
    # Xóa tất cả
    elif call.data == "clear_yes":
        user_tasks[user_id] = []
        text, markup = show_main_menu(user_id, "🧹 Đã xóa toàn bộ danh sách công việc!")
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "clear_no":
        show_task_list(user_id, chat_id, call.message.message_id)
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

def show_task_list(user_id, chat_id, message_id=None):
    """Hiển thị danh sách task với các nút action"""
    if user_id not in user_tasks or not user_tasks[user_id]:
        text = "📭 Danh sách trống!"
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_main")
        markup.add(btn_back)
    else:
        text = "📋 DANH SÁCH CÔNG VIỆC:\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, task in enumerate(user_tasks[user_id]):
            status = "✅" if task['done'] else "⏳"
            task_text = f"{idx+1}. {status} {task['content']}"
            
            if task.get('remind_time'):
                user_time = get_user_time(user_id, task['remind_time'])
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
@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id])
def handle_user_input(message):
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    state = user_states[user_id]
    print(f"Handling user input, state: {state}, text: {message.text}")
    
    # Thêm task
    if state == "waiting_task_content":
        task_content = message.text.strip()
        if chat_id not in user_tasks:
            user_tasks[user_id] = []
        
        user_tasks[user_id].append({
            'content': task_content,
            'done': False,
            'remind_time': None,
            'reminded': False
        })
        
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{len(user_tasks[user_id])-1}")
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="menu_add")
        markup.add(btn_remind)
        markup.add(btn_list, btn_add)
        
        bot.reply_to(message, 
            f"✅ Đã thêm: '{task_content}'\n\n"
            f"Bạn muốn làm gì tiếp theo?",
            reply_markup=markup
        )
    
    # Nhập giờ thủ công (HH:MM)
    elif state.startswith("manual_time_input_"):
        # State format: manual_time_input_{task_idx}_{date_str}
        # date_str có thể là "today" hoặc "YYYY_MM_DD"
        state_parts = state.split("_")
        task_idx = int(state_parts[3])
        
        # date_str có thể có dấu _ nên phải lấy từ index 4 trở đi
        date_str = "_".join(state_parts[4:])
        
        time_str = message.text.strip()
        print(f"Manual time input: task_idx={task_idx}, date_str={date_str}, time_str='{time_str}'")
        
        # Parse HH:MM hoặc H:MM
        try:
            # Kiểm tra format
            if ':' not in time_str:
                bot.reply_to(message, "⚠️ Sai định dạng! Nhập lại theo format HH:MM (ví dụ: 14:27)")
                return
            
            time_parts = time_str.split(':')
            
            # Phải có đúng 2 phần (giờ và phút)
            if len(time_parts) != 2:
                bot.reply_to(message, "⚠️ Sai định dạng! Nhập lại theo format HH:MM (ví dụ: 14:27)")
                return
            
            # Validate giờ và phút là số
            hour_str = time_parts[0].strip()
            minute_str = time_parts[1].strip()
            
            if not hour_str.isdigit() or not minute_str.isdigit():
                bot.reply_to(message, f"⚠️ Giờ và phút phải là số!\n\nBạn đã nhập: '{time_str}'\nVí dụ đúng: 14:27, 9:05")
                return
            
            hour = int(hour_str)
            minute = int(minute_str)
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                bot.reply_to(message, f"⚠️ Giờ phải từ 0-23 (bạn nhập {hour}), phút từ 0-59 (bạn nhập {minute})! Nhập lại:")
                return
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Tạo datetime với giờ local
            remind_local = selected_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            remind_utc = to_utc_time(user_id, remind_local)
            
            # Kiểm tra nếu là quá khứ
            if remind_utc <= datetime.utcnow():
                bot.reply_to(message, "⚠️ Thời gian phải là tương lai! Nhập lại:")
                return
            
            # Lưu reminder
            user_tasks[user_id][task_idx]['remind_time'] = remind_utc
            user_tasks[user_id][task_idx]['reminded'] = False
            user_states[user_id] = None
            
            task_content = user_tasks[user_id][task_idx]['content']
            remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
            
            markup = types.InlineKeyboardMarkup()
            btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
            btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
            markup.add(btn_list, btn_menu)
            
            bot.reply_to(message,
                f"⏰ Đã đặt nhắc nhở!\n\n"
                f"📌 {task_content}\n"
                f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
                reply_markup=markup
            )
        
        except (ValueError, IndexError) as e:
            print(f"Error parsing date or time: {e}")
            bot.reply_to(message, f"⚠️ Đã xảy ra lỗi khi xử lý!\n\nVui lòng thử lại hoặc dùng /cancel để hủy.")
    
    # Nhập phút thủ công
    elif state.startswith("manual_minute_input_"):
        # State format: manual_minute_input_{task_idx}_{hour}_{date_str}
        state_parts = state.split("_")
        task_idx = int(state_parts[3])
        hour = int(state_parts[4])
        
        # date_str có thể có dấu _ nên phải lấy từ index 5 trở đi
        date_str = "_".join(state_parts[5:])
        
        minute_str = message.text.strip()
        print(f"Manual minute input: task_idx={task_idx}, hour={hour}, date_str={date_str}, minute_str='{minute_str}'")
        
        try:
            # Validate là số
            if not minute_str.isdigit():
                bot.reply_to(message, f"⚠️ Phút phải là số từ 0-59!\n\nBạn đã nhập: '{minute_str}'")
                return
            
            minute = int(minute_str)
            print(f"Parsed minute: {minute}")
            
            if not (0 <= minute <= 59):
                bot.reply_to(message, f"⚠️ Phút phải từ 0-59 (bạn nhập {minute})! Nhập lại:")
                return
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Tạo datetime với giờ local
            remind_local = selected_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            remind_utc = to_utc_time(user_id, remind_local)
            
            # Kiểm tra nếu là quá khứ
            if remind_utc <= datetime.utcnow():
                bot.reply_to(message, "⚠️ Thời gian phải là tương lai! Nhập lại:")
                return
            
            # Lưu reminder
            user_tasks[user_id][task_idx]['remind_time'] = remind_utc
            user_tasks[user_id][task_idx]['reminded'] = False
            user_states[user_id] = None
            
            task_content = user_tasks[user_id][task_idx]['content']
            remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
            
            markup = types.InlineKeyboardMarkup()
            btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
            btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
            markup.add(btn_list, btn_menu)
            
            bot.reply_to(message,
                f"⏰ Đã đặt nhắc nhở!\n\n"
                f"📌 {task_content}\n"
                f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
                reply_markup=markup
            )
        
        except (ValueError, IndexError) as e:
            print(f"Error in manual minute input: {e}")
            bot.reply_to(message, "⚠️ Đã xảy ra lỗi!\n\nVui lòng thử lại hoặc dùng /cancel để hủy.")
    
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
        
        user_tasks[user_id][task_idx]['remind_time'] = remind_time
        user_tasks[user_id][task_idx]['reminded'] = False
        user_states[user_id] = None
        
        task_content = user_tasks[user_id][task_idx]['content']
        user_time = get_user_time(user_id, remind_time)
        remind_str = user_time.strftime("%d/%m/%Y %H:%M")
        
        markup = types.InlineKeyboardMarkup()
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.add(btn_list, btn_menu)
        
        bot.reply_to(message,
            f"⏰ Đã đặt nhắc nhở!\n\n"
            f"📌 {task_content}\n"
            f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
            reply_markup=markup
        )

# ============= NATURAL LANGUAGE HANDLER với AI =============

# ============= VOICE TO TEXT FEATURES =============

def download_voice_file(file_id):
    """Download voice file từ Telegram"""
    try:
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        
        # Download file
        response = requests.get(file_url, timeout=30)
        if response.status_code == 200:
            # Lưu tạm thời
            temp_filename = f"voice_{file_id}.ogg"
            with open(temp_filename, 'wb') as f:
                f.write(response.content)
            return temp_filename
        return None
    except Exception as e:
        print(f"Error downloading voice: {e}")
        return None

def transcribe_audio(audio_file_path):
    """Chuyển đổi audio thành text bằng OpenAI Whisper API"""
    if not OPENAI_API_KEY:
        return None
    
    try:
        # Sử dụng OpenAI Whisper API
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'file': (audio_file_path, audio_file, 'audio/ogg'),
                'model': (None, 'whisper-1'),
                'language': (None, 'vi'),  # Tiếng Việt
                'response_format': (None, 'text')
            }
            
            response = requests.post(url, headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Whisper API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    """Xử lý tin nhắn voice - chuyển đổi thành text"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    print(f"Voice message from user_id {user_id} (chat_id {chat_id})")
    
    # Kiểm tra có OpenAI API key không
    if not OPENAI_API_KEY:
        bot.reply_to(message, 
            "🎤 Tính năng chuyển đổi giọng nói cần OpenAI API key!\n\n"
            "📝 Thêm OPENAI_API_KEY vào file .env để sử dụng tính năng này.\n"
            "💡 Xem hướng dẫn: /help"
        )
        return
    
    # Gửi typing indicator
    bot.send_chat_action(chat_id, 'typing')
    
    # Thông báo đang xử lý
    processing_msg = bot.reply_to(message, "🎤 Đang xử lý giọng nói...")
    
    try:
        # Download voice file
        voice_file_id = message.voice.file_id
        audio_path = download_voice_file(voice_file_id)
        
        if not audio_path:
            bot.edit_message_text(
                "❌ Không thể tải xuống file giọng nói.",
                chat_id=chat_id,
                message_id=processing_msg.message_id
            )
            return
        
        # Cập nhật status
        bot.edit_message_text(
            "🤖 Đang chuyển đổi giọng nói thành văn bản...",
            chat_id=chat_id,
            message_id=processing_msg.message_id
        )
        
        # Transcribe audio
        transcribed_text = transcribe_audio(audio_path)
        
        # Xóa file tạm
        try:
            os.remove(audio_path)
        except:
            pass
        
        if not transcribed_text:
            bot.edit_message_text(
                "❌ Không thể chuyển đổi giọng nói. Vui lòng thử lại.",
                chat_id=chat_id,
                message_id=processing_msg.message_id
            )
            return
        
        # Tạo file txt (riêng tư cho từng user)
        txt_filename = f"transcription_{user_id}_{int(time.time())}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=== CHUYỂN ĐỔI GIỌNG NÓI THÀNH VĂN BẢN ===\n")
            f.write(f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Người dùng: {message.from_user.first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(transcribed_text)
        
        # Gửi file txt VỀ PRIVATE CHAT của user (không gửi vào group)
        # Đảm bảo privacy: mỗi user chỉ nhìn thấy transcription của chính mình
        try:
            # Tạo inline keyboard với nút quay lại menu
            markup = types.InlineKeyboardMarkup()
            btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
            markup.add(btn_menu)
            
            with open(txt_filename, 'rb') as f:
                bot.send_document(
                    user_id,  # Gửi về user_id (private chat), không gửi vào group
                    f,
                    caption=f"📝 **Nội dung văn bản:**\n\n{transcribed_text}\n\n✅ File đã được tạo!",
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            
            # Nếu voice được gửi từ group, thông báo user check private chat
            if chat_id != user_id:  # Nếu là group chat
                # Xóa file txt tạm
                try:
                    os.remove(txt_filename)
                except:
                    pass
                
                # Tạo inline keyboard với nút quay lại menu
                markup = types.InlineKeyboardMarkup()
                btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
                markup.add(btn_menu)
                
                bot.edit_message_text(
                    "✅ Đã chuyển đổi xong! Tôi đã gửi file txt vào chat riêng với bạn để đảm bảo riêng tư. 🔒",
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    reply_markup=markup
                )
                return
                
        except telebot.apihelper.ApiTelegramException as api_error:
            # Không thể gửi vào private chat (user chưa start bot)
            if "bot can't initiate conversation" in str(api_error) or "Forbidden" in str(api_error):
                # Xóa file txt tạm
                try:
                    os.remove(txt_filename)
                except:
                    pass
                
                # Tạo inline keyboard với nút quay lại menu
                markup = types.InlineKeyboardMarkup()
                btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
                markup.add(btn_menu)
                
                bot.edit_message_text(
                    "⚠️ **Không thể gửi file txt vào chat riêng!**\n\n"
                    "📝 Để nhận transcription riêng tư, bạn cần:\n"
                    "1️⃣ Mở chat riêng với bot\n"
                    "2️⃣ Gửi lệnh /start\n"
                    "3️⃣ Sau đó gửi lại voice message\n\n"
                    "🔒 Điều này đảm bảo các members khác không thấy nội dung của bạn!",
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    reply_markup=markup
                )
                return
            else:
                # Lỗi khác, re-raise để exception handler chính xử lý
                raise
        
        # Xóa file txt tạm (private chat)
        try:
            os.remove(txt_filename)
        except:
            pass
        
        # Xóa processing message (private chat)
        bot.delete_message(chat_id, processing_msg.message_id)
        
    except Exception as e:
        print(f"Error handling voice message: {e}")
        # Cleanup file nếu còn
        try:
            if 'txt_filename' in locals():
                os.remove(txt_filename)
        except:
            pass
        try:
            if 'audio_path' in locals():
                os.remove(audio_path)
        except:
            pass
        
        # Hiển thị lỗi cho user
        error_msg = "⚠️ Đã xảy ra lỗi khi xử lý!\n\n"
        
        # Phân tích lỗi cụ thể
        if "insufficient_quota" in str(e) or "quota" in str(e).lower():
            error_msg += "💳 **Lỗi OpenAI API:** Tài khoản hết credits\n\n"
            error_msg += "📝 Giải pháp:\n"
            error_msg += "• Thêm payment method tại: platform.openai.com\n"
            error_msg += "• Nạp credits ($5 = 833 phút voice)\n"
            error_msg += "• Kiểm tra usage tại: platform.openai.com/usage"
        elif "401" in str(e) or "authentication" in str(e).lower():
            error_msg += "🔑 **Lỗi API Key:** OpenAI key không hợp lệ\n\n"
            error_msg += "📝 Giải pháp:\n"
            error_msg += "• Kiểm tra OPENAI_API_KEY trong .env\n"
            error_msg += "• Tạo key mới tại: platform.openai.com/api-keys"
        elif "timeout" in str(e).lower() or "connection" in str(e).lower():
            error_msg += "🌐 **Lỗi mạng:** Không thể kết nối OpenAI API\n\n"
            error_msg += "📝 Vui lòng thử lại sau vài phút"
        else:
            error_msg += f"📝 Chi tiết: {str(e)[:100]}\n\n"
            error_msg += "💡 Vui lòng thử lại hoặc liên hệ admin"
        
        try:
            bot.edit_message_text(
                error_msg,
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
        except:
            try:
                bot.reply_to(message, error_msg, parse_mode='Markdown')
            except:
                bot.reply_to(message, "⚠️ Đã xảy ra lỗi khi xử lý! Vui lòng thử lại.")

# Xử lý tin nhắn ngôn ngữ tự nhiên (không phải lệnh, không trong state)
@bot.message_handler(func=lambda message: message.chat.id not in user_states or not user_states[message.chat.id])
def handle_natural_language(message):
    """Xử lý ngôn ngữ tự nhiên với AI"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    user_text = message.text.strip()
    
    # Bỏ qua nếu là lệnh
    if user_text.startswith('/'):
        return
    
    print(f"Natural language input from user_id {user_id} (chat_id {chat_id}): {user_text}")
    
    # Nếu không có GitHub token, sử dụng mode thông thường
    if not GITHUB_TOKEN:
        bot.reply_to(message, 
            "💡 Gửi tin nhắn tự do! Nhưng cần GitHub token để kích hoạt AI.\n\n"
            "Dùng /add để thêm task hoặc chọn menu bên dưới.",
            reply_markup=show_main_menu(user_id)[1]
        )
        return
    
    # Gửi typing indicator
    bot.send_chat_action(chat_id, 'typing')
    
    # Parse với AI
    ai_result = parse_natural_language_task(user_text, user_id)
    
    if not ai_result:
        # AI không trả về kết quả, fallback
        bot.reply_to(message,
            "🤔 Tôi chưa hiểu rõ ý bạn.\n\n"
            "Thử lại hoặc dùng /add để thêm task.",
            reply_markup=show_main_menu(user_id)[1]
        )
        return
    
    # Tạo task từ AI result
    task_content = ai_result.get('task', user_text)
    has_reminder = ai_result.get('has_reminder', False)
    time_str = ai_result.get('time', '')
    
    # Thêm task
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    
    task_idx = len(user_tasks[user_id])
    user_tasks[user_id].append({
        'content': task_content,
        'done': False,
        'remind_time': None,
        'reminded': False
    })
    
    response_text = f"✅ Đã thêm: '{task_content}'"
    
    # Xử lý reminder nếu có
    if has_reminder and time_str:
        remind_time = parse_time(time_str, user_id)
        if remind_time and remind_time > datetime.utcnow():
            user_tasks[user_id][task_idx]['remind_time'] = remind_time
            user_tasks[user_id][task_idx]['reminded'] = False
            
            user_time = get_user_time(user_id, remind_time)
            remind_str = user_time.strftime("%d/%m/%Y %H:%M")
            response_text += f"\n⏰ Nhắc nhở: {remind_str}"
    
    # Hiển thị với buttons
    markup = types.InlineKeyboardMarkup()
    if not has_reminder or not time_str:
        btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{task_idx}")
        markup.add(btn_remind)
    btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
    btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="menu_add")
    markup.add(btn_list, btn_add)
    
    bot.reply_to(message, response_text + "\n\n🤖 Phân tích bởi AI", reply_markup=markup)

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
