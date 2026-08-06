"""
AI Task Agent - Quản lý công việc thông minh
Tự động phân tích tin nhắn người dùng và đề xuất thông tin cần bổ sung
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class AITaskAgent:
    """
    AI Agent thông minh để quản lý thông tin công việc
    - Phân tích tin nhắn người dùng
    - Trích xuất thông tin task
    - Kiểm tra tính đầy đủ
    - Đề xuất câu hỏi để bổ sung thông tin
    """
    
    # Các trường bắt buộc
    REQUIRED_FIELDS = ['task_name', 'assignee', 'deadline']
    
    # Các trường tùy chọn với giá trị mặc định
    OPTIONAL_FIELDS = {
        'task_code': None,
        'task_group': 'Chung',
        'progress_percent': 0,
        'status': 'Đang làm',
        'details': ''
    }
    
    # Danh sách trạng thái hợp lệ
    VALID_STATUSES = ['Đang làm', 'Hoàn thành', 'Bị trễ', 'Cần hỗ trợ']
    
    # Keywords để nhận dạng các trường
    FIELD_KEYWORDS = {
        'task_name': ['tên', 'công việc', 'task', 'nhiệm vụ', 'việc'],
        'assignee': ['người làm', 'phụ trách', 'assignee', 'người thực hiện', 'người nhận'],
        'deadline': ['deadline', 'hạn', 'hạn chót', 'đến ngày', 'hoàn thành vào'],
        'task_group': ['nhóm', 'dự án', 'project', 'phòng ban', 'team'],
        'progress_percent': ['tiến độ', 'hoàn thành', '%', 'phần trăm'],
        'status': ['trạng thái', 'status', 'tình trạng'],
        'details': ['chi tiết', 'mô tả', 'nội dung', 'ghi chú']
    }
    
    def __init__(self):
        """Khởi tạo AI Agent"""
        pass
    
    def parse_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Phân tích tin nhắn từ người dùng và trích xuất thông tin task
        
        Args:
            message: Tin nhắn từ người dùng
            context: Thông tin ngữ cảnh từ cuộc hội thoại trước (nếu có)
        
        Returns:
            Dict chứa thông tin đã trích xuất
        """
        extracted = {}
        
        # Merge context nếu có
        if context:
            extracted.update(context)
        
        # Parse tin nhắn theo các pattern phổ biến
        message = message.strip()
        
        # Xác định missing fields từ context để parse thông minh hơn
        missing_fields = []
        if context:
            for field in self.REQUIRED_FIELDS:
                if field not in context or not context[field]:
                    missing_fields.append(field)
        
        # Pattern 1: Key-value format (Tên: xxx, Người làm: yyy)
        parsed_kv = self._parse_key_value_format(message)
        
        # Pattern 2: Natural language
        parsed_nl = self._parse_natural_language(message)
        
        # Pattern 3: Structured format (JSON-like)
        parsed_struct = self._parse_structured_format(message)
        
        # Pattern 4: Smart context-aware parsing for simple answers
        parsed_simple = {}
        # Nếu có missing fields và message ngắn, parse như câu trả lời đơn giản
        if missing_fields and len(message.split()) <= 6:
            # Chỉ parse simple nếu các pattern khác không match được gì quan trọng
            has_explicit_match = (
                any(k in parsed_kv for k in ['task_name', 'assignee', 'deadline']) or
                any(k in parsed_struct for k in ['task_name', 'assignee', 'deadline'])
            )
            if not has_explicit_match:
                parsed_simple = self._parse_simple_answer(message, missing_fields[0])
        
        # Merge results với priority: simple > key-value > structured > natural language
        # Priority cao hơn sẽ override priority thấp hơn
        extracted.update(parsed_nl)
        extracted.update(parsed_struct)
        extracted.update(parsed_kv)
        extracted.update(parsed_simple)  # Highest priority cho simple answer
        
        # Normalize và validate dữ liệu
        extracted = self._normalize_data(extracted)
        
        return extracted
    
    def _parse_key_value_format(self, message: str) -> Dict[str, Any]:
        """Parse format: Key: Value"""
        result = {}
        
        # Các pattern key-value
        patterns = {
            'task_name': r'(?:tên|công việc|task|nhiệm vụ)[\s:：]+([^\n,;]+)',
            'assignee': r'(?:người làm|phụ trách|assignee|người thực hiện)[\s:：]+([^\n,;]+)',
            'deadline': r'(?:deadline|hạn|hạn chót|đến ngày)[\s:：]+([^\n,;]+)',
            'task_group': r'(?:nhóm|dự án|project|team)[\s:：]+([^\n,;]+)',
            'task_code': r'(?:mã|code)[\s:：]+([A-Z0-9\-]+)',
            'progress_percent': r'(?:tiến độ|hoàn thành)[\s:：]+(\d+)\s*%?',
            'status': r'(?:trạng thái|status)[\s:：]+([^\n,;]+)',
            'details': r'(?:chi tiết|mô tả|nội dung)[\s:：]+([^\n]+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field == 'progress_percent':
                    result[field] = int(value)
                else:
                    result[field] = value
        
        return result
    
    def _parse_natural_language(self, message: str) -> Dict[str, Any]:
        """Parse natural language format"""
        result = {}
        
        # Pattern: "X là Y" hoặc "X: Y" - extract specific field updates
        field_update_patterns = {
            'task_name': r'(?:tên|công việc)\s+(?:là|:|：)\s*["\']?([^"\'\n]+)["\']?',
            'assignee': r'(?:người làm|phụ trách|người thực hiện)\s+(?:là|:|：)\s*["\']?([^"\'\n]+)["\']?',
            'deadline': r'(?:deadline|hạn|hạn chót)\s+(?:là|:|：)?\s*([^\n]+)',
            'task_group': r'(?:nhóm|dự án|team)\s+(?:là|:|：)\s*([^"\'\n]+)',
        }
        
        for field, pattern in field_update_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                result[field] = value
        
        # Detect mentions (người phụ trách)
        # Pattern: "nhờ @user" hoặc "giao cho Nguyễn Văn A"
        if 'assignee' not in result:
            assignee_patterns = [
                r'(?:nhờ|giao cho|gửi cho|assign to)\s+(@?\w+(?:\s+\w+)*)',
                r'@(\w+(?:\s+\w+)*)',
            ]
            for pattern in assignee_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    result['assignee'] = match.group(1).strip()
                    break
        
        # Detect date patterns
        if 'deadline' not in result:
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                r'(\d{1,2}/\d{1,2}/\d{4})',  # DD/MM/YYYY
                r'ngày\s+(\d{1,2}/\d{1,2})',  # ngày DD/MM
                r'(\d{1,2}/\d{1,2})',  # DD/MM
            ]
            for pattern in date_patterns:
                match = re.search(pattern, message)
                if match:
                    result['deadline'] = match.group(1).strip()
                    break
        
        return result
    
    def _parse_structured_format(self, message: str) -> Dict[str, Any]:
        """Parse JSON hoặc structured format"""
        result = {}
        
        # Try to parse as JSON
        try:
            data = json.loads(message)
            if isinstance(data, dict):
                result.update(data)
        except:
            pass
        
        return result
    
    def _parse_simple_answer(self, message: str, field: str) -> Dict[str, Any]:
        """
        Parse câu trả lời đơn giản cho một field cụ thể
        Dùng khi user trả lời trực tiếp câu hỏi của bot
        
        Args:
            message: Câu trả lời của user
            field: Field đang được hỏi ('task_name', 'assignee', 'deadline')
        
        Returns:
            Dict với field đã được điền
        """
        result = {}
        message = message.strip()
        
        # Bỏ qua nếu message quá dài (có thể là mô tả phức tạp)
        if len(message.split()) > 15:
            return result
        
        if field == 'task_name':
            # Coi toàn bộ message là task name
            result['task_name'] = message
        
        elif field == 'assignee':
            # Loại bỏ các từ thừa như "là", "tên", "người làm"
            assignee = re.sub(r'^(là|tên|người làm|người thực hiện|phụ trách)\s+', '', message, flags=re.IGNORECASE)
            assignee = assignee.strip().lstrip('@')
            result['assignee'] = assignee
        
        elif field == 'deadline':
            # Parse date
            deadline = self._normalize_date(message)
            if deadline:
                result['deadline'] = deadline
        
        elif field == 'task_group':
            # Loại bỏ từ thừa
            group = re.sub(r'^(nhóm|dự án|team|project)\s+', '', message, flags=re.IGNORECASE)
            result['task_group'] = group.strip()
        
        return result
    
    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize và validate dữ liệu"""
        normalized = {}
        
        # Task name
        if 'task_name' in data:
            normalized['task_name'] = str(data['task_name']).strip()
        
        # Assignee
        if 'assignee' in data:
            assignee = str(data['assignee']).strip()
            # Remove @ if present
            assignee = assignee.lstrip('@')
            normalized['assignee'] = assignee
        
        # Deadline - normalize to YYYY-MM-DD
        if 'deadline' in data:
            deadline = self._normalize_date(data['deadline'])
            if deadline:
                normalized['deadline'] = deadline
        
        # Task code - auto generate if needed
        if 'task_code' in data:
            normalized['task_code'] = str(data['task_code']).upper()
        
        # Task group
        if 'task_group' in data:
            normalized['task_group'] = str(data['task_group']).strip()
        
        # Progress percent
        if 'progress_percent' in data:
            try:
                progress = int(data['progress_percent'])
                normalized['progress_percent'] = max(0, min(100, progress))
            except:
                normalized['progress_percent'] = 0
        
        # Status
        if 'status' in data:
            status = str(data['status']).strip()
            # Try to match with valid statuses
            for valid_status in self.VALID_STATUSES:
                if status.lower() in valid_status.lower() or valid_status.lower() in status.lower():
                    normalized['status'] = valid_status
                    break
            if 'status' not in normalized:
                normalized['status'] = status
        
        # Details
        if 'details' in data:
            normalized['details'] = str(data['details']).strip()
        
        return normalized
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to YYYY-MM-DD format"""
        date_str = str(date_str).strip()
        
        # Already in YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # DD/MM/YYYY
        match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # DD/MM (assume current year)
        match = re.match(r'^(\d{1,2})/(\d{1,2})$', date_str)
        if match:
            day, month = match.groups()
            year = datetime.now().year
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Try to parse with datetime
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except:
            pass
        
        return None
    
    def check_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kiểm tra tính đầy đủ của dữ liệu và quyết định action
        
        Returns:
            Dict chứa:
            - action: 'save_task' hoặc 'ask_more_info'
            - missing_fields: List các trường còn thiếu
            - task: Dữ liệu task đầy đủ
            - ask_message: Câu hỏi để hỏi người dùng (nếu thiếu thông tin)
        """
        missing_fields = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        # Build complete task data
        task = {}
        
        # Add existing data
        task.update(data)
        
        # Add optional fields with defaults if not present
        for field, default_value in self.OPTIONAL_FIELDS.items():
            if field not in task or task[field] is None:
                task[field] = default_value
        
        # Auto-generate task_code if needed
        if not task.get('task_code') and task.get('task_name'):
            task['task_code'] = self._generate_task_code(task['task_name'], task.get('task_group'))
        
        # Decide action
        if missing_fields:
            action = 'ask_more_info'
            ask_message = self._generate_question(missing_fields, task)
        else:
            action = 'save_task'
            ask_message = self._generate_confirmation(task)
        
        return {
            'action': action,
            'missing_fields': missing_fields,
            'task': task,
            'ask_message': ask_message
        }
    
    def _generate_task_code(self, task_name: str, task_group: Optional[str] = None) -> str:
        """Tự động tạo mã công việc"""
        # Use group prefix if available
        prefix = 'TASK'
        if task_group:
            # Take first 3 letters of group name
            group_abbr = ''.join([c for c in task_group if c.isalpha()])[:3].upper()
            if group_abbr:
                prefix = group_abbr
        
        # Generate random suffix
        import random
        suffix = random.randint(100, 999)
        
        return f"{prefix}-{suffix}"
    
    def _generate_question(self, missing_fields: List[str], current_data: Dict) -> str:
        """Tạo câu hỏi thân thiện để hỏi thêm thông tin"""
        field_names = {
            'task_name': 'tên công việc',
            'assignee': 'người phụ trách',
            'deadline': 'hạn chót (deadline)',
            'task_group': 'nhóm/dự án',
            'progress_percent': 'tiến độ (%)',
            'status': 'trạng thái',
            'details': 'chi tiết công việc'
        }
        
        # Prioritize missing fields
        if 'task_name' in missing_fields:
            return "📝 Bạn muốn tạo công việc gì? Vui lòng cho tôi biết tên công việc nhé!"
        
        if 'assignee' in missing_fields:
            task_info = f" cho công việc '{current_data.get('task_name', '')}'" if current_data.get('task_name') else ""
            return f"👤 Ai sẽ là người phụ trách{task_info}?"
        
        if 'deadline' in missing_fields:
            return "📅 Hạn chót (deadline) của công việc này là khi nào?\n(Ví dụ: 2026-08-15 hoặc 15/08/2026)"
        
        # Multiple fields missing
        missing_names = [field_names.get(f, f) for f in missing_fields[:2]]
        return f"ℹ️ Tôi cần thêm thông tin về: {', '.join(missing_names)}.\nBạn có thể cung cấp giúp tôi được không?"
    
    def _generate_confirmation(self, task: Dict) -> str:
        """Tạo tin nhắn xác nhận khi đủ thông tin"""
        msg = "✅ Tuyệt vời! Tôi đã ghi nhận đầy đủ thông tin:\n\n"
        msg += f"📋 Mã: {task['task_code']}\n"
        msg += f"🏷️ Tên: {task['task_name']}\n"
        msg += f"👤 Người làm: {task['assignee']}\n"
        msg += f"📅 Deadline: {task['deadline']}\n"
        msg += f"📊 Nhóm: {task['task_group']}\n"
        msg += f"⚡ Trạng thái: {task['status']}\n"
        msg += f"📈 Tiến độ: {task['progress_percent']}%\n"
        
        if task.get('details'):
            msg += f"\n📝 Chi tiết: {task['details']}\n"
        
        msg += "\n💪 Chúc bạn làm việc hiệu quả!"
        
        return msg
    
    def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Xử lý tin nhắn từ người dùng - Main entry point
        
        Args:
            message: Tin nhắn từ người dùng
            context: Context từ hội thoại trước (nếu đang trong conversation)
        
        Returns:
            Dict với format:
            {
                'action': 'save_task' | 'ask_more_info',
                'missing_fields': [...],
                'task': {...},
                'ask_message': '...'
            }
        """
        # Step 1: Parse message
        extracted_data = self.parse_message(message, context)
        
        # Step 2: Check completeness
        result = self.check_completeness(extracted_data)
        
        return result


