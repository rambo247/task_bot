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

# Background thread để kiểm tra và gửi reminder
def reminder_checker():
    """Kiểm tra và gửi thông báo nhắc nhở"""
    while True:
        try:
            current_time = datetime.now()
            for chat_id, tasks in list(user_tasks.items()):
                for task in tasks:
                    if task.get('remind_time') and not task.get('reminded'):
                        remind_time = task['remind_time']
                        # Kiểm tra nếu đã đến giờ nhắc (trong vòng 1 phút)
                        if remind_time <= current_time < remind_time + timedelta(minutes=1):
                            try:
                                reminder_text = f"⏰ NHẮC NHỞ!\n\n📌 {task['content']}"
                                if task.get('done'):
                                    reminder_text += "\n\n✅ (Đã hoàn thành)"
                                bot.send_message(chat_id, reminder_text)
                                task['reminded'] = True
                            except Exception as e:
                                print(f"Error sending reminder: {e}")
            time.sleep(30)  # Kiểm tra mỗi 30 giây
        except Exception as e:
            print(f"Error in reminder_checker: {e}")
            time.sleep(30)

# Khởi động background thread
reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
reminder_thread.start()

# Lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
    welcome_text = (
        "👋 Xin chào! Tôi là bot nhắc việc của bạn.\n\n"
        "📋 Các lệnh hỗ trợ:\n"
        "/add [Nội dung task] - Thêm công việc mới\n"
        "/remind [Số thứ tự] [Thời gian] - Đặt nhắc nhở\n"
        "/list - Xem danh sách công việc\n"
        "/done [Số thứ tự] - Đánh dấu hoàn thành\n"
        "/delete [Số thứ tự] - Xóa một công việc\n"
        "/clear - Xóa toàn bộ danh sách công việc\n"
        "/help - Xem hướng dẫn"
    )
    bot.reply_to(bot_message, welcome_text)

# Lệnh /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📚 Hướng dẫn sử dụng bot:\n\n"
        "➕ Thêm công việc:\n"
        "⏰ Đặt nhắc nhở:\n"
        "   /remind 1 14:30 (hôm nay)\n"
        "   /remind 1 2026-07-23 09:00\n"
        "   /remind 1 30m (sau 30 phút)\n"
        "   /remind 1 2h (sau 2 giờ)\n\n"
        "   /add Họp lúc 9h sáng\n\n"
        "📝 Xem danh sách:\n"
        "   /list\n\n"
        "✅ Hoàn thành công việc:\n"
        "   /done 1\n\n"
        "🗑️ Xóa công việc:\n"
        "   /delete 2\n\n"
        "🧹 Xóa tất cả:\n"
        "   /clear"
    )
    bot.reply_to(message, help_text)

# Lệnh /add để thêm task
@bot.message_handler(commands=['add'])
def add_task(message):
    chat_id = message.chat.id
    # Lấy nội dung sau lệnh /add
    task_content = message.text[len('/add '):].strip()
    
    if not task_content:
        bot.reply_to(message, "⚠️ Vui lòng nhập nội dung công việc.\n\nVí dụ: /add Họp lúc 9h sáng")
        return

    if chat_id not in user_tasks:
        user_tasks[chat_id] = []
    
    user_tasks[chat_id].append({
        'content': task_content, 
        'done': False,
        'remind_time': None,
        'reminded': False
    })
    
    response = f"✅ Đã thêm công việc: '{task_content}'\n\n"
    response += f"💡 Đặt nhắc nhở với:\n/remind {len(user_tasks[chat_id])} [thời gian]"
    bot.reply_to(message, response)

