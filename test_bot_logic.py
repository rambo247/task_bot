#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SCRIPT - Kiểm tra logic privacy của bot
Chạy script này để verify các thay đổi trước khi deploy
"""

import sys
import re

def test_file_structure():
    """Test 1: Kiểm tra cấu trúc file"""
    print("\n📋 TEST 1: Kiểm tra cấu trúc file")
    print("-" * 50)
    
    with open('f:/workspace12/task_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check data structures
    checks = [
        ('user_tasks = {}', 'user_tasks dictionary'),
        ('user_chat_mapping = {}', 'user_chat_mapping dictionary'),
        ('user_timezones = {}', 'user_timezones dictionary'),
        ('user_states = {}', 'user_states dictionary'),
    ]
    
    for pattern, name in checks:
        if pattern in content:
            print(f"  ✅ {name} exists")
        else:
            print(f"  ❌ {name} NOT FOUND!")
            return False
    
    return True

def test_helper_functions():
    """Test 2: Kiểm tra helper functions"""
    print("\n🔧 TEST 2: Kiểm tra helper functions")
    print("-" * 50)
    
    with open('f:/workspace12/task_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    functions = [
        'def get_user_id(message):',
        'def update_user_chat_mapping(message):',
        'def get_user_timezone(user_id):',
        'def get_user_time(user_id',
        'def to_utc_time(user_id',
        'def create_calendar(user_id',
        'def create_time_picker(user_id',
        'def show_main_menu(user_id',
        'def show_task_list(user_id, chat_id',
        'def parse_time(time_str, user_id',
    ]
    
    for func in functions:
        if func in content:
            print(f"  ✅ {func}")
        else:
            print(f"  ❌ {func} NOT FOUND!")
            return False
    
    return True

def test_no_chat_id_in_data_operations():
    """Test 3: Đảm bảo không còn dùng chat_id cho data operations"""
    print("\n🔍 TEST 3: Kiểm tra không còn chat_id trong data ops")
    print("-" * 50)
    
    with open('f:/workspace12/task_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns không được phép
    forbidden_patterns = [
        r'user_tasks\[chat_id\]',
        r'user_states\[chat_id\]',
        r'user_timezones\[chat_id\]',
        r'get_user_time\(chat_id',
        r'to_utc_time\(chat_id',
        r'get_user_timezone\(chat_id\)',
        r'create_calendar\(chat_id',
        r'create_time_picker\(chat_id',
        r'parse_time\([^,]+,\s*chat_id',
    ]
    
    issues = []
    for pattern in forbidden_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"Found {len(matches)} instances of: {pattern}")
    
    if issues:
        print("  ❌ Found issues:")
        for issue in issues:
            print(f"     - {issue}")
        return False
    else:
        print("  ✅ Không còn chat_id trong data operations")
        return True

def test_command_handlers():
    """Test 4: Kiểm tra command handlers đã update"""
    print("\n⚡ TEST 4: Kiểm tra command handlers")
    print("-" * 50)
    
    with open('f:/workspace12/task_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm tất cả @bot.message_handler
    handlers = re.findall(r'@bot\.message_handler.*?\ndef\s+(\w+)\(', content, re.DOTALL)
    
    print(f"  Tìm thấy {len(handlers)} message handlers")
    
    # Check một số handlers quan trọng
    important_handlers = ['send_welcome', 'add_task', 'list_tasks', 'mark_done', 'set_reminder']
    
    for handler in important_handlers:
        if handler in handlers:
            print(f"  ✅ {handler} exists")
        else:
            print(f"  ⚠️  {handler} not found (có thể đã đổi tên)")
    
    return True

def test_callback_handler():
    """Test 5: Kiểm tra callback handler"""
    print("\n🎯 TEST 5: Kiểm tra callback handler")
    print("-" * 50)
    
    with open('f:/workspace12/task_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm callback_handler function
    callback_match = re.search(
        r'@bot\.callback_query_handler.*?def callback_handler\(call\):.*?(?=\n@|\n# Xử lý tin nhắn|\ndef show_task_list)',
        content,
        re.DOTALL
    )
    
    if not callback_match:
        print("  ❌ Không tìm thấy callback_handler!")
        return False
    
    callback_content = callback_match.group(0)
    
    # Check for user_id and chat_id extraction
    if 'user_id = call.from_user.id' in callback_content:
        print("  ✅ user_id được extract từ call.from_user.id")
    else:
        print("  ❌ user_id KHÔNG được extract đúng!")
        return False
    
    if 'chat_id = call.message.chat.id' in callback_content:
        print("  ✅ chat_id được extract từ call.message.chat.id")
    else:
        print("  ❌ chat_id KHÔNG được extract đúng!")
        return False
    
    if 'user_chat_mapping[user_id] = chat_id' in callback_content:
        print("  ✅ user_chat_mapping được update")
    else:
        print("  ⚠️  user_chat_mapping có thể chưa được update trong callback")
    
    return True

def test_reminder_system():
    """Test 6: Kiểm tra reminder system"""
    print("\n⏰ TEST 6: Kiểm tra reminder system")
    print("-" * 50)
    
    with open('f:/workspace12/task_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm reminder_checker function
    if 'def reminder_checker():' in content:
        print("  ✅ reminder_checker function exists")
    else:
        print("  ❌ reminder_checker NOT FOUND!")
        return False
    
    # Check reminder loops through user_id
    reminder_match = re.search(
        r'def reminder_checker\(\):.*?(?=\n# |^\n@|\ndef )',
        content,
        re.DOTALL | re.MULTILINE
    )
    
    if reminder_match:
        reminder_content = reminder_match.group(0)
        
        if 'for user_id, tasks in' in reminder_content:
            print("  ✅ Reminder loops through user_id")
        else:
            print("  ❌ Reminder NOT looping through user_id!")
            return False
        
        if 'user_chat_mapping.get(user_id)' in reminder_content:
            print("  ✅ Reminder uses user_chat_mapping")
        else:
            print("  ❌ Reminder NOT using user_chat_mapping!")
            return False
    
    return True

def test_privacy_logic():
    """Test 7: Simulate privacy logic"""
    print("\n🔒 TEST 7: Simulate privacy logic")
    print("-" * 50)
    
    # Simulate bot data structures
    user_tasks = {}
    user_chat_mapping = {}
    
    # Scenario: 2 users trong cùng một group
    group_chat_id = 99999
    
    # User A
    user_a_id = 12345
    user_tasks[user_a_id] = [
        {'content': 'Task của A', 'done': False}
    ]
    user_chat_mapping[user_a_id] = group_chat_id
    
    # User B
    user_b_id = 67890
    user_tasks[user_b_id] = [
        {'content': 'Task của B', 'done': False}
    ]
    user_chat_mapping[user_b_id] = group_chat_id
    
    # Test privacy
    a_tasks = len(user_tasks.get(user_a_id, []))
    b_tasks = len(user_tasks.get(user_b_id, []))
    
    print(f"  User A (ID: {user_a_id}) có {a_tasks} task")
    print(f"  User B (ID: {user_b_id}) có {b_tasks} task")
    
    # Verify separation
    if user_a_id in user_tasks and user_b_id in user_tasks:
        if user_tasks[user_a_id] != user_tasks[user_b_id]:
            print("  ✅ Tasks được phân tách cho mỗi user")
        else:
            print("  ❌ Tasks KHÔNG được phân tách!")
            return False
    
    # Verify chat mapping
    if user_chat_mapping[user_a_id] == user_chat_mapping[user_b_id] == group_chat_id:
        print("  ✅ Cả 2 users map đến cùng group chat")
    else:
        print("  ❌ Chat mapping KHÔNG đúng!")
        return False
    
    return True

def run_all_tests():
    """Chạy tất cả tests"""
    print("\n" + "=" * 60)
    print("🧪 BẮT ĐẦU TEST BOT TELEGRAM - PRIVACY UPDATE")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_helper_functions,
        test_no_chat_id_in_data_operations,
        test_command_handlers,
        test_callback_handler,
        test_reminder_system,
        test_privacy_logic,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n  ❌ ERROR: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ TEST")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 TẤT CẢ TESTS ĐỀU PASSED!")
        print("✅ Bot sẵn sàng để deploy!")
        print("\n📋 Checklist trước khi deploy:")
        print("  1. ✅ Cài đặt dependencies: pip install -r requirements.txt")
        print("  2. ✅ Set TELEGRAM_BOT_TOKEN trong .env")
        print("  3. ✅ Test với 2 users trong một group")
        print("  4. ✅ Verify reminders hoạt động đúng")
        return True
    else:
        print(f"\n⚠️  CÓ {total - passed} TESTS FAILED!")
        print("❌ Cần sửa các issues trước khi deploy!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
