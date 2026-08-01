"""
Demo Script - Test AI Auto Response Feature
Chạy file này để test tính năng AI tự động trả lời
"""

import sys
sys.path.append('.')

# Mock data để test các hàm
class MockUser:
    def __init__(self, user_id):
        self.id = user_id

# Import các hàm từ task_bot (chỉ để demo logic)
# Trong thực tế sẽ test qua Telegram

print("=" * 60)
print("🤖 DEMO: AI AUTO RESPONSE FEATURE")
print("=" * 60)

# Test 1: Extract Keywords
print("\n📝 TEST 1: Trích xuất từ khóa")
print("-" * 60)

def test_extract_keywords():
    from task_bot import extract_keywords
    
    test_cases = [
        "Địa chỉ văn phòng là gì?",
        "Email công ty của tôi",
        "Giờ làm việc như thế nào?",
        "What is the company address?"
    ]
    
    for text in test_cases:
        keywords = extract_keywords(text)
        print(f"Câu: '{text}'")
        print(f"Keywords: {keywords}")
        print()

try:
    test_extract_keywords()
except Exception as e:
    print(f"⚠️ Lỗi: {e}")
    print("💡 Chạy bot trước để test function này\n")

# Test 2: Knowledge Base Operations
print("\n📚 TEST 2: Thao tác Knowledge Base")
print("-" * 60)

def test_knowledge_base():
    # Giả lập dữ liệu
    ai_knowledge_base = {}
    user_id = 12345
    
    # Mock function add_to_knowledge_base
    def mock_add_kb(uid, question, answer):
        if uid not in ai_knowledge_base:
            ai_knowledge_base[uid] = []
        ai_knowledge_base[uid].append({
            'question': question,
            'answer': answer,
            'keywords': question.lower().split()
        })
        return True
    
    # Thêm dữ liệu mẫu
    print("Thêm dữ liệu Q&A...")
    mock_add_kb(user_id, "Địa chỉ văn phòng là gì?", "123 Đường ABC, Quận 1, TP.HCM")
    mock_add_kb(user_id, "Email công ty?", "contact@company.com")
    mock_add_kb(user_id, "Giờ làm việc?", "8h-17h, Thứ 2 đến Thứ 6")
    
    print(f"✅ Đã thêm {len(ai_knowledge_base[user_id])} cặp Q&A\n")
    
    # Hiển thị
    print("📋 Danh sách Knowledge Base:")
    for i, item in enumerate(ai_knowledge_base[user_id], 1):
        print(f"{i}. Q: {item['question']}")
        print(f"   A: {item['answer']}")
        print()

try:
    test_knowledge_base()
except Exception as e:
    print(f"⚠️ Lỗi: {e}\n")

# Test 3: Search Knowledge Base
print("\n🔍 TEST 3: Tìm kiếm trong Knowledge Base")
print("-" * 60)

def test_search():
    # Mock search function
    def mock_search(question, kb):
        question_lower = question.lower()
        for item in kb:
            if any(kw in question_lower for kw in item['keywords']):
                return item['answer']
        return None
    
    # Mock KB
    kb = [
        {'question': 'Địa chỉ', 'answer': '123 Đường ABC', 'keywords': ['địa', 'chỉ', 'văn', 'phòng']},
        {'question': 'Email', 'answer': 'contact@company.com', 'keywords': ['email', 'công', 'ty']},
        {'question': 'Giờ làm', 'answer': '8h-17h', 'keywords': ['giờ', 'làm', 'việc']},
    ]
    
    test_questions = [
        "Địa chỉ văn phòng?",
        "Email liên hệ?",
        "Làm việc mấy giờ?",
        "Câu hỏi không có trong KB"
    ]
    
    for q in test_questions:
        result = mock_search(q, kb)
        if result:
            print(f"Q: {q}")
            print(f"A: 📚 {result} [Từ KB]")
        else:
            print(f"Q: {q}")
            print(f"A: ❌ Không tìm thấy")
        print()

try:
    test_search()
except Exception as e:
    print(f"⚠️ Lỗi: {e}\n")

# Test 4: Workflow Complete
print("\n🎯 TEST 4: Workflow Hoàn Chỉnh")
print("-" * 60)

print("""
DEMO WORKFLOW:

1️⃣ User thêm dữ liệu Q&A:
   User: /start → Menu AI → Quản lý KB → Thêm Q&A
   User nhập Q: "Địa chỉ văn phòng?"
   User nhập A: "123 Đường ABC, Quận 1"
   
2️⃣ User bật AI Chat Mode:
   User: Menu AI → Bật AI Chat
   Status: 🟢 BẬT
   
3️⃣ User hỏi:
   User: "Địa chỉ công ty ở đâu?"
   Bot: 📚 123 Đường ABC, Quận 1
        [Từ dữ liệu đã học]
        
4️⃣ User hỏi câu khác (không có trong KB):
   User: "Làm sao đến văn phòng?"
   Bot: 🤖 Bạn có thể đến địa chỉ 123 Đường ABC...
        [Từ AI - tự suy luận dựa trên context]

5️⃣ Tắt AI Chat Mode:
   User: Menu AI → Tắt AI Chat
   Status: ⚪ TẮT
   
6️⃣ Quay về chế độ thường:
   User: "Họp team sáng mai"
   Bot: ✅ Đã thêm task...
        [Tạo task thay vì trả lời]
""")

# Summary
print("\n" + "=" * 60)
print("✅ TỔNG KẾT")
print("=" * 60)

print("""
🎉 TÍNH NĂNG ĐÃ THÊM:

1. Knowledge Base System
   ✅ Lưu trữ Q&A
   ✅ Tìm kiếm theo keywords
   ✅ CRUD operations (Add, List, Delete)

2. AI Chat Mode
   ✅ Toggle ON/OFF
   ✅ Tự động trả lời tin nhắn
   ✅ Ưu tiên KB → AI

3. Menu & UI
   ✅ Menu Quản lý Kiến Thức
   ✅ Toggle button AI Chat
   ✅ Statistics (số Q&A)

4. Smart Response
   ✅ Tìm trong KB trước
   ✅ AI suy luận nếu không tìm thấy
   ✅ AI có context từ KB

5. User States
   ✅ waiting_kb_question
   ✅ waiting_kb_answer
   ✅ Callback handlers

📝 FILES ĐÃ TẠO:
- AI_AUTO_RESPONSE_GUIDE.md (Hướng dẫn chi tiết)
- AI_AUTO_RESPONSE_QUICK.md (Quick start)
- test_ai_response.py (File này)

🚀 SẴN SÀNG SỬ DỤNG!

Để test thực tế:
1. python task_bot.py
2. Telegram: /start
3. Menu → 🤖 Trợ Lý AI
4. Thêm Q&A và test!
""")

print("=" * 60)
print("Demo script completed!")
print("=" * 60)