# ============= TESTING / DEMO =============

def test_agent():
    """Test AI Task Agent"""
    agent = AITaskAgent()
    
    print("=" * 60)
    print("AI TASK AGENT - TESTING")
    print("=" * 60)
    
    # Test case 1: Đầy đủ thông tin
    print("\n📝 TEST 1: Tin nhắn đầy đủ thông tin")
    print("-" * 60)
    message1 = """
    Tên: Thiết kế landing page mới
    Người làm: Nguyễn Văn A
    Deadline: 2026-08-15
    Nhóm: Marketing
    Trạng thái: Đang làm
    Chi tiết: Thiết kế landing page cho campaign mùa hè
    """
    result1 = agent.process_message(message1)
    print(f"Input: {message1.strip()}")
    print(f"\nAction: {result1['action']}")
    print(f"Missing: {result1['missing_fields']}")
    print(f"\n{result1['ask_message']}")
    print(f"\nTask Data:\n{json.dumps(result1['task'], indent=2, ensure_ascii=False)}")
    
    # Test case 2: Thiếu thông tin
    print("\n" + "=" * 60)
    print("📝 TEST 2: Tin nhắn thiếu thông tin")
    print("-" * 60)
    message2 = "Tạo chiến dịch marketing mới cho Nguyễn Văn B"
    result2 = agent.process_message(message2)
    print(f"Input: {message2}")
    print(f"\nAction: {result2['action']}")
    print(f"Missing: {result2['missing_fields']}")
    print(f"\n{result2['ask_message']}")
    print(f"\nTask Data:\n{json.dumps(result2['task'], indent=2, ensure_ascii=False)}")
    
    # Test case 3: Conversation flow - bổ sung từng phần
    print("\n" + "=" * 60)
    print("📝 TEST 3: Conversation flow (bổ sung dần)")
    print("-" * 60)
    
    # Turn 1
    print("\n🗣️ User: Tạo task mới cho dự án Tech")
    result3_1 = agent.process_message("Tạo task mới cho dự án Tech")
    print(f"🤖 Bot: {result3_1['ask_message']}")
    print(f"   Missing: {result3_1['missing_fields']}")
    
    # Turn 2
    print("\n🗣️ User: Tên là 'Phát triển API v2'")
    result3_2 = agent.process_message("Tên là 'Phát triển API v2'", context=result3_1['task'])
    print(f"🤖 Bot: {result3_2['ask_message']}")
    print(f"   Missing: {result3_2['missing_fields']}")
    
    # Turn 3
    print("\n🗣️ User: Người làm là Trần Văn C")
    result3_3 = agent.process_message("Người làm là Trần Văn C", context=result3_2['task'])
    print(f"🤖 Bot: {result3_3['ask_message']}")
    print(f"   Missing: {result3_3['missing_fields']}")
    
    # Turn 4
    print("\n🗣️ User: Deadline 20/08/2026")
    result3_4 = agent.process_message("Deadline 20/08/2026", context=result3_3['task'])
    print(f"🤖 Bot: {result3_4['ask_message']}")
    print(f"   Action: {result3_4['action']}")
    print(f"\nFinal Task Data:\n{json.dumps(result3_4['task'], indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    test_agent()