# Lệnh /list để xem danh sách task
@bot.message_handler(commands=['list'])
def list_tasks(message):
    chat_id = message.chat.id
    
    if chat_id not in user_tasks or not user_tasks[chat_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    tasks_text = "📋 Danh sách công việc:\n\n"
    for index, task in enumerate(user_tasks[chat_id], 1):
        status = "✅" if task['done'] else "⏳"
        tasks_text += f"{index}. {status} {task['content']}"
        
        # Hiển thị thời gian nhắc nhở nếu có
        if task.get('remind_time'):
            remind_str = task['remind_time'].strftime("%d/%m/%Y %H:%M")
            if task.get('reminded'):
                tasks_text += f"\n   🔔 Đã nhắc: {remind_str}"
            else:
                tasks_text += f"\n   ⏰ Nhắc lúc: {remind_str}"
        
        tasks_text += "\n"
        
    bot.reply_to(message, tasks_text)

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
        
        # Parse thời gian
        remind_time = parse_time(time_str)
        
        if remind_time is None:
            bot.reply_to(message, 
                "⚠️ Định dạng thời gian không hợp lệ!\n\n"
                "Các định dạng hỗ trợ:\n"
                "• HH:MM (ví dụ: 14:30)\n"
                "• YYYY-MM-DD HH:MM\n"
                "• 30m (sau 30 phút)\n"
                "• 2h (sau 2 giờ)")
            return
        
        if remind_time <= datetime.now():
            bot.reply_to(message, "⚠️ Thời gian nhắc nhở phải là thời điểm trong tương lai!")
            return
        
        # Cập nhật reminder
        user_tasks[chat_id][task_number - 1]['remind_time'] = remind_time
        user_tasks[chat_id][task_number - 1]['reminded'] = False
        
        task_content = user_tasks[chat_id][task_number - 1]['content']
        remind_str = remind_time.strftime("%d/%m/%Y %H:%M")
        
        bot.reply_to(message, 
            f"⏰ Đã đặt nhắc nhở!\n\n"
            f"📌 Công việc: {task_content}\n"
            f"🕐 Thời gian: {remind_str}")
        
    except (IndexError, ValueError) as e:
        bot.reply_to(message, 
            "⚠️ Lỗi định dạng!\n\n"
            "Sử dụng: /remind [số] [thời gian]\n"
            "Ví dụ: /remind 1 14:30")

def parse_time(time_str):
    """Parse nhiều định dạng thời gian"""
    try:
        # Định dạng: 30m, 2h, 1d (relative time)
        if time_str.endswith('m'):
            minutes = int(time_str[:-1])
            return datetime.now() + timedelta(minutes=minutes)
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            return datetime.now() + timedelta(hours=hours)
        elif time_str.endswith('d'):
            days = int(time_str[:-1])
            return datetime.now() + timedelta(days=days)
        
        # Định dạng: HH:MM (hôm nay)
        if ':' in time_str and len(time_str.split()) == 1:
            time_parts = time_str.split(':')
            if len(time_parts) == 2:
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                remind_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Nếu thời gian đã qua trong ngày hôm nay, chuyển sang ngày mai
                if remind_time <= datetime.now():
                    remind_time += timedelta(days=1)
                
                return remind_time
        
        # Định dạng: YYYY-MM-DD HH:MM
        if len(time_str.split()) == 2:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        
        # Định dạng: DD/MM/YYYY HH:MM
        if '/' in time_str:
            return datetime.strptime(time_str, "%d/%m/%Y %H:%M")
        
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
    
    if call.data == "clear_yes":
        user_tasks[chat_id] = []
        bot.edit_message_text(
            "🧹 Đã xóa toàn bộ danh sách công việc!",
            chat_id=chat_id,
            message_id=call.message.message_id
        )
    elif call.data == "clear_no":
        bot.edit_message_text(
            "❌ Đã hủy thao tác xóa.",
            chat_id=chat_id,
            message_id=call.message.message_id
        )

# Chạy bot
if __name__ == "__main__":
    print("🤖 Bot đang chạy...")
    print(f"📱 Bot name: @{bot.get_me().username}")
    bot.infinity_polling()
