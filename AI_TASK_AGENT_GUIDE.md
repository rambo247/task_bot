# 🤖 AI Task Agent - Hướng Dẫn Sử Dụng

## 📋 Tổng Quan

AI Task Agent là một tính năng thông minh được tích hợp vào Telegram Bot để giúp bạn quản lý công việc một cách chi tiết và chuyên nghiệp. Agent sẽ tự động phân tích tin nhắn của bạn và hỏi bổ sung thông tin cần thiết.

## ✨ Tính Năng Chính

### 1. Phân Tích Thông Minh
- Tự động trích xuất thông tin từ tin nhắn tự nhiên
- Hỗ trợ nhiều định dạng input (key-value, natural language, JSON)
- Nhận dạng thông tin: tên task, người phụ trách, deadline, nhóm dự án, v.v.

### 2. Hỏi Đáp Thông Minh
- Kiểm tra tính đầy đủ của thông tin
- Hỏi bổ sung các trường quan trọng còn thiếu
- Hướng dẫn người dùng từng bước

### 3. Quản Lý Chi Tiết
- **task_code**: Mã công việc (tự động tạo hoặc tùy chỉnh)
- **task_name**: Tên công việc
- **assignee**: Người phụ trách
- **deadline**: Hạn chót (YYYY-MM-DD)
- **task_group**: Nhóm/Dự án
- **status**: Trạng thái (Đang làm, Hoàn thành, Bị trễ, Cần hỗ trợ)
- **progress_percent**: Tiến độ (0-100%)
- **details**: Chi tiết công việc

## 🚀 Cách Sử Dụng

### Cách 1: Sử Dụng Command `/smart_add` hoặc `/ai_add`

```
/smart_add Thiết kế landing page cho Nguyễn Văn A, deadline 15/08/2026
```

Bot sẽ phân tích và hỏi thêm thông tin nếu cần.

### Cách 2: Qua Menu Bot

1. Gửi `/start` để mở menu chính
2. Chọn **📋 Quản Lý Task**
3. Chọn **🤖 AI Smart Add**
4. Nhập thông tin công việc

### Cách 3: Conversation Flow (Bổ Sung Dần)

```
User: /smart_add
Bot: 🤖 Hãy cho tôi biết công việc của bạn!

User: Tạo chiến dịch marketing mới
Bot: 👤 Ai sẽ là người phụ trách?

User: Nguyễn Văn B
Bot: 📅 Hạn chót của công việc này là khi nào?

User: 20/08/2026
Bot: ✅ Tuyệt vời! Tôi đã ghi nhận đầy đủ thông tin...
```

## 📝 Các Format Input Được Hỗ Trợ

### Format 1: Key-Value (Structured)

```
Tên: Thiết kế landing page mới
Người làm: Nguyễn Văn A
Deadline: 2026-08-15
Nhóm: Marketing
Trạng thái: Đang làm
Chi tiết: Thiết kế landing page cho campaign mùa hè
```

### Format 2: Natural Language

```
Tạo task thiết kế landing page cho Nguyễn Văn A, deadline 15/08/2026, nhóm Marketing
```

### Format 3: Partial Information (Bot sẽ hỏi thêm)

```
Thiết kế landing page mới
```

Bot sẽ hỏi:
- Người phụ trách là ai?
- Deadline khi nào?
- Thuộc nhóm/dự án nào?

## 🎯 Ví Dụ Thực Tế

### Ví Dụ 1: Đầy Đủ Thông Tin

**Input:**
```
/smart_add Tên: Phát triển API v2
Người làm: Trần Văn C
Deadline: 2026-08-20
Nhóm: Tech
Trạng thái: Đang làm
Tiến độ: 30%
Chi tiết: Phát triển REST API với authentication
```

**Output:**
```
✅ Tuyệt vời! Tôi đã ghi nhận đầy đủ thông tin:

📋 Mã: TEC-443
🏷️ Tên: Phát triển API v2
👤 Người làm: Trần Văn C
📅 Deadline: 2026-08-20
📊 Nhóm: Tech
⚡ Trạng thái: Đang làm
📈 Tiến độ: 30%

📝 Chi tiết: Phát triển REST API với authentication

💪 Chúc bạn làm việc hiệu quả!
```

### Ví Dụ 2: Thiếu Thông Tin

**Turn 1:**
```
User: /smart_add Tạo chiến dịch marketing
Bot: 👤 Ai sẽ là người phụ trách cho công việc 'Tạo chiến dịch marketing'?
```

**Turn 2:**
```
User: Người làm là Lê Thị D
Bot: 📅 Hạn chót (deadline) của công việc này là khi nào?
      (Ví dụ: 2026-08-15 hoặc 15/08/2026)
```

**Turn 3:**
```
User: 25/08/2026
Bot: ✅ Tuyệt vời! Tôi đã ghi nhận đầy đủ thông tin...
```

### Ví Dụ 3: Format Tự Nhiên

**Input:**
```
/smart_add Họp team planning cho dự án Website với Nguyễn Văn E, deadline 10/08
```

Bot tự động trích xuất:
- Task name: "Họp team planning cho dự án Website"
- Assignee: "Nguyễn Văn E"
- Deadline: "2026-08-10"
- Task group: "Website"

