"""
Test case cụ thể: Trả lời đơn giản cho câu hỏi của bot
"""

from ai_task_agent import AITaskAgent
import json

agent = AITaskAgent()

print("="*60)
print("TEST: Conversation với câu trả lời đơn giản")
print("="*60)

# Turn 1: User khởi tạo task
print("\n🔄 Turn 1:")
print("👤 User: Tạo task marketing mới")
result1 = agent.process_message("Tạo task marketing mới")
print(f"🤖 Bot: {result1['ask_message'][:100]}...")
print(f"📊 Missing: {result1['missing_fields']}")

# Turn 2: User trả lời đơn giản tên người
print("\n🔄 Turn 2:")
print("👤 User: Nguyễn Văn A")
result2 = agent.process_message("Nguyễn Văn A", context=result1['task'])
print(f"🤖 Bot: {result2['ask_message'][:100]}...")
print(f"📊 Missing: {result2['missing_fields']}")
print(f"✅ Assignee: {result2['task'].get('assignee', 'NOT SET')}")

# Turn 3: User trả lời đơn giản deadline
print("\n🔄 Turn 3:")
print("👤 User: 25/08/2026")
result3 = agent.process_message("25/08/2026", context=result2['task'])
print(f"🤖 Bot: {result3['ask_message'][:100]}...")
print(f"📊 Action: {result3['action']}")
print(f"✅ Deadline: {result3['task'].get('deadline', 'NOT SET')}")

if result3['action'] == 'save_task':
    print("\n✅ SUCCESS! Task completed:")
    print(json.dumps(result3['task'], indent=2, ensure_ascii=False))
else:
    print("\n❌ FAILED! Still missing fields")

print("\n" + "="*60)
