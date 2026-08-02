"""
Script thêm task mẫu để test chức năng xem danh sách
"""

import json
from pathlib import Path
import sys

DATA_DIR = Path(__file__).parent / 'data'

def add_sample_tasks(user_id=None):
    """Thêm task mẫu vào hệ thống"""
    
    if user_id is None:
        print("⚠️ Cần nhập User ID!")
        print("\nCách lấy User ID:")
        print("1. Khởi động bot: python task_bot.py")
        print("2. Gửi /start cho bot trên Telegram")
        print("3. Xem log terminal, sẽ có dòng 'user_id: XXXXXXX'")
        print("\nSau đó chạy: python add_sample_tasks.py YOUR_USER_ID")
        return
    
    # Tạo thư mục data nếu chưa có
    DATA_DIR.mkdir(exist_ok=True)
    
    # Đọc dữ liệu hiện tại
    user_tasks_file = DATA_DIR / 'user_tasks.json'
    
    if user_tasks_file.exists():
        with open(user_tasks_file, 'r', encoding='utf-8') as f:
            user_tasks = json.load(f)
    else:
        user_tasks = {}
    
    # Thêm task mẫu
    sample_tasks = [
        {
            "content": "✍️ Task mẫu 1: Họp team lúc 9h",
            "done": False,
            "remind_time": None,
            "reminded": False
        },
        {
            "content": "📧 Task mẫu 2: Gửi email báo cáo",
            "done": False,
            "remind_time": None,
            "reminded": False
        },
        {
            "content": "🎯 Task mẫu 3: Hoàn thành dự án",
            "done": True,
            "remind_time": None,
            "reminded": False
        },
        {
            "content": "📚 Task mẫu 4: Đọc tài liệu",
            "done": False,
            "remind_time": None,
            "reminded": False
        }
    ]
    
    user_tasks[str(user_id)] = sample_tasks
    
    # Lưu lại
    with open(user_tasks_file, 'w', encoding='utf-8') as f:
        json.dump(user_tasks, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("✅ ĐÃ THÊM TASK MẪU THÀNH CÔNG!")
    print("=" * 60)
    print(f"\n👤 User ID: {user_id}")
    print(f"📋 Số lượng task: {len(sample_tasks)}")
    print(f"\nDanh sách tasks đã thêm:")
    
    for idx, task in enumerate(sample_tasks, 1):
        status = "✅" if task['done'] else "⏳"
        print(f"  {idx}. {status} {task['content']}")
    
    print("\n" + "=" * 60)
    print("🎯 BƯỚC TIẾP THEO:")
    print("=" * 60)
    print("""
1. Restart bot nếu đang chạy:
   • Nhấn Ctrl+C để dừng bot
   • Chạy lại: python task_bot.py

2. Trên Telegram:
   • Gửi /list cho bot
   • Hoặc nhấn nút "📋 Xem danh sách"

3. Bạn sẽ thấy 4 task mẫu ở trên!

💡 Nếu vẫn không thấy:
   • Kiểm tra User ID có đúng không
   • Xem log terminal khi gửi /start
   • Chạy: python check_tasks.py để kiểm tra lại
    """)

def main():
    if len(sys.argv) < 2:
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 10 + "THÊM TASK MẪU ĐỂ TEST BOT" + " " * 22 + "║")
        print("╚" + "=" * 58 + "╝")
        print("\n❌ Thiếu User ID!\n")
        print("Cách sử dụng:")
        print("  python add_sample_tasks.py YOUR_USER_ID")
        print("\nVí dụ:")
        print("  python add_sample_tasks.py 123456789")
        print("\n" + "=" * 60)
        print("🔍 CÁCH LẤY USER ID:")
        print("=" * 60)
        print("""
1. Khởi động bot:
   python task_bot.py

2. Trên Telegram, gửi /start cho bot

3. Xem log trong terminal, sẽ có dòng:
   "Received callback: menu_main from chat_id: XXX, user_id: YYYYYYY"
   
4. YYYYYYY chính là User ID của bạn

5. Chạy lại script với User ID đó:
   python add_sample_tasks.py YYYYYYY
        """)
    else:
        try:
            user_id = int(sys.argv[1])
            add_sample_tasks(user_id)
        except ValueError:
            print("❌ User ID phải là số!")
            print("Ví dụ: python add_sample_tasks.py 123456789")

if __name__ == "__main__":
    main()