## 🔧 Cấu Trúc Kỹ Thuật

### Module `ai_task_agent.py`

```python
from ai_task_agent import AITaskAgent

agent = AITaskAgent()
result = agent.process_message("Tạo task mới...")

if result['action'] == 'save_task':
    # Đủ thông tin - lưu task
    save_task(result['task'])
else:
    # Thiếu thông tin - hỏi thêm
    ask_user(result['ask_message'])
```

### JSON Response Format

```json
{
  "action": "save_task",
  "missing_fields": [],
  "task": {
    "task_code": "MAR-732",
    "task_group": "Marketing",
    "task_name": "Thiết kế landing page mới",
    "assignee": "Nguyễn Văn A",
    "deadline": "2026-08-15",
    "progress_percent": 0,
    "status": "Đang làm",
    "details": "Thiết kế landing page cho campaign mùa hè"
  },
  "ask_message": "✅ Tuyệt vời! Tôi đã ghi nhận..."
}
```

### JSON Response khi thiếu thông tin

```json
{
  "action": "ask_more_info",
  "missing_fields": ["deadline"],
  "task": {
    "task_code": "MAR-892",
    "task_group": "Marketing",
    "task_name": "Tạo chiến dịch marketing",
    "assignee": "Nguyễn Văn B",
    "deadline": null,
    "progress_percent": 0,
    "status": "Đang làm",
    "details": ""
  },
  "ask_message": "📅 Hạn chót (deadline) của công việc này là khi nào?"
}
```

## 🧪 Testing

Chạy test để kiểm tra AI Agent:

```bash
python ai_task_agent.py
```

Kết quả test sẽ hiển thị 3 test cases:
1. Tin nhắn đầy đủ thông tin
2. Tin nhắn thiếu thông tin
3. Conversation flow (bổ sung dần)

## 📊 Lợi Ích

### So với `/add` thông thường:

| Tính năng | `/add` | `/smart_add` |
|-----------|--------|--------------|
| Format đầu vào | Tự do | Structured + Natural Language |
| Thông tin chi tiết | Ít | Nhiều (8 trường) |
| Tự động hỏi thêm | ❌ | ✅ |
| Tạo mã task | ❌ | ✅ |
| Theo dõi tiến độ | ❌ | ✅ |
| Phân nhóm dự án | ❌ | ✅ |
| Quản lý trạng thái | ❌ | ✅ |

## 🛠️ Tùy Chỉnh

### Thêm Trường Mới

Edit `ai_task_agent.py`:

```python
OPTIONAL_FIELDS = {
    'task_code': None,
    'task_group': 'Chung',
    'progress_percent': 0,
    'status': 'Đang làm',
    'details': '',
    'priority': 'Medium',  # ← Thêm trường mới
}
```

### Thêm Keywords

```python
FIELD_KEYWORDS = {
    'priority': ['ưu tiên', 'priority', 'độ quan trọng'],  # ← Thêm keywords
    ...
}
```

### Thêm Pattern Parsing

```python
def _parse_key_value_format(self, message: str) -> Dict[str, Any]:
    patterns = {
        'priority': r'(?:ưu tiên|priority)[\s:：]+([^\n,;]+)',  # ← Thêm pattern
        ...
    }
```

## 🔐 Bảo Mật & Privacy

- Mỗi user có dữ liệu riêng biệt
- Conversation context tự động xóa sau khi hoàn thành
- Không lưu trữ thông tin nhạy cảm

## 🐛 Troubleshooting

### Lỗi: Import Error

```bash
ModuleNotFoundError: No module named 'ai_task_agent'
```

**Giải pháp:** Đảm bảo file `ai_task_agent.py` nằm cùng thư mục với `task_bot.py`

### Lỗi: Bot không hỏi thêm thông tin

**Nguyên nhân:** Message đã chứa đủ thông tin cần thiết

**Giải pháp:** Kiểm tra lại format input, đảm bảo thiếu ít nhất 1 trong 3 trường: task_name, assignee, deadline

### Lỗi: Date format không đúng

**Format hỗ trợ:**
- `YYYY-MM-DD` (2026-08-15)
- `DD/MM/YYYY` (15/08/2026)
- `DD/MM` (15/08 - sẽ dùng năm hiện tại)

## 📚 Tài Liệu Tham Khảo

- `ai_task_agent.py` - Module AI Agent
- `task_bot.py` - Telegram Bot chính
- `AI_AUTO_RESPONSE_GUIDE.md` - Hướng dẫn AI tự động trả lời

## 🤝 Đóng Góp

Nếu bạn muốn cải thiện AI Agent:

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/ai-agent-improvement`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push: `git push origin feature/ai-agent-improvement`
5. Tạo Pull Request

## 📞 Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
- Tạo issue trên GitHub
- Liên hệ qua Telegram
- Đọc documentation chi tiết

---

**Phiên bản:** 1.0.0  
**Ngày cập nhật:** 2026-08-06  
**Tác giả:** AI Development Team  

💪 Chúc bạn làm việc hiệu quả với AI Task Agent!
