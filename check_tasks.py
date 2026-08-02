"""
Script kiểm tra và sửa lỗi xem task
Kiểm tra dữ liệu task hiện tại và khắc phục các vấn đề
"""

import json
import os
from pathlib import Path

# Đường dẫn đến thư mục data
DATA_DIR = Path(__file__).parent / 'data'

def check_data_directory():
    """Kiểm tra xem thư mục data có tồn tại không"""
    print("\n🔍 KIỂM TRA THƯ MỤC DATA")
    print("=" * 50)
    
    if DATA_DIR.exists():
        print(f"✅ Thư mục data tồn tại: {DATA_DIR}")
        print(f"📂 Các file trong thư mục:")
        
        files = list(DATA_DIR.glob('*.json'))
        if files:
            for file in files:
                size = file.stat().st_size
                print(f"   • {file.name} ({size} bytes)")
        else:
            print("   ⚠️ Không có file JSON nào trong thư mục")
    else:
        print(f"❌ Thư mục data KHÔNG tồn tại: {DATA_DIR}")
        print("💡 Đang tạo thư mục data...")
        DATA_DIR.mkdir(exist_ok=True)
        print("✅ Đã tạo thư mục data thành công")

def check_user_tasks():
    """Kiểm tra dữ liệu user_tasks"""
    print("\n📋 KIỂM TRA DỮ LIỆU TASKS")
    print("=" * 50)
    
    user_tasks_file = DATA_DIR / 'user_tasks.json'
    
    if user_tasks_file.exists():
        try:
            with open(user_tasks_file, 'r', encoding='utf-8') as f:
                user_tasks = json.load(f)
            
            print(f"✅ File user_tasks.json tồn tại")
            print(f"👥 Số lượng user có task: {len(user_tasks)}")
            
            if user_tasks:
                print("\n📊 Chi tiết tasks theo user:")
                for user_id, tasks in user_tasks.items():
                    print(f"\n   User ID: {user_id}")
                    print(f"   Số lượng task: {len(tasks)}")
                    
                    if tasks:
                        print(f"   Danh sách tasks:")
                        for idx, task in enumerate(tasks, 1):
                            status = "✅" if task.get('done', False) else "⏳"
                            content = task.get('content', 'N/A')
                            print(f"      {idx}. {status} {content}")
                            
                            if task.get('remind_time'):
                                print(f"         ⏰ Nhắc nhở: {task['remind_time']}")
            else:
                print("⚠️ File tồn tại nhưng không có dữ liệu task nào")
                
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi đọc file JSON: {e}")
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
    else:
        print(f"❌ File user_tasks.json KHÔNG tồn tại")
        print("💡 Tạo file mẫu để test...")
        create_sample_tasks()

def create_sample_tasks():
    """Tạo dữ liệu task mẫu để test"""
    print("\n🔧 TẠO DỮ LIỆU MẪU")
    print("=" * 50)
    
    # Tạo thư mục data nếu chưa có
    DATA_DIR.mkdir(exist_ok=True)
    
    # Dữ liệu mẫu
    sample_data = {
        "123456789": [  # Thay bằng user ID thật của bạn
            {
                "content": "Task mẫu 1 - Kiểm tra bot",
                "done": False,
                "remind_time": None,
                "reminded": False
            },
            {
                "content": "Task mẫu 2 - Test xem danh sách",
                "done": True,
                "remind_time": None,
                "reminded": False
            }
        ]
    }
    
    user_tasks_file = DATA_DIR / 'user_tasks.json'
    
    try:
        with open(user_tasks_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Đã tạo file mẫu: {user_tasks_file}")
        print(f"💡 Bạn cần thay user ID '123456789' bằng user ID thật của bạn")
        print(f"   Để lấy user ID, gửi /start cho bot và kiểm tra log")
    except Exception as e:
        print(f"❌ Lỗi tạo file mẫu: {e}")

def check_all_data_files():
    """Kiểm tra tất cả các file dữ liệu"""
    print("\n📁 KIỂM TRA TẤT CẢ CÁC FILE DỮ LIỆU")
    print("=" * 50)
    
    data_files = [
        'user_tasks.json',
        'user_timezones.json',
        'user_states.json',
        'user_chat_mapping.json',
        'ai_knowledge_base.json',
        'user_ai_chat_mode.json',
        'organizations.json',
        'user_organizations.json',
        'user_active_org.json',
        'departments.json',
        'contacts.json',
        'web_sources.json',
        'proactive_suggestions.json',
    ]
    
    for filename in data_files:
        filepath = DATA_DIR / filename
        
        if filepath.exists():
            size = filepath.stat().st_size
            status = "✅" if size > 2 else "⚠️"  # 2 bytes = "{}"
            print(f"{status} {filename}: {size} bytes")
        else:
            print(f"❌ {filename}: Không tồn tại")

def fix_empty_data_files():
    """Tạo các file dữ liệu trống nếu chưa tồn tại"""
    print("\n🔧 TẠO CÁC FILE DỮ LIỆU TRỐNG")
    print("=" * 50)
    
    # Tạo thư mục data nếu chưa có
    DATA_DIR.mkdir(exist_ok=True)
    
    data_files = [
        'user_tasks.json',
        'user_timezones.json',
        'user_states.json',
        'user_chat_mapping.json',
        'ai_knowledge_base.json',
        'user_ai_chat_mode.json',
        'organizations.json',
        'user_organizations.json',
        'user_active_org.json',
        'departments.json',
        'contacts.json',
        'web_sources.json',
        'proactive_suggestions.json',
    ]
    
    created_count = 0
    
    for filename in data_files:
        filepath = DATA_DIR / filename
        
        if not filepath.exists():
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                print(f"✅ Đã tạo: {filename}")
                created_count += 1
            except Exception as e:
                print(f"❌ Lỗi tạo {filename}: {e}")
    
    if created_count > 0:
        print(f"\n✅ Đã tạo {created_count} file dữ liệu")
    else:
        print("\n✅ Tất cả các file đã tồn tại")

def main():
    """Chạy tất cả các kiểm tra"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "CHẨN ĐOÁN VÀ SỬA LỖI TASK BOT" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 1. Kiểm tra thư mục data
    check_data_directory()
    
    # 2. Tạo các file trống nếu cần
    fix_empty_data_files()
    
    # 3. Kiểm tra tất cả file dữ liệu
    check_all_data_files()
    
    # 4. Kiểm tra chi tiết user_tasks
    check_user_tasks()
    
    print("\n" + "=" * 60)
    print("🎯 HƯỚNG DẪN TIẾP THEO")
    print("=" * 60)
    print("""
1. Nếu bạn chưa có task nào:
   • Chạy bot (python task_bot.py)
   • Gửi /start cho bot
   • Thêm task bằng menu hoặc /add [nội dung]
   • Sau đó chạy lại script này để kiểm tra

2. Nếu đã có task nhưng không xem được:
   • Kiểm tra User ID trong log khi gửi /start
   • Xác nhận User ID trong file user_tasks.json
   • Restart bot và thử lại /list

3. Để xem task:
   • Gửi /list cho bot
   • Hoặc nhấn nút "📋 Xem danh sách" trong menu

4. Để test với dữ liệu mẫu:
   • Chạy: python check_tasks.py --create-sample
   • Sửa User ID trong data/user_tasks.json
   • Restart bot và thử /list
    """)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample":
        # Chế độ tạo dữ liệu mẫu
        DATA_DIR.mkdir(exist_ok=True)
        create_sample_tasks()
    else:
        # Chế độ kiểm tra thông thường
        main()
