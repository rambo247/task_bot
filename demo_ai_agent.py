"""
Demo & Interactive Test cho AI Task Agent
Chạy file này để test AI Agent một cách interactive
"""

from ai_task_agent import AITaskAgent
import json


def print_separator(title=""):
    """In separator đẹp"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    else:
        print('-'*60)


def print_result(result):
    """In kết quả đẹp"""
    print(f"\n📊 Kết quả:")
    print(f"   Action: {result['action']}")
    print(f"   Missing: {result['missing_fields']}")
    print(f"\n💬 Bot Response:")
    print(f"   {result['ask_message']}")
    print(f"\n📋 Task Data:")
    print(json.dumps(result['task'], indent=3, ensure_ascii=False))


def demo_full_info():
    """Demo: Tin nhắn đầy đủ thông tin"""
    print_separator("DEMO 1: TIN NHẮN ĐẦY ĐỦ THÔNG TIN")
    
    agent = AITaskAgent()
    
    message = """
    Tên: Thiết kế landing page cho campaign mùa hè
    Người làm: Nguyễn Văn A
    Deadline: 2026-08-15
    Nhóm: Marketing
    Trạng thái: Đang làm
    Tiến độ: 25%
    Chi tiết: Thiết kế landing page đẹp mắt, responsive
    """
    
    print(f"\n📩 User Message:")
    print(message)
    
    result = agent.process_message(message)
    print_result(result)


def demo_partial_info():
    """Demo: Tin nhắn thiếu thông tin"""
    print_separator("DEMO 2: TIN NHẮN THIẾU THÔNG TIN")
    
    agent = AITaskAgent()
    
    message = "Tạo chiến dịch marketing mới"
    
    print(f"\n📩 User Message:")
    print(f"   {message}")
    
    result = agent.process_message(message)
    print_result(result)


def demo_natural_language():
    """Demo: Natural language format"""
    print_separator("DEMO 3: NATURAL LANGUAGE FORMAT")
    
    agent = AITaskAgent()
    
    message = "Họp team planning với Nguyễn Văn B deadline 20/08/2026 cho dự án Website"
    
    print(f"\n📩 User Message:")
    print(f"   {message}")
    
    result = agent.process_message(message)
    print_result(result)


def demo_conversation_flow():
    """Demo: Conversation flow với bổ sung dần"""
    print_separator("DEMO 4: CONVERSATION FLOW (BỔ SUNG DẦN)")
    
    agent = AITaskAgent()
    
    turns = [
        ("Tạo task mới cho dự án Tech", None),
        ("Tên là 'Phát triển API v2'", None),
        ("Người làm là Trần Văn C", None),
        ("Deadline 20/08/2026", None),
    ]
    
    context = {}
    
    for i, (user_msg, _) in enumerate(turns, 1):
        print(f"\n🔄 Turn {i}:")
        print(f"   👤 User: {user_msg}")
        
        result = agent.process_message(user_msg, context)
        
        print(f"   🤖 Bot: {result['ask_message']}")
        print(f"   📊 Action: {result['action']}")
        print(f"   ⚠️ Missing: {result['missing_fields']}")
        
        # Update context
        context = result['task']
        
        if result['action'] == 'save_task':
            print(f"\n✅ HOÀN TẤT! Task đã đủ thông tin.")
            print(f"\n📋 Final Task Data:")
            print(json.dumps(result['task'], indent=3, ensure_ascii=False))
            break


def demo_various_formats():
    """Demo: Nhiều format khác nhau"""
    print_separator("DEMO 5: NHIỀU FORMAT KHÁC NHAU")
    
    agent = AITaskAgent()
    
    test_cases = [
        {
            "name": "Format Key-Value với dấu hai chấm",
            "message": "Tên: Design UI\nNgười làm: John\nDeadline: 2026-08-25"
        },
        {
            "name": "Format tự nhiên có @mention",
            "message": "Tạo task viết docs cho @TrầnVănD deadline 30/08"
        },
        {
            "name": "Format ngắn gọn",
            "message": "Meeting với team marketing ngày 18/08"
        },
        {
            "name": "Format JSON-like",
            "message": '{"task_name": "Review code", "assignee": "Lê Văn E", "deadline": "2026-08-12"}'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print_separator()
        print(f"📩 Input: {test_case['message']}")
        
        result = agent.process_message(test_case['message'])
        
        print(f"\n   Action: {result['action']}")
        print(f"   Missing: {result['missing_fields']}")
        
        if result['task'].get('task_name'):
            print(f"   ✅ Task Name: {result['task']['task_name']}")
        if result['task'].get('assignee'):
            print(f"   ✅ Assignee: {result['task']['assignee']}")
        if result['task'].get('deadline'):
            print(f"   ✅ Deadline: {result['task']['deadline']}")


def interactive_mode():
    """Chế độ interactive - test với input tùy ý"""
    print_separator("CHẾ ĐỘ INTERACTIVE")
    
    agent = AITaskAgent()
    context = {}
    
    print("\n🤖 Chào bạn! Tôi là AI Task Agent.")
    print("💡 Bạn có thể nhập thông tin task để test.")
    print("⚠️ Gõ 'quit' hoặc 'exit' để thoát.\n")
    
    turn = 1
    
    while True:
        user_input = input(f"👤 Turn {turn} - Bạn: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Tạm biệt!")
            break
        
        if not user_input:
            continue
        
        result = agent.process_message(user_input, context)
        
        print(f"\n🤖 Bot: {result['ask_message']}")
        print(f"📊 Status: {result['action']}")
        
        if result['missing_fields']:
            print(f"⚠️ Missing: {', '.join(result['missing_fields'])}")
        
        # Update context
        context = result['task']
        
        if result['action'] == 'save_task':
            print(f"\n✅ HOÀN TẤT! Task đã được lưu.")
            print(f"\n📋 Task Data:")
            print(json.dumps(result['task'], indent=2, ensure_ascii=False))
            
            # Reset
            print("\n🔄 Bạn có thể tạo task mới...\n")
            context = {}
            turn = 1
        else:
            turn += 1
        
        print()


def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("  🤖 AI TASK AGENT - DEMO & TEST")
        print("="*60)
        print("\n📋 Chọn demo:")
        print("   1. Demo 1: Tin nhắn đầy đủ thông tin")
        print("   2. Demo 2: Tin nhắn thiếu thông tin")
        print("   3. Demo 3: Natural language format")
        print("   4. Demo 4: Conversation flow (bổ sung dần)")
        print("   5. Demo 5: Nhiều format khác nhau")
        print("   6. 🎮 Interactive Mode (Test tự do)")
        print("   7. 🚀 Chạy tất cả demos")
        print("   0. Thoát")
        
        choice = input("\n➡️ Lựa chọn của bạn: ").strip()
        
        if choice == '1':
            demo_full_info()
        elif choice == '2':
            demo_partial_info()
        elif choice == '3':
            demo_natural_language()
        elif choice == '4':
            demo_conversation_flow()
        elif choice == '5':
            demo_various_formats()
        elif choice == '6':
            interactive_mode()
        elif choice == '7':
            demo_full_info()
            demo_partial_info()
            demo_natural_language()
            demo_conversation_flow()
            demo_various_formats()
        elif choice == '0':
            print("\n👋 Tạm biệt!")
            break
        else:
            print("\n⚠️ Lựa chọn không hợp lệ!")
        
        input("\n⏎ Nhấn Enter để tiếp tục...")


if __name__ == '__main__':
    main()
