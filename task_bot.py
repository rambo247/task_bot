import telebot
import os
from telebot import types

# Lấy token từ biến môi trường hoặc sử dụng token mặc định
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8802370170:AAEGZU_Df5OnDQTO7kn9lyf2UzeIbbh2KPk')
bot = telebot.TeleBot(TOKEN)

# Lưu trữ danh sách task tạm thời theo Chat ID
user_tasks = {}

# Lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
    welcome_text = (
        "👋 Xin chào! Tôi là bot nhắc việc của bạn.\n\n"
        "📋 Các lệnh hỗ trợ:\n"
        "/add [Nội dung task] - Thêm công việc mới\n"
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
    
    user_tasks[chat_id].append({'content': task_content, 'done': False})
    bot.reply_to(message, f"✅ Đã thêm công việc: '{task_content}'")

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
        tasks_text += f"{index}. {status} {task['content']}\n"
        
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
