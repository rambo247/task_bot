import telebot
import os
import threading
import time
import calendar
import requests
import json
import re
import csv
import io
import uuid
from datetime import datetime, timedelta
from telebot import types
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# ============= AI TASK AGENT CLASS (Embedded) =============

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

# ============= END AI TASK AGENT CLASS =============

# Enterprise features imports
try:
    from bs4 import BeautifulSoup
    import validators
    ENTERPRISE_ENABLED = True
except ImportError:
    ENTERPRISE_ENABLED = False
    print("⚠️ Enterprise features disabled. Install: pip install beautifulsoup4 validators")

# Load environment variables from .env file
load_dotenv()

# Lấy token từ biến môi trường hoặc sử dụng token mặc định
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8802370170:AAEGZU_Df5OnDQTO7kn9lyf2UzeIbbh2KPk')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # GitHub token cho AI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # OpenAI API key cho Whisper (Speech-to-Text)
bot = telebot.TeleBot(TOKEN)

# Lưu trữ danh sách task theo User ID (riêng tư cho mỗi user)
user_tasks = {}

# Lưu trữ timezone offset của mỗi user (theo giờ, mặc định GMT+7 cho Việt Nam)
user_timezones = {}

# Lưu trữ trạng thái người dùng (đang thêm task, đặt reminder, etc.)
user_states = {}

# Track cancelled scraping operations
scraping_cancelled = {}

# Lưu trữ mapping user_id -> chat_id để gửi reminder
user_chat_mapping = {}

# Các timezone phổ biến
TIMEZONES = {
    'VN': 7,    # Việt Nam (GMT+7)
    'TH': 7,    # Thái Lan
    'SG': 8,    # Singapore
    'JP': 9,    # Nhật Bản
    'KR': 9,    # Hàn Quốc
    'CN': 8,    # Trung Quốc
    'UTC': 0,   # UTC
    'GMT': 0,   # GMT
}

# ============= AI KNOWLEDGE BASE =============
# Lưu trữ dữ liệu Q&A cho AI tự động trả lời
ai_knowledge_base = {}
# Format: ai_knowledge_base[user_id] = [
#     {'question': 'câu hỏi', 'answer': 'câu trả lời', 'keywords': ['từ', 'khóa']},
#     ...
# ]

# Lưu trữ chế độ AI chat cho từng user
user_ai_chat_mode = {}  # user_id -> True/False

# ============= ENTERPRISE FEATURES =============
# Multi-tenant Organizations
organizations = {}
# Format: organizations[org_id] = {
#     'id': 'org_xxx',
#     'name': 'Company Name',
#     'owner_user_id': 12345,
#     'members': [12345, 67890],
#     'created_at': 'ISO timestamp',
#     'settings': {
#         'private': True,
#         'auto_import': True,
#         'web_scraping': True
#     }
# }

user_organizations = {}  # user_id -> ['org_id_1', 'org_id_2', ...]
user_active_org = {}  # user_id -> 'org_id' (org hiện tại đang dùng)

# Departments (phòng ban)
departments = {}
# Format: departments[org_id] = [
#     {
#         'id': 'dept_xxx',
#         'name': 'Phòng Kỹ Thuật',
#         'manager': 'Nguyễn Văn A',
#         'manager_contact': 'contact_id',
#         'description': 'Phát triển sản phẩm',
#         'email': 'tech@company.com',
#         'phone': '1234',
#         'members': ['contact_id_1', 'contact_id_2']
#     },
#     ...
# ]

# Contacts/Employees (nhân viên)
contacts = {}
# Format: contacts[org_id] = [
#     {
#         'id': 'contact_xxx',
#         'name': 'Nguyễn Văn A',
#         'position': 'Trưởng phòng IT',
#         'department': 'dept_xxx',
#         'email': 'a.nguyen@company.com',
#         'phone': '0901234567',
#         'extension': '101',
#         'skills': ['Python', 'AI', 'DevOps'],
#         'notes': 'Expert in AI'
#     },
#     ...
# ]

# Web sources (nguồn web để scrape)
web_sources = {}
# Format: web_sources[org_id] = [
#     {
#         'id': 'source_xxx',
#         'url': 'https://company.com/about',
#         'type': 'company_info',
#         'last_scraped': 'ISO timestamp',
#         'status': 'success|failed',
#         'items_count': 50
#     },
#     ...
# ]

# Proactive AI suggestions
proactive_suggestions = {}  # user_id -> [{'type': 'missing_data', 'message': '...', 'actions': [...]}]

# ============= AI TASK AGENT =============
# Initialize AI Task Agent
ai_task_agent = AITaskAgent()

# Lưu conversation context cho AI Agent
# user_id -> {'task': {...}, 'state': 'collecting', 'last_update': timestamp}
ai_conversation_context = {}

# ============= JSON PERSISTENCE =============
import os
import shutil
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent / 'data'
BACKUP_DIR = Path(__file__).parent / 'backups'

# Create directories if not exist
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# Data file paths
DATA_FILES = {
    'user_tasks': DATA_DIR / 'user_tasks.json',
    'user_timezones': DATA_DIR / 'user_timezones.json',
    'user_states': DATA_DIR / 'user_states.json',
    'user_chat_mapping': DATA_DIR / 'user_chat_mapping.json',
    'ai_knowledge_base': DATA_DIR / 'ai_knowledge_base.json',
    'user_ai_chat_mode': DATA_DIR / 'user_ai_chat_mode.json',
    'organizations': DATA_DIR / 'organizations.json',
    'user_organizations': DATA_DIR / 'user_organizations.json',
    'user_active_org': DATA_DIR / 'user_active_org.json',
    'departments': DATA_DIR / 'departments.json',
    'contacts': DATA_DIR / 'contacts.json',
    'web_sources': DATA_DIR / 'web_sources.json',
    'proactive_suggestions': DATA_DIR / 'proactive_suggestions.json',
}

def save_data():
    """Save all data to JSON files"""
    try:
        data_to_save = {
            'user_tasks': user_tasks,
            'user_timezones': user_timezones,
            'user_states': user_states,
            'user_chat_mapping': user_chat_mapping,
            'ai_knowledge_base': ai_knowledge_base,
            'user_ai_chat_mode': user_ai_chat_mode,
            'organizations': organizations,
            'user_organizations': user_organizations,
            'user_active_org': user_active_org,
            'departments': departments,
            'contacts': contacts,
            'web_sources': web_sources,
            'proactive_suggestions': proactive_suggestions,
        }
        
        for key, filepath in DATA_FILES.items():
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save[key], f, ensure_ascii=False, indent=2, default=str)
            except Exception as e:
                print(f"⚠️ Error saving {key}: {e}")
        
        # print("✅ Data saved successfully")
    except Exception as e:
        print(f"❌ Error saving data: {e}")

def load_data():
    """Load all data from JSON files"""
    global user_tasks, user_timezones, user_states, user_chat_mapping
    global ai_knowledge_base, user_ai_chat_mode
    global organizations, user_organizations, user_active_org
    global departments, contacts, web_sources, proactive_suggestions
    
    try:
        loaded_count = 0
        for key, filepath in DATA_FILES.items():
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Convert string keys back to int for user_id keys
                        if key in ['user_tasks', 'user_timezones', 'user_states', 'user_chat_mapping', 
                                   'ai_knowledge_base', 'user_ai_chat_mode', 'user_organizations', 
                                   'user_active_org', 'proactive_suggestions']:
                            data = {int(k) if k.isdigit() else k: v for k, v in data.items()}
                        
                        # Assign to global variables
                        if key == 'user_tasks':
                            # Parse datetime strings in remind_time & migrate progress fields
                            for user_id, tasks in data.items():
                                for task in tasks:
                                    # Migrate remind_time
                                    if task.get('remind_time') and isinstance(task['remind_time'], str):
                                        try:
                                            task['remind_time'] = datetime.strptime(task['remind_time'], "%Y-%m-%d %H:%M:%S")
                                        except:
                                            task['remind_time'] = None
                                    
                                    # Migrate progress_percent field (add if missing)
                                    if 'progress_percent' not in task:
                                        task['progress_percent'] = 0
                                    
                                    # Migrate progress_updates field (add if missing)
                                    if 'progress_updates' not in task:
                                        task['progress_updates'] = []
                            user_tasks = data
                            print(f"   🔄 Migrated {sum(len(tasks) for tasks in data.values())} tasks with progress fields")
                        elif key == 'user_timezones':
                            user_timezones = data
                        elif key == 'user_states':
                            user_states = data
                        elif key == 'user_chat_mapping':
                            # Migration: Convert old format (int) to new format (dict)
                            migrated_count = 0
                            for uid, value in data.items():
                                if isinstance(value, int):
                                    # Old format: user_chat_mapping[uid] = chat_id (int)
                                    data[uid] = {
                                        'chat_id': value,
                                        'username': '',
                                        'first_name': '',
                                        'last_name': ''
                                    }
                                    migrated_count += 1
                            user_chat_mapping = data
                            if migrated_count > 0:
                                print(f"   🔄 Migrated {migrated_count} user_chat_mapping entries to new format")
                        elif key == 'ai_knowledge_base':
                            ai_knowledge_base = data
                        elif key == 'user_ai_chat_mode':
                            user_ai_chat_mode = data
                        elif key == 'organizations':
                            organizations = data
                        elif key == 'user_organizations':
                            user_organizations = data
                        elif key == 'user_active_org':
                            user_active_org = data
                        elif key == 'departments':
                            departments = data
                        elif key == 'contacts':
                            contacts = data
                        elif key == 'web_sources':
                            web_sources = data
                        elif key == 'proactive_suggestions':
                            proactive_suggestions = data
                        
                        loaded_count += 1
                except Exception as e:
                    print(f"⚠️ Error loading {key}: {e}")
        
        if loaded_count > 0:
            print(f"✅ Loaded {loaded_count} data files")
            # Print stats
            print(f"   📊 Organizations: {len(organizations)}")
            print(f"   👥 Users with tasks: {len(user_tasks)}")
            print(f"   🏢 Departments: {sum(len(v) for v in departments.values())}")
            print(f"   📇 Contacts: {sum(len(v) for v in contacts.values())}")
            print(f"   🧠 KB entries: {sum(len(v) for v in ai_knowledge_base.values())}")
        else:
            print("ℹ️ No existing data found, starting fresh")
    except Exception as e:
        print(f"❌ Error loading data: {e}")

def auto_backup():
    """Create automatic backup of all data"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"backup_{timestamp}.zip"
        
        # Create zip archive
        import zipfile
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filepath in DATA_FILES.values():
                if filepath.exists():
                    zipf.write(filepath, filepath.name)
        
        print(f"✅ Backup created: {backup_file.name}")
        
        # Keep only last 7 backups
        backups = sorted(BACKUP_DIR.glob("backup_*.zip"), key=lambda x: x.stat().st_mtime, reverse=True)
        for old_backup in backups[7:]:
            old_backup.unlink()
            print(f"🗑️ Deleted old backup: {old_backup.name}")
    except Exception as e:
        print(f"⚠️ Error creating backup: {e}")


def get_user_id(message):
    """Lấy user ID từ message (để đảm bảo privacy trong group)"""
    return message.from_user.id

def update_user_chat_mapping(message):
    """Cập nhật mapping user_id -> chat_id và thông tin user để gửi reminder và share task"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    
    # Lưu đầy đủ thông tin user
    user_chat_mapping[user_id] = {
        'chat_id': chat_id,
        'username': message.from_user.username or '',
        'first_name': message.from_user.first_name or '',
        'last_name': message.from_user.last_name or ''
    }

def get_user_timezone(user_id):
    """Lấy timezone offset của user (mặc định GMT+7)"""
    return user_timezones.get(user_id, 7)  # Mặc định Việt Nam GMT+7

def get_user_time(user_id, utc_time=None):
    """Chuyển UTC time sang giờ của user"""
    if utc_time is None:
        utc_time = datetime.utcnow()
    offset = get_user_timezone(user_id)
    return utc_time + timedelta(hours=offset)

def to_utc_time(user_id, local_time):
    """Chuyển giờ local của user sang UTC"""
    offset = get_user_timezone(user_id)
    return local_time - timedelta(hours=offset)

def create_calendar(user_id, year=None, month=None):
    """Tạo calendar keyboard để chọn ngày"""
    user_now = get_user_time(user_id)
    
    if year is None:
        year = user_now.year
    if month is None:
        month = user_now.month
    
    markup = types.InlineKeyboardMarkup(row_width=7)
    
    # Header với tên tháng và năm
    month_name = calendar.month_name[month]
    header = types.InlineKeyboardButton(
        f"📅 {month_name} {year}",
        callback_data="calendar_ignore"
    )
    markup.row(header)
    
    # Navigation buttons
    btn_prev = types.InlineKeyboardButton("◀️", callback_data=f"calendar_prev_{year}_{month}")
    btn_today = types.InlineKeyboardButton("📍 Hôm nay", callback_data=f"calendar_today")
    btn_next = types.InlineKeyboardButton("▶️", callback_data=f"calendar_next_{year}_{month}")
    markup.row(btn_prev, btn_today, btn_next)
    
    # Days of week header
    week_days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    markup.row(*[types.InlineKeyboardButton(day, callback_data="calendar_ignore") for day in week_days])
    
    # Calendar days
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="calendar_ignore"))
            else:
                # Kiểm tra nếu là ngày trong quá khứ
                date = datetime(year, month, day)
                if date.date() < user_now.date():
                    row.append(types.InlineKeyboardButton(str(day), callback_data="calendar_ignore"))
                else:
                    row.append(types.InlineKeyboardButton(
                        str(day),
                        callback_data=f"calendar_day_{year}_{month}_{day}"
                    ))
        markup.row(*row)
    
    # Quick select buttons
    btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="calendar_cancel")
    markup.row(btn_cancel)
    
    return markup

def create_time_picker(user_id, selected_date=None, selected_hour=None):
    """Tạo time picker keyboard để chọn giờ"""
    markup = types.InlineKeyboardMarkup(row_width=6)
    
    if selected_date:
        date_str = selected_date.strftime("%d/%m/%Y")
        header = types.InlineKeyboardButton(
            f"🕐 Chọn giờ - {date_str}",
            callback_data="time_ignore"
        )
        markup.row(header)
    else:
        header = types.InlineKeyboardButton("🕐 Chọn giờ", callback_data="time_ignore")
        markup.row(header)
    
    if selected_hour is None:
        # Chọn giờ (0-23)
        user_now = get_user_time(user_id)
        current_hour = user_now.hour if selected_date and selected_date.date() == user_now.date() else -1
        
        # Hiển thị giờ theo nhóm
        markup.row(*[types.InlineKeyboardButton("Giờ", callback_data="time_ignore")])
        
        hours_rows = []
        for h in range(24):
            if selected_date and selected_date.date() == user_now.date() and h < current_hour:
                continue  # Skip past hours for today
            hours_rows.append(types.InlineKeyboardButton(
                f"{h:02d}h",
                callback_data=f"time_hour_{h}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
            ))
        
        # Chia thành các hàng 6 nút
        for i in range(0, len(hours_rows), 6):
            markup.row(*hours_rows[i:i+6])
    else:
        # Chọn phút (0, 15, 30, 45)
        markup.row(*[types.InlineKeyboardButton("Phút", callback_data="time_ignore")])
        
        minutes = [0, 15, 30, 45]
        min_buttons = []
        for m in minutes:
            min_buttons.append(types.InlineKeyboardButton(
                f"{m:02d}",
                callback_data=f"time_minute_{selected_hour}_{m}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
            ))
        markup.row(*min_buttons)
        
        # Thêm các phút khác (5, 10, 20, 25, 35, 40, 50, 55)
        other_minutes = [5, 10, 20, 25, 35, 40, 50, 55]
        other_min_buttons = []
        for m in other_minutes:
            other_min_buttons.append(types.InlineKeyboardButton(
                f"{m:02d}",
                callback_data=f"time_minute_{selected_hour}_{m}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
            ))
        # Chia thành 2 hàng
        markup.row(*other_min_buttons[:4])
        markup.row(*other_min_buttons[4:])
        
        # Nút nhập thủ công
        btn_manual = types.InlineKeyboardButton(
            "✍️ Nhập chính xác (VD: 27)",
            callback_data=f"time_manual_minute_{selected_hour}_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
        )
        markup.row(btn_manual)
        
        # Nút quay lại chọn giờ
        btn_back = types.InlineKeyboardButton("🔙 Chọn lại giờ", callback_data=f"time_back_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}")
        markup.row(btn_back)
    
    # Quick time buttons
    markup.row(types.InlineKeyboardButton("⏱️ 5 phút", callback_data="time_quick_5m"),
               types.InlineKeyboardButton("⏱️ 15 phút", callback_data="time_quick_15m"),
               types.InlineKeyboardButton("⏱️ 30 phút", callback_data="time_quick_30m"))
    markup.row(types.InlineKeyboardButton("⏱️ 1 giờ", callback_data="time_quick_1h"),
               types.InlineKeyboardButton("⏱️ 2 giờ", callback_data="time_quick_2h"),
               types.InlineKeyboardButton("⏱️ 3 giờ", callback_data="time_quick_3h"))
    
    # Nút nhập thủ công (nếu chưa chọn giờ hoặc đã chọn ngày)
    if selected_date:
        btn_manual_time = types.InlineKeyboardButton(
            "✍️ Nhập giờ (VD: 14:30)",
            callback_data=f"time_manual_full_{selected_date.strftime('%Y_%m_%d') if selected_date else 'today'}"
        )
        markup.row(btn_manual_time)
    
    btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="time_cancel")
    markup.row(btn_cancel)
    
    return markup

# Background thread để kiểm tra và gửi reminder
def reminder_checker():
    """Kiểm tra và gửi thông báo nhắc nhở"""
    while True:
        try:
            current_time = datetime.utcnow()  # Sử dụng UTC time
            for user_id, tasks in list(user_tasks.items()):
                for task in tasks:
                    if task.get('remind_time') and not task.get('reminded'):
                        remind_time = task['remind_time']  # Đã lưu ở UTC
                        
                        # Parse string to datetime if needed (for safety)
                        if isinstance(remind_time, str):
                            try:
                                remind_time = datetime.strptime(remind_time, "%Y-%m-%d %H:%M:%S")
                                task['remind_time'] = remind_time  # Update to datetime object
                            except:
                                continue  # Skip if parse fails
                        
                        # Kiểm tra nếu đã đến giờ nhắc (trong vòng 1 phút)
                        if remind_time <= current_time < remind_time + timedelta(minutes=1):
                            try:
                                # Lấy chat_id từ mapping (có thể là private chat hoặc group)
                                chat_id = user_chat_mapping.get(user_id, {}).get('chat_id')
                                if not chat_id:
                                    print(f"No chat_id mapping for user_id {user_id}")
                                    continue
                                
                                print(f"Sending reminder to user_id {user_id} (chat_id {chat_id}): {task['content']}")
                                reminder_text = f"⏰ NHẮC NHỞ!\n\n📌 {task['content']}"
                                if task.get('done'):
                                    reminder_text += "\n\n✅ (Đã hoàn thành)"
                                
                                # Tạo inline keyboard với các nút menu
                                markup = types.InlineKeyboardMarkup(row_width=2)
                                
                                # Tìm index của task để tạo callback
                                task_idx = user_tasks[user_id].index(task)
                                
                                # Nếu task chưa hoàn thành, thêm nút Done
                                if not task.get('done'):
                                    btn_done = types.InlineKeyboardButton("✅ Hoàn thành", callback_data=f"task_done_{task_idx}")
                                    btn_snooze = types.InlineKeyboardButton("💤 Hoãn 15 phút", callback_data=f"reminder_snooze_{task_idx}_15")
                                    markup.add(btn_done, btn_snooze)
                                
                                # Các nút chung
                                btn_list = types.InlineKeyboardButton("📋 Xem tất cả", callback_data="menu_list")
                                btn_add = types.InlineKeyboardButton("➕ Thêm task", callback_data="menu_add")
                                markup.add(btn_list, btn_add)
                                
                                btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
                                markup.add(btn_menu)
                                
                                bot.send_message(chat_id, reminder_text, reply_markup=markup)
                                task['reminded'] = True
                                save_data()
                                print(f"Reminder sent successfully to user_id {user_id}")
                            except Exception as e:
                                print(f"Error sending reminder: {e}")
            time.sleep(30)  # Kiểm tra mỗi 30 giây
        except Exception as e:
            print(f"Error in reminder_checker: {e}")
            time.sleep(30)

# ============= AUTO LEARNING WORKER =============

def auto_learning_worker():
    """Background thread tự động học từ web sources"""
    print("🤖 Auto-learning worker started")
    
    while True:
        try:
            time.sleep(300)  # Check mỗi 5 phút xem có org nào cần update
            
            # Kiểm tra từng organization có web sources
            for org_id, sources_list in list(web_sources.items()):
                if not sources_list:
                    continue
                
                # Kiểm tra setting của org
                org = organizations.get(org_id)
                if not org:
                    continue
                
                settings = org.get('settings', {})
                if not settings.get('auto_learning', False):
                    continue  # Skip nếu auto-learning bị tắt
                
                learning_frequency = settings.get('learning_frequency', 3600)  # Default 1 hour
                
                # Lấy owner của org để notify
                owner_id = org.get('owner_user_id')
                if not owner_id:
                    continue
                
                new_items_count = 0
                
                # Scrape và extract từ mỗi source
                for source in sources_list:
                    try:
                        url = source.get('url')
                        if not url:
                            continue
                        
                        # Check last scraped time (không scrape quá thường xuyên)
                        last_scraped = source.get('last_scraped')
                        if last_scraped:
                            try:
                                last_time = datetime.fromisoformat(last_scraped)
                                time_since_scrape = (datetime.utcnow() - last_time).total_seconds()
                                if time_since_scrape < learning_frequency:
                                    continue  # Skip nếu chưa đến lúc scrape
                            except:
                                pass
                        
                        print(f"Auto-learning: Scraping {url[:50]}...")
                        
                        # Scrape website
                        data, error = scrape_website(url)
                        if error or not data:
                            source['status'] = 'failed'
                            source['last_error'] = error
                            continue
                        
                        # Update source với raw content
                        source['raw_content'] = data.get('raw_content')
                        source['title'] = data.get('title')
                        source['description'] = data.get('description')
                        source['last_scraped'] = datetime.utcnow().isoformat()
                        source['status'] = 'success'
                        
                        # Auto-extract FAQ và important content
                        extracted_items = auto_extract_knowledge(data, url)
                        
                        if extracted_items:
                            # Add to knowledge base cho owner
                            for item in extracted_items:
                                add_to_knowledge_base(
                                    owner_id,
                                    item['question'],
                                    item['answer'],
                                    source='auto_learn',
                                    metadata={
                                        'url': url,
                                        'title': data.get('title'),
                                        'auto_extracted': True,
                                        'confidence': item.get('confidence', 0.7)
                                    }
                                )
                                new_items_count += 1
                            
                            print(f"Auto-learned {len(extracted_items)} items from {url[:50]}")
                        
                        save_data()
                        time.sleep(2)  # Delay giữa các request
                        
                    except Exception as e:
                        print(f"Error auto-learning from {url[:50]}: {e}")
                        continue
                
                # Notify user về dữ liệu mới
                if new_items_count > 0:
                    try:
                        chat_id = user_chat_mapping.get(owner_id, {}).get('chat_id')
                        if chat_id:
                            notify_text = (
                                f"🤖 **HỌC TỰ ĐỘNG**\n\n"
                                f"Bot đã tự động học được **{new_items_count} mục** "
                                f"mới từ web sources của {org['name']}!\n\n"
                                f"💡 Bạn có thể hỏi bot về những thông tin mới này."
                            )
                            
                            markup = types.InlineKeyboardMarkup()
                            btn_kb = types.InlineKeyboardButton("📚 Xem KB", callback_data="kb_list")
                            btn_menu = types.InlineKeyboardButton("🏠 Menu", callback_data="menu_main")
                            markup.add(btn_kb, btn_menu)
                            
                            bot.send_message(chat_id, notify_text, reply_markup=markup, parse_mode='Markdown')
                            print(f"Notified user {owner_id} about {new_items_count} new items")
                    except Exception as e:
                        print(f"Error notifying user: {e}")
            
        except Exception as e:
            print(f"Error in auto_learning_worker: {e}")
            time.sleep(60)

def auto_extract_knowledge(scraped_data, url):
    """Tự động extract kiến thức từ raw content"""
    if not scraped_data or 'raw_content' not in scraped_data:
        return []
    
    raw_content = scraped_data['raw_content']
    title = scraped_data.get('title', '')
    extracted = []
    
    # 1. Extract FAQ sections
    faq_items = extract_faq_from_content(raw_content)
    extracted.extend(faq_items)
    
    # 2. Extract heading-based Q&A
    heading_items = extract_headings_qa(raw_content, title)
    extracted.extend(heading_items)
    
    # 3. Extract key facts (definitions, statistics, important points)
    fact_items = extract_key_facts(raw_content, title)
    extracted.extend(fact_items)
    
    # Deduplicate và limit
    seen = set()
    unique_items = []
    for item in extracted:
        key = item['question'].lower().strip()
        if key not in seen and len(unique_items) < 20:  # Limit 20 items per scrape
            seen.add(key)
            unique_items.append(item)
    
    return unique_items

def extract_faq_from_content(content):
    """Extract FAQ từ content"""
    items = []
    lines = content.split('\n')
    
    in_faq = False
    current_q = None
    current_a = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect FAQ section
        if any(marker in line.lower() for marker in ['faq', 'câu hỏi', 'q&a', 'questions']):
            in_faq = True
            continue
        
        if in_faq:
            # Detect question (Q:, Câu hỏi:, 1., etc.)
            if (line.startswith(('Q:', 'Q.', 'Câu hỏi:', '?')) or 
                (line[0].isdigit() and '?' in line)):
                
                # Save previous Q&A
                if current_q and current_a:
                    items.append({
                        'question': current_q,
                        'answer': ' '.join(current_a).strip(),
                        'confidence': 0.9
                    })
                
                # Start new question
                current_q = line.lstrip('Q:.? 0123456789').strip()
                current_a = []
            
            # Detect answer (A:, Trả lời:, etc.)
            elif line.startswith(('A:', 'A.', 'Trả lời:', 'Answer:')):
                current_a = [line.lstrip('A:.Trả lời: Answer:').strip()]
            
            # Continue answer
            elif current_q and len(line) > 20:
                current_a.append(line)
            
            # Exit FAQ section
            elif len(items) > 0 and not any(c in line for c in ['?', 'Q', 'A']):
                in_faq = False
    
    # Save last Q&A
    if current_q and current_a:
        items.append({
            'question': current_q,
            'answer': ' '.join(current_a).strip(),
            'confidence': 0.9
        })
    
    return items

def extract_headings_qa(content, title):
    """Extract Q&A từ headings và content"""
    items = []
    lines = content.split('\n')
    
    current_heading = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect heading (short line, all caps hoặc title case)
        if (len(line) < 100 and 
            (line.isupper() or line.istitle()) and 
            not line.endswith(('.', '!', '?'))):
            
            # Save previous section
            if current_heading and current_content:
                content_text = ' '.join(current_content).strip()
                if len(content_text) > 50:
                    # Convert heading to question
                    question = f"{current_heading}?"
                    if not question.endswith('?'):
                        question = f"Thông tin về {current_heading.lower()}?"
                    
                    items.append({
                        'question': question,
                        'answer': content_text[:500],  # Limit 500 chars
                        'confidence': 0.7
                    })
            
            # Start new section
            current_heading = line
            current_content = []
        
        # Collect content
        elif current_heading and len(line) > 20:
            current_content.append(line)
            if len(current_content) > 5:  # Limit paragraphs
                break
    
    # Save last section
    if current_heading and current_content:
        content_text = ' '.join(current_content).strip()
        if len(content_text) > 50:
            question = f"Thông tin về {current_heading.lower()}?"
            items.append({
                'question': question,
                'answer': content_text[:500],
                'confidence': 0.7
            })
    
    return items[:5]  # Limit 5 heading-based items

def extract_key_facts(content, title):
    """Extract các thông tin quan trọng"""
    items = []
    lines = content.split('\n')
    
    # Look for definition patterns
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) < 20 or len(line) > 200:
            continue
        
        # Detect definitions (là, nghĩa là, được định nghĩa, is defined as, etc.)
        if any(marker in line.lower() for marker in [' là ', ' nghĩa là ', ' được định nghĩa', 'is defined', 'means']):
            # Try to split into term and definition
            for marker in [' là ', ' nghĩa là ', ' được định nghĩa là ']:
                if marker in line.lower():
                    parts = line.split(marker, 1)
                    if len(parts) == 2:
                        term = parts[0].strip()
                        definition = parts[1].strip()
                        
                        if len(term) > 3 and len(definition) > 20:
                            items.append({
                                'question': f"{term} là gì?",
                                'answer': definition,
                                'confidence': 0.8
                            })
                            break
    
    return items[:5]  # Limit 5 facts

# Khởi động background threads
reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
reminder_thread.start()

auto_learning_thread = threading.Thread(target=auto_learning_worker, daemon=True)
auto_learning_thread.start()

def show_main_menu(user_id, message_text="👋 Xin chào! Tôi là trợ lý đa chức năng của bạn."):
    """Hiển thị menu chính với các category"""
    tz = get_user_timezone(user_id)
    task_count = len(user_tasks.get(user_id, []))
    
    # Enterprise stats
    org_id = get_active_org(user_id)
    org_name = ""
    if org_id and org_id in organizations:
        org_name = organizations[org_id]['name']
    
    text = f"{message_text}\n\n"
    text += f"📊 **Thống kê:**\n"
    text += f"   • 📋 Tasks: {task_count}\n"
    text += f"   • 🌍 Múi giờ: GMT+{tz}\n"
    if org_name:
        text += f"   • 🏢 Org: {org_name}\n"
    text += f"\n🎯 **Chọn chức năng:**"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Row 1: Task Management & Voice Tools
    btn_tasks = types.InlineKeyboardButton("📋 Quản Lý Task", callback_data="category_tasks")
    btn_voice = types.InlineKeyboardButton("🎤 Công Cụ Voice", callback_data="category_voice")
    markup.add(btn_tasks, btn_voice)
    
    # Row 2: AI Assistant & Enterprise
    btn_ai = types.InlineKeyboardButton("🤖 Trợ Lý AI", callback_data="category_ai")
    btn_enterprise = types.InlineKeyboardButton("🏢 Doanh Nghiệp", callback_data="category_enterprise")
    markup.add(btn_ai, btn_enterprise)
    
    # Row 3: Quick Actions & Settings
    btn_quick = types.InlineKeyboardButton("⚡ Thêm Nhanh", callback_data="menu_add")
    btn_settings = types.InlineKeyboardButton("⚙️ Cài Đặt", callback_data="category_settings")
    markup.add(btn_quick, btn_settings)
    
    # Row 4: Help
    btn_help = types.InlineKeyboardButton("❓ Trợ Giúp", callback_data="menu_help")
    markup.add(btn_help)
    
    return text, markup

def show_tasks_menu(user_id):
    """Hiển thị menu Task Management"""
    task_count = len(user_tasks.get(user_id, []))
    pending = sum(1 for t in user_tasks.get(user_id, []) if not t.get('done', False))
    completed = task_count - pending
    
    text = f"📋 **QUẢN LÝ CÔNG VIỆC**\n\n"
    text += f"📊 Thống kê:\n"
    text += f"   • Tổng: {task_count} tasks\n"
    text += f"   • Đang làm: {pending} tasks\n"
    text += f"   • Hoàn thành: {completed} tasks\n\n"
    text += f"🎯 Chọn thao tác:"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_add = types.InlineKeyboardButton("➕ Thêm task", callback_data="menu_add")
    btn_smart = types.InlineKeyboardButton("🤖 AI Smart Add", callback_data="menu_smart_add")
    btn_list = types.InlineKeyboardButton("📋 Xem tất cả", callback_data="menu_list")
    markup.add(btn_add, btn_smart)
    markup.add(btn_list)
    
    if task_count > 0:
        btn_pending = types.InlineKeyboardButton("⏳ Tasks đang làm", callback_data="tasks_pending")
        btn_completed = types.InlineKeyboardButton("✅ Tasks hoàn thành", callback_data="tasks_completed")
        markup.add(btn_pending, btn_completed)
    
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_back)
    
    return text, markup

def show_voice_menu(user_id):
    """Hiển thị menu Voice Tools"""
    text = (
        "🎤 **CÔNG CỤ VOICE**\n\n"
        "✨ Chức năng:\n"
        "   • Chuyển giọng nói thành văn bản\n"
        "   • Hỗ trợ tiếng Việt & English\n"
        "   • Xuất file .txt\n"
        "   • Powered by OpenAI Whisper\n\n"
        "📱 Cách sử dụng:\n"
        "   1. Ghi âm voice message\n"
        "   2. Gửi cho bot\n"
        "   3. Nhận file .txt\n\n"
        "💰 Chi phí: ~150 VND/phút\n\n"
        "🎯 Thao tác:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_guide = types.InlineKeyboardButton("📖 Hướng dẫn chi tiết", callback_data="voice_guide")
    btn_demo = types.InlineKeyboardButton("🎬 Xem demo", callback_data="voice_demo")
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_guide, btn_demo, btn_back)
    
    return text, markup

def show_ai_menu(user_id):
    """Hiển thị menu AI Assistant"""
    has_github_token = bool(GITHUB_TOKEN)
    has_openai_key = bool(OPENAI_API_KEY)
    kb_count = len(ai_knowledge_base.get(user_id, []))
    chat_mode = user_ai_chat_mode.get(user_id, False)
    
    text = (
        "🤖 **TRỢ LÝ AI**\n\n"
        "✨ Tính năng AI:\n"
        "   • 💬 Tạo Task Từ Ngôn Ngữ Tự Nhiên\n"
        "   • 🎤 Chuyển Đổi Giọng Nói Thành Văn Bản\n"
        "   • 🧠 AI Tự Động Trả Lời (NEW!)\n"
        "   • 📚 Quản Lý Kiến Thức AI\n\n"
        "🔑 Trạng thái:\n"
        f"   • GitHub AI: {'✅ Hoạt động' if has_github_token else '❌ Chưa cấu hình'}\n"
        f"   • OpenAI: {'✅ Hoạt động' if has_openai_key else '❌ Chưa cấu hình'}\n"
        f"   • Chế độ AI Chat: {'🟢 BẬT' if chat_mode else '⚪ TẮT'}\n"
        f"   • Dữ liệu học: {kb_count} cặp Q&A\n\n"
        "🎯 Thao tác:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    if has_github_token:
        btn_nl = types.InlineKeyboardButton("💬 Tạo task bằng ngôn ngữ tự nhiên", callback_data="ai_natural_language")
    else:
        btn_nl = types.InlineKeyboardButton("🔒 Setup GitHub AI", callback_data="ai_setup_github")
    markup.add(btn_nl)
    
    # Nút bật/tắt chế độ AI Chat
    if chat_mode:
        btn_chat = types.InlineKeyboardButton("⚪ Tắt AI Chat", callback_data="ai_chat_toggle")
    else:
        btn_chat = types.InlineKeyboardButton("🟢 Bật AI Chat", callback_data="ai_chat_toggle")
    markup.add(btn_chat)
    
    # Menu quản lý kiến thức
    btn_kb = types.InlineKeyboardButton("📚 Quản lý kiến thức AI", callback_data="ai_knowledge_menu")
    markup.add(btn_kb)
    
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_back)
    
    return text, markup

def show_settings_menu(user_id):
    """Hiển thị menu Settings"""
    tz = get_user_timezone(user_id)
    
    text = (
        "⚙️ **CÀI ĐẶT**\n\n"
        f"🌍 **Múi giờ hiện tại:** GMT+{tz}\n"
        f"📋 **Tổng tasks:** {len(user_tasks.get(user_id, []))}\n\n"
        "🎯 Cấu hình:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_tz = types.InlineKeyboardButton("🌍 Đổi múi giờ", callback_data="menu_timezone")
    btn_clear = types.InlineKeyboardButton("🗑️ Xóa dữ liệu", callback_data="settings_clear_confirm")
    markup.add(btn_tz, btn_clear)
    
    btn_about = types.InlineKeyboardButton("ℹ️ Về bot", callback_data="settings_about")
    btn_stats = types.InlineKeyboardButton("📊 Thống kê", callback_data="settings_stats")
    markup.add(btn_about, btn_stats)
    
    btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
    markup.add(btn_back)
    
    return text, markup

# Lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
    print(f"Received /start from chat_id: {bot_message.chat.id}, user_id: {bot_message.from_user.id}")
    user_id = get_user_id(bot_message)
    chat_id = bot_message.chat.id
    update_user_chat_mapping(bot_message)
    
    text, markup = show_main_menu(user_id)
    bot.send_message(chat_id, text, reply_markup=markup)

# Lệnh /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📚 **HƯỚNG DẪN SỬ DỤNG BOT**\n\n"
        "🎯 **MENU CHÍNH:**\n"
        "Bot được chia thành 6 danh mục:\n\n"
        "📋 **Quản Lý Task** - Quản lý công việc\n"
        "   • Thêm/Xem/Sửa/Xóa tasks\n"
        "   • Đặt nhắc nhở với lịch\n"
        "   • Lọc theo trạng thái\n"
        "   • Cập nhật tiến độ (0-100%)\n\n"
        "🎤 **Công Cụ Voice** - Chuyển giọng nói thành văn bản\n"
        "   • Gửi voice → Nhận file .txt\n"
        "   • Hỗ trợ tiếng Việt & English\n"
        "   • Sử dụng OpenAI Whisper\n\n"
        "🤖 **Trợ Lý AI** - Trợ lý thông minh\n"
        "   • Tạo task từ ngôn ngữ tự nhiên\n"
        "   • AI phân tích và tạo nhắc nhở\n"
        "   • Gợi ý thông minh (sắp có)\n\n"
        "⚡ **Thêm Nhanh** - Thêm task nhanh\n"
        "   • Thêm task trực tiếp từ menu chính\n"
        "   • Không cần vào menu phụ\n\n"
        "⚙️ **Cài Đặt** - Cấu hình\n"
        "   • Đổi múi giờ\n"
        "   • Xóa dữ liệu\n"
        "   • Xem thống kê\n\n"
        "❓ **Trợ Giúp** - Hướng dẫn và hỗ trợ\n\n"
        "📝 **LỆNH NHANH:**\n"
        "   • /add [nội dung] - Thêm task\n"
        "   • /done [số] - Hoàn thành task\n"
        "   • /progress [số] [%] [ghi chú] - Cập nhật tiến độ\n"
        "   • /share - Chia sẻ task cho người khác\n"
        "   • /list - Xem danh sách\n"
        "   • /smart_add - Thêm task bằng AI\n\n"
        "💡 **MẸO:**\n"
        "• Dùng nút menu để thao tác nhanh\n"
        "• Voice: Ghi âm cuộc họp → File văn bản\n"
        "• AI: Nói tự nhiên → Task + Nhắc nhở\n"
        "• Progress: Theo dõi tiến độ + Ghi chú chi tiết\n"
        "• Nút 📝: Xem lịch sử cập nhật\n"
        "• Nút 📤: Chia sẻ task qua Telegram\n"
        "• Gửi /start để quay về menu chính"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
    markup.add(btn_menu)
    
    bot.send_message(message.chat.id, help_text, reply_markup=markup, parse_mode='Markdown')

# Lệnh /timezone để đặt múi giờ
@bot.message_handler(commands=['timezone'])
def set_timezone(message):
    print(f"Received /timezone from chat_id: {message.chat.id}, user_id: {message.from_user.id}")
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            # Hiển thị timezone hiện tại và hướng dẫn
            current_tz = get_user_timezone(user_id)
            tz_list = "\n".join([f"   {code} = GMT+{offset}" for code, offset in sorted(TIMEZONES.items(), key=lambda x: x[1])])
            bot.reply_to(message,
                f"🌍 Múi giờ hiện tại: GMT+{current_tz}\n\n"
                f"📝 Cách đặt múi giờ:\n"
                f"/timezone VN (Việt Nam)\n"
                f"/timezone GMT+7\n"
                f"/timezone +8\n\n"
                f"🌐 Các múi giờ phổ biến:\n{tz_list}")
            return
        
        tz_input = args[1].strip().upper()
        
        # Kiểm tra nếu là mã quốc gia
        if tz_input in TIMEZONES:
            user_timezones[user_id] = TIMEZONES[tz_input]
            bot.reply_to(message, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_input]} ({tz_input})")
            return
        
        # Kiểm tra định dạng GMT+X hoặc +X
        if tz_input.startswith('GMT'):
            tz_input = tz_input[3:]
        
        if tz_input.startswith('+') or tz_input.startswith('-'):
            offset = int(tz_input)
            if -12 <= offset <= 14:
                user_timezones[user_id] = offset
                bot.reply_to(message, f"✅ Đã đặt múi giờ: GMT{tz_input:+d}")
            else:
                bot.reply_to(message, "⚠️ Múi giờ không hợp lệ! Vui lòng chọn từ GMT-12 đến GMT+14")
        else:
            bot.reply_to(message, 
                "⚠️ Định dạng không hợp lệ!\n\n"
                "Sử dụng: /timezone VN hoặc /timezone +7")
    
    except (ValueError, IndexError):
        bot.reply_to(message, 
            "⚠️ Lỗi định dạng!\n\n"
            "Ví dụ: /timezone VN hoặc /timezone +7")

# Lệnh /add để thêm task
@bot.message_handler(commands=['add'])
def add_task(message):
    print(f"Received /add from chat_id: {message.chat.id}, user_id: {message.from_user.id}")
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    # Lấy nội dung sau lệnh /add
    task_content = message.text[len('/add '):].strip()
    
    if not task_content:
        # Chuyển sang chế độ hỏi nội dung
        user_states[user_id] = "waiting_task_content"
        bot.reply_to(message, 
            "✍️ Nhập nội dung công việc:\n\n"
            "(Ví dụ: Họp team lúc 9h sáng)")
        return

    if user_id not in user_tasks:
        user_tasks[user_id] = []
    
    user_tasks[user_id].append({
        'content': task_content, 
        'done': False,
        'remind_time': None,
        'reminded': False,
        'progress_percent': 0,
        'progress_updates': []
    })
    save_data()
    
    # Hiển thị với menu buttons
    markup = types.InlineKeyboardMarkup()
    btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{len(user_tasks[user_id])-1}")
    btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
    btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="menu_add")
    markup.add(btn_remind)
    markup.add(btn_list, btn_add)
    
    bot.reply_to(message,
        f"✅ Đã thêm: '{task_content}'",
        reply_markup=markup
    )

# ============= AI SMART TASK MANAGEMENT =============

@bot.message_handler(commands=['smart_add', 'ai_add'])
def smart_add_task(message):
    """
    Thêm task thông minh với AI Agent
    AI sẽ hỏi bổ sung thông tin nếu thiếu
    """
    print(f"Received /smart_add from chat_id: {message.chat.id}, user_id: {message.from_user.id}")
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    # Lấy nội dung sau lệnh
    content = message.text.split(maxsplit=1)
    message_text = content[1].strip() if len(content) > 1 else ""
    
    if not message_text:
        # Bắt đầu hỏi trực tiếp
        user_states[user_id] = "ai_collecting_task"
        ai_conversation_context[user_id] = {'task': {}, 'state': 'collecting', 'last_update': datetime.now()}
        
        # Hỏi trực tiếp tên công việc
        help_msg = "📝 Bạn muốn tạo công việc gì? Vui lòng cho tôi biết tên công việc nhé!"
        bot.reply_to(message, help_msg)
        return
    
    # Process với AI Agent
    result = ai_task_agent.process_message(message_text)
    
    if result['action'] == 'save_task':
        # Đủ thông tin - lưu task
        save_ai_task(user_id, result['task'])
        
        # Send confirmation
        bot.reply_to(message, result['ask_message'], parse_mode='Markdown')
        
        # Clear conversation context
        if user_id in ai_conversation_context:
            del ai_conversation_context[user_id]
        if user_id in user_states:
            del user_states[user_id]
    
    else:
        # Thiếu thông tin - hỏi thêm
        user_states[user_id] = "ai_collecting_task"
        ai_conversation_context[user_id] = {
            'task': result['task'],
            'state': 'collecting',
            'last_update': datetime.now()
        }
        
        bot.reply_to(message, result['ask_message'], parse_mode='Markdown')


def save_ai_task(user_id, task_data):
    """
    Lưu task từ AI Agent vào database
    Convert format từ AI Agent sang format của bot
    """
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    
    # Build content string cho compatibility với existing system
    content = f"📋 {task_data['task_name']}\n"
    content += f"👤 Phụ trách: {task_data['assignee']}\n"
    content += f"📅 Deadline: {task_data['deadline']}\n"
    content += f"🏷️ Nhóm: {task_data['task_group']}\n"
    content += f"⚡ Trạng thái: {task_data['status']}"
    
    if task_data.get('details'):
        content += f"\n📝 {task_data['details']}"
    
    # Create task in existing format
    new_task = {
        'content': content,
        'done': task_data['status'] == 'Hoàn thành',
        'remind_time': None,
        'reminded': False,
        'progress_percent': task_data['progress_percent'],
        'progress_updates': [],  # Initialize progress tracking
        # Additional AI fields
        'ai_task': True,
        'task_code': task_data['task_code'],
        'task_group': task_data['task_group'],
        'task_name': task_data['task_name'],
        'assignee': task_data['assignee'],
        'deadline': task_data['deadline'],
        'status': task_data['status'],
        'details': task_data.get('details', '')
    }
    
    user_tasks[user_id].append(new_task)
    save_data()
    
    print(f"✅ Saved AI task for user {user_id}: {task_data['task_code']} - {task_data['task_name']}")

# ============= END AI SMART TASK MANAGEMENT =============

# Lệnh /list để xem danh sách task
@bot.message_handler(commands=['list'])
def list_tasks(message):
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    show_task_list(user_id, chat_id)

# Lệnh /done để đánh dấu hoàn thành
@bot.message_handler(commands=['done'])
def mark_done(message):
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        task_number = int(message.text.split()[1])
        if 1 <= task_number <= len(user_tasks[user_id]):
            user_tasks[user_id][task_number - 1]['done'] = True
            save_data()
            bot.reply_to(message, f"✅ Đã đánh dấu hoàn thành: '{user_tasks[user_id][task_number - 1]['content']}'")
        else:
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[user_id])}")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Vui lòng nhập số thứ tự công việc.\n\nVí dụ: /done 1")

# Lệnh /progress để cập nhật tiến độ
@bot.message_handler(commands=['progress'])
def update_progress(message):
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        # Parse: /progress 1 50 [optional note]
        parts = message.text.split(maxsplit=3)
        
        if len(parts) < 3:
            bot.reply_to(message, 
                "⚠️ Vui lòng nhập đúng định dạng:\n\n"
                "/progress [số] [%] [ghi chú]\n\n"
                "Ví dụ:\n"
                "/progress 1 50\n"
                "/progress 1 50 Đã hoàn thành phân tích")
            return
        
        task_number = int(parts[1])
        progress = int(parts[2])
        note = parts[3] if len(parts) == 4 else None
        
        if task_number < 1 or task_number > len(user_tasks[user_id]):
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[user_id])}")
            return
        
        if progress < 0 or progress > 100:
            bot.reply_to(message, "⚠️ Tiến độ phải từ 0 đến 100%")
            return
        
        task_idx = task_number - 1
        
        # If no note provided, ask for it
        if note is None:
            user_states[user_id] = f"progress_note_{task_idx}_{progress}"
            
            markup = types.InlineKeyboardMarkup()
            btn_skip = types.InlineKeyboardButton("⏭️ Bỏ qua (không ghi chú)", callback_data=f"skip_progress_note_{task_idx}_{progress}")
            markup.add(btn_skip)
            
            bot.reply_to(message,
                f"📝 Nhập ghi chú cho cập nhật này:\n\n"
                f"(Hoặc nhấn nút bỏ qua)",
                reply_markup=markup)
            return
        
        # Has note - update directly
        old_progress = user_tasks[user_id][task_idx].get('progress_percent', 0)
        user_tasks[user_id][task_idx]['progress_percent'] = progress
        
        # Initialize progress_updates if not exists
        if 'progress_updates' not in user_tasks[user_id][task_idx]:
            user_tasks[user_id][task_idx]['progress_updates'] = []
        
        # Add update record
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'progress': progress,
            'old_progress': old_progress,
            'note': note
        }
        user_tasks[user_id][task_idx]['progress_updates'].append(update_record)
        print(f"📝 [/progress command] Added update: {old_progress}% → {progress}% (total: {len(user_tasks[user_id][task_idx]['progress_updates'])})")
        
        # Auto mark as done if 100%
        if progress == 100:
            user_tasks[user_id][task_idx]['done'] = True
            # Update status to "Hoàn thành" if it exists (for AI tasks)
            if 'status' in user_tasks[user_id][task_idx]:
                user_tasks[user_id][task_idx]['status'] = 'Hoàn thành'
        
        save_data()
        
        # Remove old progress line from content if exists
        task_content = re.sub(r'\n?📈 Đã hoàn thành: \d+%', '', user_tasks[user_id][task_idx]['content'])
        bot.reply_to(message, 
            f"✅ **Đã cập nhật tiến độ!**\n\n"
            f"📌 Task: {task_content}\n"
            f"📊 Đã hoàn thành: {get_progress_bar(progress)}\n"
            f"💬 Ghi chú: {note}",
            parse_mode='Markdown')
        
    except (IndexError, ValueError) as e:
        bot.reply_to(message, 
            "⚠️ Lỗi định dạng!\n\n"
            "Sử dụng: /progress [số] [%] [ghi chú]\n"
            "Ví dụ:\n"
            "/progress 1 50\n"
            "/progress 1 75 Đã test xong")

# Lệnh /share để chia sẻ task
@bot.message_handler(commands=['share'])
def share_tasks_command(message):
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống! Không có gì để chia sẻ.")
        return
    
    # Show task list with checkboxes
    text = "📤 **CHIA SẺ TASK**\n\nĐã chọn: 0/" + str(len(user_tasks[user_id])) + "\n\n👇 Click để chọn/bỏ chọn task:\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for idx, task in enumerate(user_tasks[user_id]):
        status = "✅" if task['done'] else "⏳"
        task_text = f"☐ {idx+1}. {status} {task['content'][:40]}"
        if len(task['content']) > 40:
            task_text += "..."
        
        btn = types.InlineKeyboardButton(
            task_text,
            callback_data=f"share_toggle_{idx}_"
        )
        markup.add(btn)
    
    # Control buttons
    btn_all = types.InlineKeyboardButton("☑ Chọn tất cả", callback_data="share_all")
    btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
    markup.row(btn_all)
    markup.add(btn_cancel)
    
    bot.reply_to(message, text, reply_markup=markup, parse_mode='Markdown')

# Lệnh /remind để đặt nhắc nhở
@bot.message_handler(commands=['remind'])
def set_reminder(message):
    print(f"Received /remind from chat_id: {message.chat.id}, user_id: {message.from_user.id}")
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
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
        
        if task_number < 1 or task_number > len(user_tasks[user_id]):
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[user_id])}")
            return
        
        # Parse thời gian (với timezone của user)
        remind_time = parse_time(time_str, user_id)
        
        if remind_time is None:
            bot.reply_to(message, 
                "⚠️ Định dạng thời gian không hợp lệ!\n\n"
                "Các định dạng hỗ trợ:\n"
                "• HH:MM (ví dụ: 14:30)\n"
                "• YYYY-MM-DD HH:MM\n"
                "• 30m (sau 30 phút)\n"
                "• 2h (sau 2 giờ)")
            return
        
        if remind_time <= datetime.utcnow():
            bot.reply_to(message, "⚠️ Thời gian nhắc nhở phải là thời điểm trong tương lai!")
            return
        
        # Cập nhật reminder (lưu ở UTC)
        user_tasks[user_id][task_number - 1]['remind_time'] = remind_time
        save_data()
        user_tasks[user_id][task_number - 1]['reminded'] = False
        
        task_content = user_tasks[user_id][task_number - 1]['content']
        # Hiển thị theo giờ local của user
        user_time = get_user_time(user_id, remind_time)
        remind_str = user_time.strftime("%d/%m/%Y %H:%M")
        
        bot.reply_to(message, 
            f"⏰ Đã đặt nhắc nhở!\n\n"
            f"📌 Công việc: {task_content}\n"
            f"🕐 Thời gian: {remind_str} (GMT+{get_user_timezone(user_id)})")
        
    except (IndexError, ValueError) as e:
        bot.reply_to(message, 
            "⚠️ Lỗi định dạng!\n\n"
            "Sử dụng: /remind [số] [thời gian]\n"
            "Ví dụ: /remind 1 14:30")

def parse_time(time_str, user_id=None):
    """Parse nhiều định dạng thời gian (trả về UTC time)"""
    try:
        # Định dạng: 30m, 2h, 1d (relative time)
        if time_str.endswith('m'):
            minutes = int(time_str[:-1])
            return datetime.utcnow() + timedelta(minutes=minutes)  # UTC
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            return datetime.utcnow() + timedelta(hours=hours)  # UTC
        elif time_str.endswith('d'):
            days = int(time_str[:-1])
            return datetime.utcnow() + timedelta(days=days)  # UTC
        
        # Định dạng: HH:MM (hôm nay, theo giờ local của user)
        if ':' in time_str and len(time_str.split()) == 1:
            time_parts = time_str.split(':')
            if len(time_parts) == 2:
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                # Lấy giờ local của user
                user_now = get_user_time(user_id) if user_id else datetime.utcnow()
                remind_time = user_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Nếu thời gian đã qua trong ngày hôm nay, chuyển sang ngày mai
                if remind_time <= user_now:
                    remind_time += timedelta(days=1)
                
                # Chuyển sang UTC
                return to_utc_time(user_id, remind_time) if user_id else remind_time
        
        # Định dạng: YYYY-MM-DD HH:MM (theo giờ local của user)
        if len(time_str.split()) == 2:
            local_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            return to_utc_time(user_id, local_time) if user_id else local_time
        
        # Định dạng: DD/MM/YYYY HH:MM (theo giờ local của user)
        if '/' in time_str:
            local_time = datetime.strptime(time_str, "%d/%m/%Y %H:%M")
            return to_utc_time(user_id, local_time) if user_id else local_time
        
        return None
    except:
        return None

# ============= AI FEATURES với GitHub Models =============

def call_github_ai(user_message, system_prompt="You are a helpful assistant."):
    """Gọi GitHub Models AI API"""
    if not GITHUB_TOKEN:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"GitHub AI API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error calling GitHub AI: {e}")
        return None

# ============= AI KNOWLEDGE BASE FUNCTIONS =============

def extract_keywords(text):
    """Trích xuất từ khóa từ câu hỏi (đơn giản)"""
    # Loại bỏ các từ phổ biến và ký tự đặc biệt
    stop_words = ['là', 'của', 'và', 'có', 'được', 'trong', 'cho', 'với', 'the', 'a', 'an', 'is', 'are', 'what', 'how', 'when', 'where', 'why', 'gì', 'như', 'thế', 'nào', 'khi', 'ở', 'đâu', 'tại', 'sao']
    words = text.lower().replace('?', '').replace('!', '').replace('.', '').split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords

def search_knowledge_base(user_id, question):
    """Tìm kiếm trong knowledge base theo từ khóa với metadata tracking"""
    if user_id not in ai_knowledge_base or not ai_knowledge_base[user_id]:
        return None
    
    question_keywords = set(extract_keywords(question))
    best_match = None
    best_score = 0
    best_match_idx = -1
    
    for idx, item in enumerate(ai_knowledge_base[user_id]):
        # Tính điểm match dựa trên từ khóa chung
        item_keywords = set(item.get('keywords', []))
        common_keywords = question_keywords & item_keywords
        score = len(common_keywords)
        
        # Bonus points for source reliability
        source = item.get('source', 'manual')
        if source.startswith('web_faq'):
            score += 0.5  # FAQ sources are more reliable
        elif source.startswith('web_heading'):
            score += 0.3
        
        # Kiểm tra match chính xác câu hỏi
        if question.lower().strip() == item['question'].lower().strip():
            # Update usage tracking
            item['usage_count'] = item.get('usage_count', 0) + 1
            item['last_used'] = datetime.utcnow().isoformat()
            save_data()
            
            # Return enhanced result with source info
            result = {
                'answer': item['answer'],
                'source': item.get('source', 'manual'),
                'source_url': item.get('source_url'),
                'source_title': item.get('source_title'),
                'confidence': 1.0  # Exact match
            }
            return result
        
        if score > best_score:
            best_score = score
            best_match = item
            best_match_idx = idx
    
    # Nếu có ít nhất 2 từ khóa trùng, trả về câu trả lời
    if best_score >= 2 and best_match:
        # Update usage tracking
        best_match['usage_count'] = best_match.get('usage_count', 0) + 1
        best_match['last_used'] = datetime.utcnow().isoformat()
        save_data()
        
        # Return enhanced result with source info
        result = {
            'answer': best_match['answer'],
            'source': best_match.get('source', 'manual'),
            'source_url': best_match.get('source_url'),
            'source_title': best_match.get('source_title'),
            'confidence': min(best_score / len(question_keywords), 1.0) if question_keywords else 0.5
        }
        return result
    
    return None

def add_to_knowledge_base(user_id, question, answer, source='manual', metadata=None):
    """Thêm cặp Q&A vào knowledge base với metadata đầy đủ"""
    if user_id not in ai_knowledge_base:
        ai_knowledge_base[user_id] = []
    
    keywords = extract_keywords(question)
    
    # Build knowledge entry with rich metadata
    entry = {
        'question': question,
        'answer': answer,
        'keywords': keywords,
        'source': source,  # manual, web, import, faq, heading, etc.
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'usage_count': 0,  # Track how many times this was used
        'last_used': None
    }
    
    # Add optional metadata
    if metadata:
        if 'url' in metadata:
            entry['source_url'] = metadata['url']
        if 'title' in metadata:
            entry['source_title'] = metadata['title']
        if 'category' in metadata:
            entry['category'] = metadata['category']
        if 'tags' in metadata:
            entry['tags'] = metadata['tags']
        if 'confidence' in metadata:
            entry['confidence'] = metadata['confidence']
    
    ai_knowledge_base[user_id].append(entry)
    save_data()
    return True

def get_ai_response(user_id, user_message):
    """Lấy câu trả lời AI - HỌC BỊ ĐỘNG (on-demand từ web sources)"""
    # 1. Tìm trong knowledge base trước (cache)
    kb_result = search_knowledge_base(user_id, user_message)
    if kb_result:
        answer = kb_result['answer']
        source = kb_result.get('source', 'manual')
        confidence = kb_result.get('confidence', 0.5)
        
        # Build response with source attribution
        response = f"📚 {answer}\n\n"
        
        # Add source information
        if kb_result.get('source_url'):
            source_title = kb_result.get('source_title', 'Website')
            source_url = kb_result['source_url']
            response += f"🔗 Nguồn: [{source_title[:50]}]({source_url})\n"
        elif source.startswith('web_'):
            response += f"🌐 Nguồn: Web source\n"
        elif source == 'text_import':
            response += f"📋 Nguồn: Import text\n"
        elif source == 'manual':
            response += f"✍️ Nguồn: Nhập thủ công\n"
        
        # Add confidence indicator
        if confidence >= 0.9:
            response += f"✅ Độ chính xác: Cao\n"
        elif confidence >= 0.6:
            response += f"⚡ Độ chính xác: Trung bình\n"
        
        response += "\n_[Từ KB cache]_"
        return response
    
    # 2. ON-DEMAND: Tìm trong web sources (HỌC BỊ ĐỘNG)
    org_id = get_active_org(user_id)
    if org_id and org_id in web_sources:
        sources_list = web_sources[org_id]
        
        # Try to extract answer from web sources on-demand
        for source in sources_list:
            if source.get('raw_content'):
                # Extract answer from cached raw content
                result = extract_answer_from_source(source, user_message)
                
                if result and result.get('answer'):
                    answer = result['answer']
                    confidence = result.get('confidence', 0.5)
                    
                    # Cache to KB for next time
                    add_to_knowledge_base(
                        user_id,
                        user_message,
                        answer,
                        source='web_on_demand',
                        metadata={
                            'url': result.get('source_url'),
                            'title': result.get('source_title'),
                            'extracted_on_demand': True
                        }
                    )
                    
                    # Build response
                    response = f"📚 {answer}\n\n"
                    response += f"🔗 Nguồn: [{result.get('source_title', 'Web Source')[:50]}]({result['source_url']})\n"
                    
                    if confidence >= 0.8:
                        response += f"✅ Độ tin cậy: Cao\n"
                    elif confidence >= 0.5:
                        response += f"⚡ Độ tin cậy: Trung bình\n"
                    
                    response += "\n_[Trích xuất từ web source]_"
                    return response
            
            elif source.get('url'):
                # Need to scrape on-demand if no cached content
                try:
                    data, error = scrape_website(source['url'])
                    if data and not error:
                        # Cache raw content
                        source['raw_content'] = data.get('raw_content')
                        source['title'] = data.get('title')
                        source['description'] = data.get('description')
                        save_data()
                        
                        # Extract answer
                        result = extract_answer_from_source(data, user_message)
                        
                        if result and result.get('answer'):
                            answer = result['answer']
                            confidence = result.get('confidence', 0.5)
                            
                            # Cache to KB
                            add_to_knowledge_base(
                                user_id,
                                user_message,
                                answer,
                                source='web_on_demand',
                                metadata={
                                    'url': result.get('source_url'),
                                    'title': result.get('source_title'),
                                    'extracted_on_demand': True
                                }
                            )
                            
                            # Build response
                            response = f"📚 {answer}\n\n"
                            response += f"🔗 Nguồn: [{result.get('source_title', 'Web Source')[:50]}]({result['source_url']})\n"
                            
                            if confidence >= 0.8:
                                response += f"✅ Độ tin cậy: Cao\n"
                            elif confidence >= 0.5:
                                response += f"⚡ Độ tin cậy: Trung bình\n"
                            
                            response += "\n_[Trích xuất on-demand từ web]_"
                            return response
                except Exception as e:
                    print(f"Error scraping on-demand: {e}")
                    continue
    
    # 3. Sử dụng AI reasoning nếu có GitHub token
    if GITHUB_TOKEN:
        # Lấy context từ knowledge base
        context = ""
        if user_id in ai_knowledge_base and ai_knowledge_base[user_id]:
            kb_items = ai_knowledge_base[user_id]
            sorted_items = sorted(
                kb_items,
                key=lambda x: (x.get('usage_count', 0) * 10 + (1 if x.get('last_used') else 0)),
                reverse=True
            )[:5]
            
            context = "Kiến thức có sẵn:\n"
            for item in sorted_items:
                context += f"- Q: {item['question']}\n"
                context += f"  A: {item['answer']}\n"
                if item.get('source_url'):
                    context += f"  URL: {item['source_url']}\n"
        
        system_prompt = f"""Bạn là trợ lý thông minh.
{context}

Sử dụng kiến thức trên để suy luận nếu liên quan.
Trả lời ngắn gọn bằng tiếng Việt."""
        
        ai_response = call_github_ai(user_message, system_prompt)
        if ai_response:
            return f"🤖 {ai_response}\n\n_[AI suy luận]_"
    
    return None

def show_knowledge_menu(user_id):
    """Hiển thị menu quản lý knowledge base"""
    kb_count = len(ai_knowledge_base.get(user_id, []))
    
    text = (
        "📚 **QUẢN LÝ KIẾN THỨC AI**\n\n"
        f"📊 Thống kê:\n"
        f"   • Tổng dữ liệu: {kb_count} cặp Q&A\n\n"
        "💡 Hướng dẫn:\n"
        "   • Thêm dữ liệu để AI học\n"
        "   • AI sẽ tự động trả lời dựa trên dữ liệu\n"
        "   • Nếu không tìm thấy, AI sẽ suy luận\n\n"
        "🎯 Thao tác:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_add = types.InlineKeyboardButton("➕ Thêm dữ liệu Q&A", callback_data="kb_add")
    markup.add(btn_add)
    
    if kb_count > 0:
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="kb_list")
        btn_clear = types.InlineKeyboardButton("🗑️ Xóa tất cả", callback_data="kb_clear_confirm")
        markup.add(btn_list, btn_clear)
    
    btn_back = types.InlineKeyboardButton("🔙 Menu AI", callback_data="category_ai")
    markup.add(btn_back)
    
    return text, markup

def parse_natural_language_task(user_text, user_id):
    """Sử dụng AI để parse task và thời gian từ ngôn ngữ tự nhiên"""
    user_now = get_user_time(user_id)
    current_time_str = user_now.strftime("%Y-%m-%d %H:%M")
    
    system_prompt = f"""Bạn là trợ lý thông minh phân tích công việc và thời gian.
Thời gian hiện tại: {current_time_str}
Múi giờ: GMT+{get_user_timezone(user_id)}

Nhiệm vụ: Phân tích câu của user và trả về JSON với format:
{{
  "task": "nội dung công việc",
  "time": "thời gian nhắc nhở",
  "has_reminder": true/false
}}

Quy tắc phân tích thời gian:
- "sáng mai", "mai sáng" → ngày mai 9:00
- "chiều mai", "mai chiều" → ngày mai 14:00
- "tối nay", "tối" → hôm nay 20:00
- "9h sáng", "9h" → 09:00 gần nhất (hôm nay hoặc mai)
- "2h chiều", "14h" → 14:00 gần nhất
- Nếu không có thời gian cụ thể: has_reminder = false

Chỉ trả về JSON, không thêm text khác."""
    
    ai_response = call_github_ai(user_text, system_prompt)
    
    if not ai_response:
        return None
    
    try:
        # Parse JSON từ AI response
        result = json.loads(ai_response)
        return result
    except:
        # Nếu AI không trả về JSON chuẩn, fallback
        return None

# ============= ENTERPRISE FUNCTIONS =============

def generate_id(prefix='item'):
    """Generate unique ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def get_active_org(user_id):
    """Lấy organization đang active của user"""
    return user_active_org.get(user_id)

def create_organization(user_id, org_name):
    """Tạo organization mới"""
    org_id = generate_id('org')
    organizations[org_id] = {
        'id': org_id,
        'name': org_name,
        'owner_user_id': user_id,
        'members': [user_id],
        'created_at': datetime.utcnow().isoformat(),
        'settings': {
            'private': True,
            'auto_import': True,
            'web_scraping': ENTERPRISE_ENABLED,
            'auto_learning': True,  # Tự động học từ web
            'learning_frequency': 3600  # Mỗi 1 giờ (seconds)
        }
    }
    
    # Add to user's org list
    if user_id not in user_organizations:
        user_organizations[user_id] = []
    user_organizations[user_id].append(org_id)
    
    # Set as active org
    user_active_org[user_id] = org_id
    
    # Initialize data structures
    departments[org_id] = []
    contacts[org_id] = []
    web_sources[org_id] = []
    
    save_data()
    return org_id

def add_department(org_id, name, manager='', description='', email='', phone=''):
    """Thêm phòng ban"""
    dept_id = generate_id('dept')
    dept = {
        'id': dept_id,
        'name': name,
        'manager': manager,
        'manager_contact': None,
        'description': description,
        'email': email,
        'phone': phone,
        'members': [],
        'created_at': datetime.utcnow().isoformat()
    }
    
    if org_id not in departments:
        departments[org_id] = []
    departments[org_id].append(dept)
    
    save_data()
    return dept_id

def add_contact(org_id, name, position='', department='', email='', phone='', extension='', skills=None, notes=''):
    """Thêm nhân viên/contact"""
    contact_id = generate_id('contact')
    contact = {
        'id': contact_id,
        'name': name,
        'position': position,
        'department': department,
        'email': email,
        'phone': phone,
        'extension': extension,
        'skills': skills or [],
        'notes': notes,
        'created_at': datetime.utcnow().isoformat()
    }
    
    if org_id not in contacts:
        contacts[org_id] = []
    contacts[org_id].append(contact)
    
    # Add to department members if specified
    if department:
        for dept in departments.get(org_id, []):
            if dept['id'] == department or dept['name'].lower() == department.lower():
                dept['members'].append(contact_id)
                break
    
    save_data()
    return contact_id

def search_department(org_id, query):
    """Tìm phòng ban theo tên hoặc từ khóa"""
    if org_id not in departments:
        return None
    
    query_lower = query.lower()
    best_match = None
    best_score = 0
    
    for dept in departments[org_id]:
        score = 0
        
        # Exact match
        if query_lower in dept['name'].lower():
            score += 10
        
        # Manager match
        if dept.get('manager') and query_lower in dept['manager'].lower():
            score += 5
        
        # Description match
        if dept.get('description') and query_lower in dept['description'].lower():
            score += 3
        
        # Keywords match
        keywords = extract_keywords(query)
        for kw in keywords:
            if kw in dept['name'].lower():
                score += 2
            if dept.get('description') and kw in dept['description'].lower():
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = dept
    
    return best_match if best_score > 0 else None

def search_contact(org_id, query):
    """Tìm nhân viên theo tên, chức vụ, skills"""
    if org_id not in contacts:
        return []
    
    query_lower = query.lower()
    results = []
    
    for contact in contacts[org_id]:
        score = 0
        
        # Name exact match
        if query_lower in contact['name'].lower():
            score += 10
        
        # Position match
        if contact.get('position') and query_lower in contact['position'].lower():
            score += 5
        
        # Skills match
        if contact.get('skills'):
            for skill in contact['skills']:
                if query_lower in skill.lower():
                    score += 3
        
        # Email match
        if contact.get('email') and query_lower in contact['email'].lower():
            score += 2
        
        # Keywords match
        keywords = extract_keywords(query)
        for kw in keywords:
            if kw in contact['name'].lower():
                score += 2
            if contact.get('position') and kw in contact['position'].lower():
                score += 1
        
        if score > 0:
            results.append((score, contact))
    
    # Sort by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    return [contact for score, contact in results[:5]]  # Top 5 results

def scrape_website(url):
    """Scrape nội dung từ website - CHỈ LẤY RAW CONTENT (không extract Q&A)"""
    if not ENTERPRISE_ENABLED:
        return None, "Enterprise features not enabled. Install: pip install beautifulsoup4"
    
    if not validators.url(url):
        return None, "URL không hợp lệ"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style tags
        for tag in soup(['script', 'style', 'meta', 'link', 'noscript']):
            tag.decompose()
        
        # Get raw text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Get metadata
        title = soup.title.string if soup.title else 'Untitled'
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content') if meta_desc else ''
        
        # Return raw data (NO Q&A extraction)
        return {
            'url': url,
            'title': title,
            'description': description,
            'raw_content': text[:50000],  # Limit to 50KB
            'content_length': len(text),
            'scraped_at': datetime.utcnow().isoformat(),
            'status': 'success'
        }, None
        
    except requests.RequestException as e:
        return None, f"Lỗi khi tải trang: {str(e)[:100]}"
    except Exception as e:
        return None, f"Lỗi: {str(e)[:100]}"

def extract_answer_from_source(source_data, question):
    """Trích xuất câu trả lời từ nguồn dữ liệu khi có câu hỏi (ON-DEMAND)"""
    if not source_data or 'raw_content' not in source_data:
        return None
    
    try:
        raw_content = source_data['raw_content']
        question_lower = question.lower()
        keywords = extract_keywords(question)
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in raw_content.split('\n') if len(p.strip()) > 20]
        
        # Find relevant paragraphs
        relevant_paras = []
        for para in paragraphs:
            para_lower = para.lower()
            score = 0
            
            # Check if question appears in paragraph
            if question_lower in para_lower:
                score += 10
            
            # Check keywords
            for kw in keywords:
                if kw in para_lower:
                    score += 1
            
            if score > 0:
                relevant_paras.append((score, para))
        
        # Sort by relevance
        relevant_paras.sort(key=lambda x: x[0], reverse=True)
        
        # Get top 3 most relevant paragraphs
        if relevant_paras:
            answer_parts = [para for score, para in relevant_paras[:3]]
            answer = '\n\n'.join(answer_parts)
            
            # Limit answer length
            if len(answer) > 1000:
                answer = answer[:1000] + '...'
            
            return {
                'answer': answer,
                'source_url': source_data.get('url'),
                'source_title': source_data.get('title'),
                'confidence': min(relevant_paras[0][0] / 10, 1.0),  # Normalize score
                'extracted_at': datetime.utcnow().isoformat()
            }
        
        return None
        
    except Exception as e:
        print(f"Error extracting answer: {e}")
        return None

def import_from_text(text_data, org_id=None):
    """Import dữ liệu từ text (format: question | answer)"""
    results = {
        'qa_pairs': 0,
        'departments': 0,
        'contacts': 0,
        'errors': []
    }
    
    lines = text_data.strip().split('\n')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            # Q&A format: question | answer
            if '|' in line:
                parts = line.split('|', 1)
                if len(parts) == 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    if question and answer:
                        results['qa_pairs'] += 1
                        # Store as Q&A pair
                        continue
            
            # Department format: [DEPT] name | manager | email
            elif line.startswith('[DEPT]'):
                line = line.replace('[DEPT]', '').strip()
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 1 and org_id:
                    name = parts[0]
                    manager = parts[1] if len(parts) > 1 else ''
                    email = parts[2] if len(parts) > 2 else ''
                    add_department(org_id, name, manager=manager, email=email)
                    results['departments'] += 1
                    continue
            
            # Contact format: [CONTACT] name | position | dept | email | phone
            elif line.startswith('[CONTACT]'):
                line = line.replace('[CONTACT]', '').strip()
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 1 and org_id:
                    name = parts[0]
                    position = parts[1] if len(parts) > 1 else ''
                    dept = parts[2] if len(parts) > 2 else ''
                    email = parts[3] if len(parts) > 3 else ''
                    phone = parts[4] if len(parts) > 4 else ''
                    add_contact(org_id, name, position=position, department=dept, email=email, phone=phone)
                    results['contacts'] += 1
                    continue
        
        except Exception as e:
            results['errors'].append(f"Line {i}: {str(e)[:50]}")
    
    return results

def format_department_info(dept, org_id):
    """Format thông tin phòng ban để hiển thị"""
    text = f"🏛️ **{dept['name']}**\n\n"
    
    if dept.get('description'):
        text += f"📝 Mô tả: {dept['description']}\n"
    
    if dept.get('manager'):
        text += f"👤 Trưởng phòng: {dept['manager']}\n"
    
    if dept.get('email'):
        text += f"📧 Email: {dept['email']}\n"
    
    if dept.get('phone'):
        text += f"☎️ Phone: {dept['phone']}\n"
    
    # Count members
    member_count = len(dept.get('members', []))
    text += f"\n👥 Số nhân viên: {member_count}"
    
    return text

def format_contact_info(contact):
    """Format thông tin contact để hiển thị"""
    text = f"👤 **{contact['name']}**\n\n"
    
    if contact.get('position'):
        text += f"📋 Chức vụ: {contact['position']}\n"
    
    if contact.get('department'):
        text += f"🏛️ Phòng ban: {contact['department']}\n"
    
    if contact.get('email'):
        text += f"📧 Email: {contact['email']}\n"
    
    if contact.get('phone'):
        text += f"☎️ Phone: {contact['phone']}\n"
    
    if contact.get('extension'):
        text += f"📞 Ext: {contact['extension']}\n"
    
    if contact.get('skills'):
        skills_str = ', '.join(contact['skills'][:5])
        text += f"\n🔧 Skills: {skills_str}"
    
    if contact.get('notes'):
        text += f"\n💡 Ghi chú: {contact['notes'][:100]}"
    
    return text

def get_enhanced_ai_response(user_id, user_message, org_id=None):
    """Enhanced AI response with department & contact search"""
    
    # 1. Tìm trong knowledge base VÀ web sources (passive learning)
    # Gọi get_ai_response() đã có logic đầy đủ cho KB cache + web sources on-demand
    ai_answer = get_ai_response(user_id, user_message)
    if ai_answer:
        return ai_answer
    
    # 2. Tìm department nếu có org
    if org_id:
        # Detect department queries
        dept_keywords = ['phòng', 'ban', 'department', 'dept', 'phụ trách', 'quản lý']
        if any(kw in user_message.lower() for kw in dept_keywords):
            dept = search_department(org_id, user_message)
            if dept:
                return format_department_info(dept, org_id) + "\n\n_[Từ dữ liệu doanh nghiệp]_"
        
        # Detect contact queries
        contact_keywords = ['ai là', 'liên hệ', 'contact', 'email', 'phone', 'số', 'gọi', 'tìm người']
        if any(kw in user_message.lower() for kw in contact_keywords):
            results = search_contact(org_id, user_message)
            if results:
                if len(results) == 1:
                    return format_contact_info(results[0]) + "\n\n_[Từ danh bạ]_"
                else:
                    # Multiple results
                    text = f"👥 **Tìm thấy {len(results)} người:**\n\n"
                    for i, contact in enumerate(results[:3], 1):
                        text += f"{i}. {contact['name']}"
                        if contact.get('position'):
                            text += f" - {contact['position']}"
                        text += "\n"
                    return text + "\n_[Từ danh bạ]_"
    
    # 3. Use AI
    if GITHUB_TOKEN:
        context = ""
        
        # Add KB context
        if user_id in ai_knowledge_base and ai_knowledge_base[user_id]:
            context += "Dữ liệu đã biết:\n"
            for item in ai_knowledge_base[user_id][-5:]:
                context += f"- Q: {item['question']}\n  A: {item['answer']}\n"
        
        # Add org context
        if org_id:
            org = organizations.get(org_id)
            if org:
                context += f"\nTổ chức: {org['name']}\n"
            
            dept_count = len(departments.get(org_id, []))
            contact_count = len(contacts.get(org_id, []))
            if dept_count > 0:
                context += f"- Có {dept_count} phòng ban\n"
            if contact_count > 0:
                context += f"- Có {contact_count} nhân viên\n"
        
        system_prompt = f"""Bạn là trợ lý doanh nghiệp thông minh.
{context}
Trả lời ngắn gọn, súc tích bằng tiếng Việt.
Nếu không biết chắc chắn, đề xuất cách tìm kiếm hoặc thêm dữ liệu."""
        
        ai_response = call_github_ai(user_message, system_prompt)
        if ai_response:
            return f"🤖 {ai_response}\n\n_[Từ AI]_"
    
    return None

def show_organization_menu(user_id):
    """Hiển thị menu quản lý organization"""
    org_id = get_active_org(user_id)
    
    if not org_id:
        text = (
            "🏢 **QUẢN LÝ DOANH NGHIỆP**\n\n"
            "📊 Bạn chưa có organization nào.\n\n"
            "💡 Tạo organization để:\n"
            "   • Quản lý phòng ban\n"
            "   • Lưu danh bạ nhân viên\n"
            "   • Import dữ liệu hàng loạt\n"
            "   • AI tự động tìm kiếm\n\n"
            "🎯 Bắt đầu ngay:"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_create = types.InlineKeyboardButton("➕ Tạo Organization", callback_data="org_create")
        markup.add(btn_create)
    else:
        org = organizations[org_id]
        dept_count = len(departments.get(org_id, []))
        contact_count = len(contacts.get(org_id, []))
        web_count = len(web_sources.get(org_id, []))
        
        text = (
            f"🏢 **{org['name']}**\n\n"
            f"📊 Thống kê:\n"
            f"   • 🏛️ Phòng ban: {dept_count}\n"
            f"   • 👥 Nhân viên: {contact_count}\n"
            f"   • 🌐 Nguồn web: {web_count}\n"
            f"   • 👤 Members: {len(org['members'])}\n\n"
            "🎯 Quản lý:"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn_dept = types.InlineKeyboardButton("🏛️ Phòng Ban", callback_data="org_departments")
        btn_contacts = types.InlineKeyboardButton("👥 Nhân Viên", callback_data="org_contacts")
        markup.add(btn_dept, btn_contacts)
        
        btn_import = types.InlineKeyboardButton("📥 Import Dữ Liệu", callback_data="org_import")
        btn_web = types.InlineKeyboardButton("🌐 Nguồn Web", callback_data="org_web_sources")
        markup.add(btn_import, btn_web)
        
        btn_settings = types.InlineKeyboardButton("⚙️ Cài Đặt", callback_data="org_settings")
        markup.add(btn_settings)
    
    btn_back = types.InlineKeyboardButton("🔙 Menu Chính", callback_data="menu_main")
    markup.add(btn_back)
    
    return text, markup

# ============= END ENTERPRISE FUNCTIONS =============

# Lệnh /delete để xóa một task
@bot.message_handler(commands=['delete'])
def delete_task(message):
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đang trống!")
        return
    
    try:
        task_number = int(message.text.split()[1])
        if 1 <= task_number <= len(user_tasks[user_id]):
            deleted_task = user_tasks[user_id].pop(task_number - 1)
            bot.reply_to(message, f"🗑️ Đã xóa công việc: '{deleted_task['content']}'")
        else:
            bot.reply_to(message, f"⚠️ Số thứ tự không hợp lệ. Vui lòng chọn từ 1 đến {len(user_tasks[user_id])}")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Vui lòng nhập số thứ tự công việc.\n\nVí dụ: /delete 1")

# Lệnh /clear để xóa danh sách
@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    user_id = get_user_id(message)
    update_user_chat_mapping(message)
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.reply_to(message, "📭 Danh sách công việc của bạn đã trống!")
        return
        
    # Tạo inline keyboard để xác nhận
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Có", callback_data="clear_yes"),
        types.InlineKeyboardButton("❌ Không", callback_data="clear_no")
    )
    bot.reply_to(message, "⚠️ Bạn có chắc chắn muốn xóa toàn bộ danh sách công việc?", reply_markup=markup)

# Lệnh /cancel để hủy thao tác đang làm
@bot.message_handler(commands=['cancel'])
def cancel_action(message):
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    if user_id in user_states and user_states[user_id]:
        old_state = user_states[user_id]
        user_states[user_id] = None
        
        # Hiển thị menu hoặc task list tùy theo state
        if old_state.startswith("selecting_remind_") or old_state.startswith("manual_"):
            text, markup = show_main_menu(user_id, "❌ Đã hủy đặt nhắc nhở")
            bot.send_message(chat_id, text, reply_markup=markup)
        else:
            text, markup = show_main_menu(user_id, "❌ Đã hủy thao tác")
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.reply_to(message, "Không có thao tác nào đang thực hiện.")

# Xử lý callback từ inline keyboard
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    print(f"Received callback: {call.data} from chat_id: {chat_id}, user_id: {user_id}")
    
    # Cập nhật mapping với đầy đủ thông tin
    user_chat_mapping[user_id] = {
        'chat_id': chat_id,
        'username': call.from_user.username or '',
        'first_name': call.from_user.first_name or '',
        'last_name': call.from_user.last_name or ''
    }
    
    # Menu chính
    if call.data == "menu_main":
        # Clear state nếu đang trong bất kỳ input state nào
        if user_id in user_states:
            user_states[user_id] = None
        
        text, markup = show_main_menu(user_id)
        try:
            # Thử edit message hiện tại
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            # Nếu không edit được (ví dụ: message là document), gửi message mới
            print(f"Cannot edit message, sending new one: {e}")
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Thêm công việc
    elif call.data == "menu_add":
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_main")
        markup.add(btn_cancel)
        
        user_states[user_id] = "waiting_task_content"
        bot.edit_message_text(
            "✍️ Nhập nội dung công việc:\n\n"
            "(Ví dụ: Họp team lúc 9h sáng)\n\n"
            "💡 Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    # Thêm công việc với AI Agent
    elif call.data == "menu_smart_add":
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_main")
        markup.add(btn_cancel)
        
        user_states[user_id] = "ai_collecting_task"
        ai_conversation_context[user_id] = {'task': {}, 'state': 'collecting', 'last_update': datetime.now()}
        
        # Hỏi trực tiếp tên công việc
        help_msg = "📝 Bạn muốn tạo công việc gì? Vui lòng cho tôi biết tên công việc nhé!"
        
        bot.edit_message_text(
            help_msg,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    # Xem danh sách
    elif call.data == "menu_list":
        # Clear state nếu đang trong bất kỳ input state nào
        if user_id in user_states:
            user_states[user_id] = None
        
        if user_id not in user_tasks or not user_tasks[user_id]:
            markup = types.InlineKeyboardMarkup()
            btn_add = types.InlineKeyboardButton("➕ Thêm công việc đầu tiên", callback_data="menu_add")
            btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_main")
            markup.add(btn_add)
            markup.add(btn_back)
            bot.edit_message_text(
                "📭 Danh sách công việc của bạn đang trống!",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            show_task_list(user_id, chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    # Đặt múi giờ
    elif call.data == "menu_timezone":
        current_tz = get_user_timezone(user_id)
        markup = types.InlineKeyboardMarkup(row_width=3)
        
        # Các nút timezone
        for code in ['VN', 'TH', 'SG', 'JP', 'KR', 'CN']:
            offset = TIMEZONES[code]
            btn = types.InlineKeyboardButton(
                f"{code} (GMT+{offset})",
                callback_data=f"tz_{code}"
            )
            markup.add(btn)
        
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_main")
        markup.add(btn_back)
        
        bot.edit_message_text(
            f"🌍 Múi giờ hiện tại: GMT+{current_tz}\n\n"
            f"Chọn múi giờ của bạn:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    # Xử lý chọn timezone
    elif call.data.startswith("tz_"):
        tz_code = call.data[3:]
        if tz_code in TIMEZONES:
            user_timezones[user_id] = TIMEZONES[tz_code]
            bot.answer_callback_query(call.id, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_code]}")
            text, markup = show_main_menu(user_id, f"✅ Đã đặt múi giờ: GMT+{TIMEZONES[tz_code]}")
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
    
    # Hướng dẫn
    elif call.data == "menu_help":
        help_text = (
            "📚 **HƯỚNG DẪN SỬ DỤNG BOT**\n\n"
            "🎯 **SỬ DỤNG MENU:**\n"
            "• Nhấn các nút trên menu để thao tác nhanh\n"
            "• Không cần gõ lệnh phức tạp\n"
            "• Menu được chia thành các danh mục dễ tìm\n\n"
            "📋 **QUẢN LÝ TASK:**\n"
            "• Thêm, xem, sửa, xóa tasks\n"
            "• Đặt nhắc nhở cho từng task\n"
            "• Chọn ngày giờ bằng lịch\n\n"
            "🎤 **CÔNG CỤ VOICE:**\n"
            "• Gửi voice message → Nhận file .txt\n"
            "• Hỗ trợ tiếng Việt & English\n"
            "• Sử dụng OpenAI Whisper\n\n"
            "🤖 **TRỢ LÝ AI:**\n"
            "• Tạo task bằng ngôn ngữ tự nhiên\n"
            "• AI phân tích và tạo nhắc nhở tự động\n"
            "• Cần GitHub Token (miễn phí)\n\n"
            "⏰ **ĐỊNH DẠNG THỜI GIAN:**\n"
            "• 14:30 - Hôm nay lúc 14:30\n"
            "• 2m, 30m, 2h - Sau 2 phút, 30 phút, 2 giờ\n"
            "• Hoặc dùng lịch chọn ngày giờ\n\n"
            "🌍 **MÚI GIỜ:**\n"
            "• Vào Cài Đặt → Đổi múi giờ\n"
            "• Thời gian hiển thị theo múi giờ của bạn\n\n"
            "💡 **MẸO:**\n"
            "• Thêm Nhanh: Thêm task nhanh từ menu chính\n"
            "• Voice: Ghi âm cuộc họp → Chuyển thành văn bản\n"
            "• AI: Nói tự nhiên, AI tạo task cho bạn"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.add(btn_back)
        bot.edit_message_text(help_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== CATEGORY MENUS =====
    
    # Task Management Category
    elif call.data == "category_tasks":
        text, markup = show_tasks_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Voice Tools Category
    elif call.data == "category_voice":
        text, markup = show_voice_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # AI Assistant Category
    elif call.data == "category_ai":
        text, markup = show_ai_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Settings Category
    elif call.data == "category_settings":
        text, markup = show_settings_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== ENTERPRISE CATEGORY =====
    
    elif call.data == "category_enterprise":
        text, markup = show_organization_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Organization - Create
    elif call.data == "org_create":
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="category_enterprise")
        markup.add(btn_cancel)
        
        user_states[user_id] = "waiting_org_name"
        bot.edit_message_text(
            "🏢 **TẠO ORGANIZATION**\n\n"
            "✍️ Nhập tên công ty/tổ chức:\n\n"
            "(Ví dụ: ABC Corporation, Công Ty XYZ)\n\n"
            "💡 Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Organization - Departments Menu
    elif call.data == "org_departments":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        dept_list = departments.get(org_id, [])
        text = f"🏛️ **QUẢN LÝ PHÒNG BAN**\n\n"
        text += f"📊 Tổng số: {len(dept_list)} phòng ban\n\n"
        
        if dept_list:
            text += "📋 Danh sách:\n"
            for i, dept in enumerate(dept_list, 1):
                text += f"{i}. {dept['name']}"
                if dept.get('manager'):
                    text += f" - {dept['manager']}"
                text += "\n"
        else:
            text += "💡 Chưa có phòng ban nào.\n"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_add = types.InlineKeyboardButton("➕ Thêm Phòng Ban", callback_data="dept_add")
        markup.add(btn_add)
        
        if dept_list:
            btn_list = types.InlineKeyboardButton("🔍 Tìm Phòng Ban", callback_data="dept_search")
            markup.add(btn_list)
        
        btn_back = types.InlineKeyboardButton("🔙 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Department - Add
    elif call.data == "dept_add":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_departments")
        markup.add(btn_cancel)
        
        user_states[user_id] = "waiting_dept_name"
        bot.edit_message_text(
            "🏛️ **THÊM PHÒNG BAN**\n\n"
            "✍️ Nhập tên phòng ban:\n\n"
            "(Ví dụ: Phòng Kỹ Thuật, Phòng Kinh Doanh)\n\n"
            "💡 Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Organization - Contacts Menu
    elif call.data == "org_contacts":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        contact_list = contacts.get(org_id, [])
        text = f"👥 **DANH BẠ NHÂN VIÊN**\n\n"
        text += f"📊 Tổng số: {len(contact_list)} người\n\n"
        
        if contact_list:
            text += "📋 Danh sách (10 người gần nhất):\n"
            for i, contact in enumerate(contact_list[-10:], 1):
                text += f"{i}. {contact['name']}"
                if contact.get('position'):
                    text += f" - {contact['position']}"
                text += "\n"
        else:
            text += "💡 Chưa có nhân viên nào.\n"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_add = types.InlineKeyboardButton("➕ Thêm Nhân Viên", callback_data="contact_add")
        markup.add(btn_add)
        
        if contact_list:
            btn_search = types.InlineKeyboardButton("🔍 Tìm Người", callback_data="contact_search")
            btn_list = types.InlineKeyboardButton("📋 Xem Tất Cả", callback_data="contact_list_all")
            markup.add(btn_search, btn_list)
        
        btn_back = types.InlineKeyboardButton("🔙 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Contact - Add
    elif call.data == "contact_add":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_contacts")
        markup.add(btn_cancel)
        
        user_states[user_id] = "waiting_contact_name"
        bot.edit_message_text(
            "👤 **THÊM NHÂN VIÊN**\n\n"
            "✍️ Nhập tên nhân viên:\n\n"
            "(Ví dụ: Nguyễn Văn A)\n\n"
            "💡 Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Organization - Web Sources Menu
    elif call.data == "org_web_sources":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        web_list = web_sources.get(org_id, [])
        text = f"🌐 **NGUỒN WEB (HỌC BỊ ĐỘNG)**\n\n"
        text += f"📊 Tổng số: {len(web_list)} nguồn\n\n"
        
        if web_list:
            text += "📋 Danh sách:\n"
            for i, source in enumerate(web_list, 1):
                source_type = source.get('type', 'N/A')
                text += f"{i}. {source.get('url', 'N/A')[:50]}\n"
                text += f"   📄 {source.get('title', 'N/A')[:40]}\n"
                text += f"   📅 {source.get('added_at', 'N/A')[:10]}\n"
                text += f"   📊 {source.get('content_length', 0):,} ký tự\n\n"
        else:
            text += "💡 Chưa thêm nguồn web nào.\n\n"
        
        text += "🤖 **Học bị động:**\n"
        text += "   • AI chưa extract Q&A ngay\n"
        text += "   • Chỉ extract khi bạn hỏi\n"
        text += "   • Tiết kiệm bộ nhớ và nhanh hơn!"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_add = types.InlineKeyboardButton("➕ Thêm Nguồn Web", callback_data="import_web")
        markup.add(btn_add)
        
        btn_back = types.InlineKeyboardButton("🔙 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Organization - Import Menu
    elif call.data == "org_import":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        text = (
            "📥 **IMPORT DỮ LIỆU HÀNG LOẠT**\n\n"
            "💡 Hỗ trợ:\n"
            "   • File TXT (Q&A, Departments, Contacts)\n"
            "   • Copy/Paste text trực tiếp\n"
            "   • Web scraping (URL)\n\n"
            "📝 Format:\n"
            "```\n"
            "# Q&A\n"
            "Câu hỏi? | Câu trả lời\n\n"
            "# Phòng ban\n"
            "[DEPT] Tên phòng | Trưởng phòng | Email\n\n"
            "# Nhân viên\n"
            "[CONTACT] Tên | Chức vụ | Phòng | Email | Phone\n"
            "```\n\n"
            "🎯 Chọn nguồn:"
        )
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_text = types.InlineKeyboardButton("📋 Paste Text", callback_data="import_text")
        btn_web = types.InlineKeyboardButton("🌐 Scrape Website", callback_data="import_web")
        markup.add(btn_text, btn_web)
        
        btn_back = types.InlineKeyboardButton("🔙 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Import - Text
    elif call.data == "import_text":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_import")
        markup.add(btn_cancel)
        
        user_states[user_id] = "waiting_import_text"
        bot.edit_message_text(
            "📋 **IMPORT TỪ TEXT**\n\n"
            "Paste nội dung theo format:\n\n"
            "```\n"
            "Câu hỏi 1? | Câu trả lời 1\n"
            "Câu hỏi 2? | Câu trả lời 2\n\n"
            "[DEPT] Phòng Kỹ Thuật | Nguyễn A | tech@co.com\n\n"
            "[CONTACT] Trần B | Dev | Kỹ Thuật | b@co.com | 0901234567\n"
            "```\n\n"
            "💡 Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Import - Web
    elif call.data == "import_web":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.answer_callback_query(call.id, "⚠️ Chưa có organization!", show_alert=True)
            return
        
        if not ENTERPRISE_ENABLED:
            bot.answer_callback_query(call.id, "⚠️ Cần cài: pip install beautifulsoup4", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_import")
        markup.add(btn_cancel)
        
        user_states[user_id] = "waiting_import_url"
        bot.edit_message_text(
            "🌐 **THÊM NGUỒN WEB (HỌC BỊ ĐỘNG)**\n\n"
            "✍️ Nhập URL website:\n\n"
            "(Ví dụ: https://company.com/about)\n\n"
            "🤖 AI sẽ:\n"
            "   ✅ Tải và lưu nội dung trang\n"
            "   ✅ KHÔNG trích xuất Q&A ngay\n"
            "   ✅ Chỉ extract khi bạn hỏi\n\n"
            "💡 Học bị động = Tiết kiệm bộ nhớ!\n\n"
            "Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Cancel web scraping and return to menu
    elif call.data == "scrape_cancel":
        user_states[user_id] = None
        scraping_cancelled[user_id] = True  # Mark as cancelled
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Import Menu", callback_data="org_import")
        markup.add(btn_back)
        
        try:
            bot.edit_message_text(
                "❌ Đã hủy tải website\n\n"
                "Bạn có thể thử lại sau.",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except:
            pass
        bot.answer_callback_query(call.id, "Đã hủy")
    
    # Scrape Confirmation - YES (HỌC BỊ ĐỘNG)
    elif call.data == "scrape_confirm_yes":
        # Retrieve temporary scraped data
        if not hasattr(user_states, '_temp_scraped_data') or user_id not in user_states._temp_scraped_data:
            bot.answer_callback_query(call.id, "⚠️ Dữ liệu đã hết hạn. Thử lại!", show_alert=True)
            return
        
        temp_data = user_states._temp_scraped_data[user_id]
        url = temp_data['url']
        data = temp_data['data']
        org_id = temp_data['org_id']
        
        # LƯU NGUỒN WEB (không extract Q&A ngay)
        if org_id not in web_sources:
            web_sources[org_id] = []
        
        web_sources[org_id].append({
            'id': generate_id('source'),
            'url': url,
            'title': data.get('title', 'Untitled'),
            'description': data.get('description', ''),
            'raw_content': data.get('raw_content', ''),  # Lưu raw content
            'content_length': data.get('content_length', 0),
            'type': 'web_passive',  # Học bị động
            'added_at': datetime.utcnow().isoformat(),
            'status': 'ready',
            'added_by': user_id
        })
        save_data()
        
        # Clean up
        del user_states._temp_scraped_data[user_id]
        user_states[user_id] = None
        
        # Success message
        result_text = f"✅ **ĐÃ THÊM NGUỒN WEB (HỌC BỊ ĐỘNG)**\n\n"
        result_text += f"🌐 URL: {url[:60]}\n"
        result_text += f"📄 Title: {data.get('title', 'N/A')[:60]}\n"
        result_text += f"📊 Nội dung: {data.get('content_length', 0):,} ký tự\n\n"
        
        result_text += f"🤖 **Học bị động:**\n"
        result_text += f"   ✅ Nguồn đã sẵn sàng\n"
        result_text += f"   ✅ AI sẽ tìm khi bạn hỏi\n"
        result_text += f"   ✅ Trích xuất on-demand\n\n"
        
        result_text += f"💡 **Cách sử dụng:**\n"
        result_text += f"1. Click **💬 Chat với AI** bên dưới\n"
        result_text += f"2. Click **⚡ Bật/Tắt AI Chat**\n"
        result_text += f"3. Gửi câu hỏi liên quan đến nguồn này\n"
        result_text += f"4. AI sẽ tự động tìm và trả lời!"
        
        markup = types.InlineKeyboardMarkup()
        btn_chat = types.InlineKeyboardButton("💬 Chat với AI", callback_data="category_ai")
        btn_more = types.InlineKeyboardButton("🌐 Thêm nguồn khác", callback_data="import_web")
        btn_menu = types.InlineKeyboardButton("🏠 Menu", callback_data="category_enterprise")
        markup.add(btn_chat)
        markup.add(btn_more, btn_menu)
        
        bot.edit_message_text(
            result_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "✅ Đã thêm nguồn web!")
    
    # Scrape Confirmation - NO
    elif call.data == "scrape_confirm_no":
        # Clean up temporary data
        if hasattr(user_states, '_temp_scraped_data') and user_id in user_states._temp_scraped_data:
            del user_states._temp_scraped_data[user_id]
        
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_retry = types.InlineKeyboardButton("🔄 Scrape Lại", callback_data="import_web")
        btn_menu = types.InlineKeyboardButton("🏠 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_retry, btn_menu)
        
        bot.edit_message_text(
            "❌ **ĐÃ HỦY**\n\n"
            "Nguồn web không được thêm vào doanh nghiệp.\n\n"
            "💡 Bạn có thể thêm URL khác hoặc quay lại menu.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "❌ Đã hủy")
    
    # Import Text Confirmation - YES
    elif call.data == "import_confirm_yes":
        # Retrieve temporary import data
        if not hasattr(user_states, '_temp_import_data') or user_id not in user_states._temp_import_data:
            bot.answer_callback_query(call.id, "⚠️ Dữ liệu đã hết hạn. Thử lại!", show_alert=True)
            return
        
        temp_data = user_states._temp_import_data[user_id]
        qa_pairs = temp_data['qa_pairs']
        results = temp_data['results']
        
        # Add Q&A to user's KB with metadata
        for qa in qa_pairs:
            add_to_knowledge_base(
                user_id, 
                qa['question'], 
                qa['answer'],
                source='text_import',
                metadata={'imported_at': datetime.utcnow().isoformat()}
            )
        
        save_data()
        
        # Clean up
        del user_states._temp_import_data[user_id]
        user_states[user_id] = None
        
        # Format results
        result_text = "✅ **ĐÃ LƯU VÀO KNOWLEDGE BASE**\n\n"
        result_text += f"📚 Q&A: {results['qa_pairs']}\n"
        result_text += f"🏛️ Phòng ban: {results['departments']}\n"
        result_text += f"👥 Nhân viên: {results['contacts']}\n\n"
        result_text += f"💡 AI có thể trả lời các câu hỏi từ dữ liệu này!"
        
        if results['errors']:
            result_text += f"\n\n⚠️ Lỗi: {len(results['errors'])} dòng"
        
        markup = types.InlineKeyboardMarkup()
        btn_import = types.InlineKeyboardButton("📥 Import Thêm", callback_data="org_import")
        btn_menu = types.InlineKeyboardButton("🏠 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_import, btn_menu)
        
        bot.edit_message_text(
            result_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "✅ Đã lưu vào KB!")
    
    # Import Text Confirmation - NO
    elif call.data == "import_confirm_no":
        # Clean up temporary data
        if hasattr(user_states, '_temp_import_data') and user_id in user_states._temp_import_data:
            del user_states._temp_import_data[user_id]
        
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_retry = types.InlineKeyboardButton("🔄 Import Lại", callback_data="import_text")
        btn_menu = types.InlineKeyboardButton("🏠 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_retry, btn_menu)
        
        bot.edit_message_text(
            "❌ **ĐÃ HỦY**\n\n"
            "Dữ liệu không được thêm vào Knowledge Base.\n\n"
            "💡 Bạn có thể import lại hoặc quay lại menu.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "❌ Đã hủy")
    
    # ===== END ENTERPRISE CALLBACKS =====
    
    # ===== TASKS SUBMENU =====
    
    elif call.data == "tasks_pending":
        pending_tasks = [t for t in user_tasks.get(user_id, []) if not t.get('done', False)]
        if not pending_tasks:
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(
                "✅ Không có task nào đang làm!\n\nTất cả đã hoàn thành!",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            text = f"⏳ **TASKS ĐANG LÀM** ({len(pending_tasks)})\n\n"
            for i, task in enumerate(pending_tasks, 1):
                text += f"{i}. {task['content']}\n"
                if task.get('remind_time'):
                    remind_local = get_user_time(user_id, task['remind_time'])
                    text += f"   🕐 {remind_local.strftime('%d/%m %H:%M')}\n"
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "tasks_completed":
        completed_tasks = [t for t in user_tasks.get(user_id, []) if t.get('done', False)]
        if not completed_tasks:
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(
                "📭 Chưa có task nào hoàn thành!",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            text = f"✅ **TASKS ĐÃ HOÀN THÀNH** ({len(completed_tasks)})\n\n"
            for i, task in enumerate(completed_tasks, 1):
                text += f"{i}. ~~{task['content']}~~\n"
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quản Lý Task", callback_data="category_tasks")
            markup.add(btn_back)
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== VOICE SUBMENU =====
    
    elif call.data == "voice_guide":
        guide_text = (
            "📖 **HƯỚNG DẪN CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN**\n\n"
            "🎯 **Cách sử dụng:**\n"
            "1. Nhấn giữ icon micro 🎤 trong Telegram\n"
            "2. Nói nội dung (tiếng Việt hoặc English)\n"
            "3. Thả tay để gửi\n"
            "4. Đợi 2-8 giây\n"
            "5. Nhận file .txt với nội dung đã chuyển đổi\n\n"
            "⚙️ **Cài đặt (lần đầu):**\n"
            "• Cần OpenAI API key\n"
            "• Xem: VOICE_QUICK_SETUP.md\n"
            "• Chi phí: ~150 VND/phút\n\n"
            "🔒 **Riêng tư:**\n"
            "• File txt luôn gửi về chat riêng\n"
            "• Thành viên khác không thấy nội dung\n"
            "• Mỗi user có dữ liệu riêng biệt\n\n"
            "💡 **Mẹo:**\n"
            "• Nói rõ ràng, không quá nhanh\n"
            "• Môi trường yên tĩnh → Độ chính xác cao\n"
            "• Hỗ trợ voice dài (cả phút)"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Công Cụ Voice", callback_data="category_voice")
        markup.add(btn_back)
        bot.edit_message_text(guide_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "voice_demo":
        demo_text = (
            "🎬 **DEMO: CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN**\n\n"
            "📝 **Ví dụ 1: Ghi chú cuộc họp**\n"
            "Voice: \"Cuộc họp ngày mai lúc 9 giờ sáng, thảo luận về dự án X\"\n"
            "→ File txt: Nội dung đầy đủ được chuyển đổi\n\n"
            "📝 **Ví dụ 2: Danh sách việc cần làm**\n"
            "Voice: \"Nhớ mua sữa, trứng, bánh mì khi về nhà\"\n"
            "→ File txt: Danh sách mua sắm\n\n"
            "📝 **Ví dụ 3: Phỏng vấn**\n"
            "Voice: [5 phút phỏng vấn]\n"
            "→ File txt: Bản ghi hoàn chỉnh\n\n"
            "🎯 **Thử ngay:**\n"
            "Gửi voice message cho bot để test!"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Công Cụ Voice", callback_data="category_voice")
        markup.add(btn_back)
        bot.edit_message_text(demo_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== AI SUBMENU =====
    
    elif call.data == "ai_natural_language":
        if not GITHUB_TOKEN:
            bot.answer_callback_query(call.id, "❌ Chưa cấu hình GitHub Token!", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="category_ai")
        markup.add(btn_cancel)
        
        bot.edit_message_text(
            "💬 **TẠO TASK BẰNG NGÔN NGỮ TỰ NHIÊN**\n\n"
            "Nhập nội dung task theo cách tự nhiên, AI sẽ phân tích và tạo task + nhắc nhở cho bạn.\n\n"
            "📝 Ví dụ:\n"
            "• \"Họp team lúc 2 giờ chiều mai\"\n"
            "• \"Nhắc tôi mua sữa sau 30 phút\"\n"
            "• \"Deadline dự án X ngày 30/7\"\n\n"
            "✍️ Nhập nội dung:\n\n"
            "💡 Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        user_states[user_id] = "waiting_task_content"
        bot.answer_callback_query(call.id)
    
    elif call.data == "ai_setup_github":
        setup_text = (
            "🔑 **CÀI ĐẶT GITHUB AI**\n\n"
            "GitHub Models API hoàn toàn **MIỄN PHÍ** và rất mạnh!\n\n"
            "📝 **Cách cài đặt:**\n"
            "1. Truy cập: github.com/settings/tokens\n"
            "2. Tạo token mới (classic)\n"
            "3. Chọn scopes: repo, read:user\n"
            "4. Copy token\n"
            "5. Thêm vào .env: GITHUB_TOKEN=your_token\n"
            "6. Khởi động lại bot\n\n"
            "📖 **Xem hướng dẫn chi tiết:**\n"
            "→ AI_SETUP.md trong repository\n\n"
            "✨ **Tính năng khi có GitHub AI:**\n"
            "• Tạo task từ ngôn ngữ tự nhiên\n"
            "• Tự động phân tích thời gian\n"
            "• Gợi ý thông minh"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Trợ Lý AI", callback_data="category_ai")
        markup.add(btn_back)
        bot.edit_message_text(setup_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "ai_upcoming":
        upcoming_text = (
            "🚀 **TÍNH NĂNG SẮP CÓ**\n\n"
            "📊 **Phân Tích Task Thông Minh:**\n"
            "• AI phân tích mô hình năng suất\n"
            "• Gợi ý thời gian làm việc tốt nhất\n"
            "• Ước lượng thời gian hoàn thành\n\n"
            "🔮 **Gợi Ý Từ AI:**\n"
            "• Gợi ý task dựa trên lịch sử\n"
            "• Tự động phân loại tasks\n"
            "• Đề xuất độ ưu tiên\n\n"
            "🎯 **Nhắc Nhở Thông Minh:**\n"
            "• Thông báo theo ngữ cảnh\n"
            "• Tự điều chỉnh thời gian nhắc\n"
            "• Nhắc nhở theo vị trí\n\n"
            "🤝 **Cộng Tác Nhóm:**\n"
            "• Chia sẻ tasks trong nhóm\n"
            "• Phân công công việc\n"
            "• Theo dõi tiến độ\n\n"
            "⏰ **Ra mắt:** Q4 2026\n"
            "💡 **Đề xuất tính năng?** Liên hệ admin!"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Trợ Lý AI", callback_data="category_ai")
        markup.add(btn_back)
        bot.edit_message_text(upcoming_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # ===== AI CHAT & KNOWLEDGE BASE =====
    
    elif call.data == "ai_chat_toggle":
        # Bật/tắt chế độ AI chat
        current_mode = user_ai_chat_mode.get(user_id, False)
        user_ai_chat_mode[user_id] = not current_mode
        
        if user_ai_chat_mode[user_id]:
            msg = "✅ Đã bật AI Chat! Bot sẽ tự động trả lời tin nhắn của bạn."
        else:
            msg = "⏸️ Đã tắt AI Chat. Bot chỉ phản hồi commands."
        
        bot.answer_callback_query(call.id, msg, show_alert=True)
        
        # Cập nhật menu
        text, markup = show_ai_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    
    elif call.data == "ai_knowledge_menu":
        text, markup = show_knowledge_menu(user_id)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "kb_add":
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="ai_knowledge_menu")
        markup.add(btn_cancel)
        
        bot.edit_message_text(
            "📚 **THÊM DỮ LIỆU Q&A**\n\n"
            "Nhập câu hỏi mà bạn muốn AI học:\n\n"
            "Ví dụ: \"Địa chỉ văn phòng là gì?\"\n\n"
            "💡 Gõ /cancel để hủy",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        user_states[user_id] = "waiting_kb_question"
        bot.answer_callback_query(call.id)
    
    elif call.data == "kb_list":
        kb_items = ai_knowledge_base.get(user_id, [])
        if not kb_items:
            text = "📭 Chưa có dữ liệu nào!"
            markup = types.InlineKeyboardMarkup()
            btn_add = types.InlineKeyboardButton("➕ Thêm dữ liệu", callback_data="kb_add")
            btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="ai_knowledge_menu")
            markup.add(btn_add, btn_back)
        else:
            text = f"📚 **DỮ LIỆU AI ({len(kb_items)} cặp)**\n\n"
            for i, item in enumerate(kb_items[:10], 1):  # Hiển thị 10 cặp đầu
                text += f"{i}. **Q:** {item['question']}\n"
                text += f"   **A:** {item['answer'][:50]}{'...' if len(item['answer']) > 50 else ''}\n\n"
            
            if len(kb_items) > 10:
                text += f"_... và {len(kb_items) - 10} cặp khác_\n\n"
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            for i in range(min(len(kb_items), 5)):
                btn = types.InlineKeyboardButton(f"🗑️ Xóa #{i+1}", callback_data=f"kb_delete_{i}")
                markup.add(btn)
            
            btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="ai_knowledge_menu")
            markup.add(btn_back)
        
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("kb_delete_"):
        idx = int(call.data.split("_")[2])
        if user_id in ai_knowledge_base and idx < len(ai_knowledge_base[user_id]):
            deleted = ai_knowledge_base[user_id].pop(idx)
            bot.answer_callback_query(call.id, f"✅ Đã xóa: {deleted['question'][:30]}...")
            # Refresh list
            text, markup = show_knowledge_menu(user_id)
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, "❌ Không tìm thấy dữ liệu!", show_alert=True)
    
    elif call.data == "kb_clear_confirm":
        kb_count = len(ai_knowledge_base.get(user_id, []))
        text = (
            "⚠️ **XÁC NHẬN XÓA DỮ LIỆU AI**\n\n"
            f"Bạn có {kb_count} cặp Q&A.\n\n"
            "⚠️ **Không thể khôi phục!**\n\n"
            "Bạn chắc chắn?"
        )
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("🗑️ Có, xóa hết", callback_data="kb_clear_yes")
        btn_no = types.InlineKeyboardButton("❌ Không, giữ lại", callback_data="ai_knowledge_menu")
        btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.add(btn_yes, btn_no)
        markup.add(btn_back)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "kb_clear_yes":
        ai_knowledge_base[user_id] = []
        markup = types.InlineKeyboardMarkup()
        btn_kb = types.InlineKeyboardButton("📚 Quản lý Kiến Thức", callback_data="ai_knowledge_menu")
        btn_ai = types.InlineKeyboardButton("🤖 Menu AI", callback_data="category_ai")
        btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
        markup.add(btn_kb)
        markup.add(btn_ai, btn_menu)
        
        bot.edit_message_text(
            "✅ Đã xóa toàn bộ dữ liệu AI!\n\n"
            "📚 Bạn có thể thêm dữ liệu mới bất cứ lúc nào.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id, "✅ Đã xóa toàn bộ dữ liệu AI!")
    
    # ===== SETTINGS SUBMENU =====
    
    elif call.data == "settings_clear_confirm":
        text = (
            "⚠️ **XÁC NHẬN XÓA DỮ LIỆU**\n\n"
            f"Bạn có {len(user_tasks.get(user_id, []))} tasks.\n\n"
            "Xóa sẽ mất:\n"
            "• Tất cả tasks\n"
            "• Tất cả reminders\n"
            "• Cài đặt múi giờ (về mặc định)\n\n"
            "⚠️ **Không thể khôi phục!**\n\n"
            "Bạn chắc chắn?"
        )
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("🗑️ Có, xóa hết", callback_data="settings_clear_yes")
        btn_no = types.InlineKeyboardButton("❌ Không, giữ lại", callback_data="category_settings")
        markup.add(btn_yes, btn_no)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "settings_clear_yes":
        # Xóa tất cả dữ liệu của user
        user_tasks[user_id] = []
        user_timezones[user_id] = 7  # Reset về GMT+7
        user_states[user_id] = None
        
        text, markup = show_main_menu(user_id, "🗑️ Đã xóa toàn bộ dữ liệu!")
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id, "✅ Đã xóa toàn bộ dữ liệu!")
    
    elif call.data == "settings_about":
        about_text = (
            "ℹ️ **VỀ BOT**\n\n"
            "🤖 **Tên:** PHT Task Bot\n"
            "📦 **Phiên bản:** 2.0.0 (Đa Chức Năng)\n"
            "👨‍💻 **Phát triển bởi:** PHT Team\n"
            "📅 **Cập nhật:** 25/07/2026\n\n"
            "✨ **Tính năng chính:**\n"
            "• Quản lý công việc với nhắc nhở thông minh\n"
            "• Chuyển đổi giọng nói thành văn bản\n"
            "• Tạo task bằng AI\n"
            "• Hỗ trợ đa múi giờ\n"
            "• Thiết kế ưu tiên riêng tư\n\n"
            "🔗 **Liên kết:**\n"
            "• GitHub: github.com/rambo247/task_bot\n"
            "• Tài liệu: Repository README.md\n\n"
            "💡 **Công nghệ:**\n"
            "• Python 3.6+\n"
            "• pyTelegramBotAPI\n"
            "• OpenAI Whisper API\n"
            "• GitHub Models API"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Cài Đặt", callback_data="category_settings")
        markup.add(btn_back)
        bot.edit_message_text(about_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    elif call.data == "settings_stats":
        total_tasks = len(user_tasks.get(user_id, []))
        pending = sum(1 for t in user_tasks.get(user_id, []) if not t.get('done', False))
        completed = total_tasks - pending
        with_reminder = sum(1 for t in user_tasks.get(user_id, []) if t.get('remind_time'))
        
        stats_text = (
            f"📊 **THỐNG KÊ CỦA BẠN**\n\n"
            f"📋 **Tasks:**\n"
            f"   • Tổng: {total_tasks}\n"
            f"   • Đang làm: {pending}\n"
            f"   • Hoàn thành: {completed}\n"
            f"   • Có reminder: {with_reminder}\n\n"
            f"⚙️ **Cài đặt:**\n"
            f"   • Múi giờ: GMT+{get_user_timezone(user_id)}\n"
            f"   • GitHub AI: {'✅ Bật' if GITHUB_TOKEN else '❌ Tắt'}\n"
            f"   • OpenAI: {'✅ Bật' if OPENAI_API_KEY else '❌ Tắt'}\n\n"
            f"💪 **Tỷ Lệ Hoàn Thành:**\n"
            f"   {f'{completed}/{total_tasks} ({int(completed/total_tasks*100)}%)' if total_tasks > 0 else 'Chưa có dữ liệu'}"
        )
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Cài Đặt", callback_data="category_settings")
        markup.add(btn_back)
        bot.edit_message_text(stats_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    
    # Xử lý action cho từng task
    elif call.data.startswith("task_"):
        parts = call.data.split("_")
        action = parts[1]
        task_idx = int(parts[2])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")
            return
        
        if action == "done":
            user_tasks[user_id][task_idx]['done'] = True
            bot.answer_callback_query(call.id, "✅ Đã hoàn thành!")
            show_task_list(user_id, chat_id, call.message.message_id)
        
        elif action == "remind":
            user_states[user_id] = f"selecting_remind_date_{task_idx}"
            task_content = user_tasks[user_id][task_idx]['content']
            
            # Hiển thị calendar picker
            calendar_markup = create_calendar(user_id)
            bot.edit_message_text(
                f"📅 Chọn ngày nhắc nhở cho:\n'{task_content}'",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=calendar_markup
            )
            bot.answer_callback_query(call.id)
        
        elif action == "note":
            # Thêm ghi chú trực tiếp mà không cần cập nhật tiến độ
            task_content = user_tasks[user_id][task_idx]['content']
            current_progress = user_tasks[user_id][task_idx].get('progress_percent', 0)
            
            # Set state để nhận ghi chú
            user_states[user_id] = f"add_task_note_{task_idx}"
            
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
            markup.add(btn_cancel)
            
            bot.edit_message_text(
                f"💬 **THÊM GHI CHÚ**\n\n"
                f"Task: {task_content[:50]}\n"
                f"Tiến độ: {get_progress_bar(current_progress)}\n\n"
                f"✍️ Nhập nội dung ghi chú:\n"
                f"(Ghi chú sẽ được thêm vào lịch sử với tiến độ hiện tại)",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
        
        elif action == "progress":
            # Hiển thị menu chọn progress
            task_content = user_tasks[user_id][task_idx]['content']
            current_progress = user_tasks[user_id][task_idx].get('progress_percent', 0)
            
            markup = types.InlineKeyboardMarkup(row_width=3)
            
            # Progress options
            progress_options = [0, 25, 50, 75, 100]
            btn_row = []
            for progress in progress_options:
                label = f"{'✅ ' if progress == current_progress else ''}{progress}%"
                btn_row.append(types.InlineKeyboardButton(label, callback_data=f"set_progress_{task_idx}_{progress}"))
                if len(btn_row) == 3:
                    markup.row(*btn_row)
                    btn_row = []
            if btn_row:
                markup.row(*btn_row)
            
            # Nút nhập thủ công
            btn_manual = types.InlineKeyboardButton("✏️ Nhập thủ công (0-100%)", callback_data=f"manual_progress_{task_idx}")
            markup.add(btn_manual)
            
            # Back button
            btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_list")
            markup.add(btn_back)
            
            bot.edit_message_text(
                f"📊 **CẬP NHẬT TIẾN ĐỘ**\n\n"
                f"Task: {task_content[:50]}\n"
                f"Hiện tại: {get_progress_bar(current_progress)}\n\n"
                f"Chọn tiến độ mới:",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
        
        elif action == "delete":
            deleted_task = user_tasks[user_id].pop(task_idx)
            save_data()
            bot.answer_callback_query(call.id, f"🗑️ Đã xóa: {deleted_task['content']}")
            if user_tasks[user_id]:
                show_task_list(user_id, chat_id, call.message.message_id)
            else:
                text, markup = show_main_menu(user_id, "✅ Đã xóa task cuối cùng!")
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        
        elif action == "back":
            show_task_list(user_id, chat_id, call.message.message_id)
            bot.answer_callback_query(call.id)
    
    # Manual progress input
    elif call.data.startswith("manual_progress_"):
        parts = call.data.split("_")
        task_idx = int(parts[2])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")
            return
        
        # Set state to wait for manual progress input
        user_states[user_id] = f"manual_progress_input_{task_idx}"
        
        task_content = user_tasks[user_id][task_idx]['content']
        current_progress = user_tasks[user_id][task_idx].get('progress_percent', 0)
        
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_cancel)
        
        bot.edit_message_text(
            f"✏️ **NHẬP TIẾN ĐỘ THỦ CÔNG**\n\n"
            f"Task: {task_content[:50]}\n"
            f"Hiện tại: {get_progress_bar(current_progress)}\n\n"
            f"Nhập số phần trăm tiến độ (0-100):\n"
            f"Ví dụ: 95",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Set progress handlers
    elif call.data.startswith("set_progress_"):
        parts = call.data.split("_")
        task_idx = int(parts[2])
        progress = int(parts[3])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")
            return
        
        # Set state to ask for note
        user_states[user_id] = f"progress_note_{task_idx}_{progress}"
        
        task_content = user_tasks[user_id][task_idx]['content']
        markup = types.InlineKeyboardMarkup()
        btn_skip = types.InlineKeyboardButton("⏭️ Bỏ qua (không ghi chú)", callback_data=f"skip_progress_note_{task_idx}_{progress}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_skip)
        markup.add(btn_cancel)
        
        bot.edit_message_text(
            f"📝 **THÊM GHI CHÚ CẬP NHẬT**\n\n"
            f"Task: {task_content[:50]}\n"
            f"Đã hoàn thành: {progress}%\n\n"
            f"Nhập nội dung chi tiết về cập nhật này:\n"
            f"(Ví dụ: Đã hoàn thành phân tích requirements)",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Skip progress note
    elif call.data.startswith("skip_progress_note_"):
        parts = call.data.split("_")
        task_idx = int(parts[3])
        progress = int(parts[4])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")
            return
        
        # Update progress without note
        old_progress = user_tasks[user_id][task_idx].get('progress_percent', 0)
        user_tasks[user_id][task_idx]['progress_percent'] = progress
        
        # Initialize progress_updates if not exists
        if 'progress_updates' not in user_tasks[user_id][task_idx]:
            user_tasks[user_id][task_idx]['progress_updates'] = []
        
        # Add update record
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'progress': progress,
            'old_progress': old_progress,
            'note': None
        }
        user_tasks[user_id][task_idx]['progress_updates'].append(update_record)
        print(f"📝 [skip_progress_note callback] Added update: {old_progress}% → {progress}% (total: {len(user_tasks[user_id][task_idx]['progress_updates'])})")
        
        # Auto mark as done if 100%
        if progress == 100:
            user_tasks[user_id][task_idx]['done'] = True
            # Update status to "Hoàn thành" if it exists (for AI tasks)
            if 'status' in user_tasks[user_id][task_idx]:
                user_tasks[user_id][task_idx]['status'] = 'Hoàn thành'
        
        # Clear state
        user_states[user_id] = None
        
        save_data()
        bot.answer_callback_query(call.id, f"📊 Đã cập nhật: {progress}%")
        show_task_list(user_id, chat_id, call.message.message_id)
    
    # Share tasks handlers
    elif call.data == "share_start":
        # Start sharing mode
        show_task_list_for_sharing(user_id, chat_id, call.message.message_id, [])
        bot.answer_callback_query(call.id)
    
    elif call.data == "share_all":
        # Select all tasks
        all_indices = list(range(len(user_tasks.get(user_id, []))))
        show_task_list_for_sharing(user_id, chat_id, call.message.message_id, all_indices)
        bot.answer_callback_query(call.id, "✅ Đã chọn tất cả")
    
    elif call.data == "share_none":
        # Deselect all
        show_task_list_for_sharing(user_id, chat_id, call.message.message_id, [])
        bot.answer_callback_query(call.id, "☐ Đã bỏ chọn tất cả")
    
    elif call.data.startswith("share_toggle_"):
        # Toggle task selection
        parts = call.data.split("_")
        task_idx = int(parts[2])
        
        # Parse current selected indices
        if len(parts) > 3 and parts[3]:
            selected_indices = [int(x) for x in parts[3:] if x]
        else:
            selected_indices = []
        
        # Toggle
        if task_idx in selected_indices:
            selected_indices.remove(task_idx)
        else:
            selected_indices.append(task_idx)
        
        show_task_list_for_sharing(user_id, chat_id, call.message.message_id, selected_indices)
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("share_done_"):
        # Done selecting, show user list
        parts = call.data.split("_")
        if len(parts) > 2:
            selected_indices = [int(x) for x in parts[2:] if x]
        else:
            selected_indices = []
        
        if not selected_indices:
            bot.answer_callback_query(call.id, "⚠️ Chưa chọn task nào!")
            return
        
        # Show user list to select recipient
        show_user_list_for_sharing(user_id, chat_id, call.message.message_id, selected_indices)
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("share_to_user_"):
        # User selected from list
        parts = call.data.split("_")
        if len(parts) < 4:
            bot.answer_callback_query(call.id, "❌ Lỗi dữ liệu!")
            return
        
        recipient_id = int(parts[3])
        if len(parts) > 4:
            selected_indices = [int(x) for x in parts[4:] if x]
        else:
            selected_indices = []
        
        # Send tasks to recipient
        send_tasks_to_recipient(user_id, chat_id, call.message.message_id, recipient_id, selected_indices)
        bot.answer_callback_query(call.id, "✅ Đang gửi...")
    
    elif call.data.startswith("share_manual_input_"):
        # Manual input option selected
        parts = call.data.split("_")
        if len(parts) > 3:
            selected_indices = [int(x) for x in parts[3:] if x]
        else:
            selected_indices = []
        
        if not selected_indices:
            bot.answer_callback_query(call.id, "❌ Lỗi: Không tìm thấy task đã chọn.")
            return
        
        # Store selected in state for manual input
        user_states[user_id] = f"waiting_share_recipient_{'_'.join(map(str, selected_indices))}"
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại danh sách", callback_data=f"share_done_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_back)
        markup.add(btn_cancel)
        
        bot.edit_message_text(
            f"📤 **GỬI TASK - NHẬP THỦ CÔNG**\n\n"
            f"Đã chọn {len(selected_indices)} task.\n\n"
            f"Nhập username người nhận:\n"
            f"• Nhập: @username\n"
            f"• Hoặc: user_id (số)\n"
            f"• Hoặc: Forward tin nhắn của họ\n\n"
            f"Ví dụ: @john_doe",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("share_from_contacts_"):
        # Chọn từ danh bạ điện thoại
        parts = call.data.split("_")
        if len(parts) > 3:
            selected_indices = [int(x) for x in parts[3:] if x]
        else:
            selected_indices = []
        
        if not selected_indices:
            bot.answer_callback_query(call.id, "❌ Lỗi: Không tìm thấy task đã chọn.")
            return
        
        # Store selected in state for contact input
        user_states[user_id] = f"waiting_share_contact_{'_'.join(map(str, selected_indices))}"
        
        # Send message with contact request keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_contact = types.KeyboardButton("📱 Mở danh bạ điện thoại", request_contact=True)
        btn_cancel = types.KeyboardButton("❌ Hủy")
        markup.add(btn_contact)
        markup.add(btn_cancel)
        
        # Send new message (không thể edit vì cần ReplyKeyboardMarkup)
        bot.send_message(
            chat_id,
            f"📱 **MỞ DANH BẠ ĐIỆN THOẠI**\n\n"
            f"Đã chọn {len(selected_indices)} task để chia sẻ.\n\n"
            f"👉 **Nhấn nút bên dưới để mở danh bạ của bạn**\n\n"
            f"👤 Chọn người nhận từ danh bạ Telegram\n"
            f"_(Chỉ hiển thị người có tài khoản Telegram)_",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # View progress detail
    elif call.data.startswith("task_detail_"):
        parts = call.data.split("_")
        task_idx = int(parts[2])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")
            return
        
        task = user_tasks[user_id][task_idx]
        updates = task.get('progress_updates', [])
        
        if not updates:
            # Show message instead of just popup
            # Remove old progress line from content if exists
            task_content = re.sub(r'\n?📈 Đã hoàn thành: \d+%', '', task['content'])
            
            text = f"📝 **LỊCH SỬ CẬP NHẬT TIẾN ĐỘ**\n\n"
            text += f"📌 Task: {task_content}\n"
            text += f"📊 Hiện tại: {get_progress_bar(task.get('progress_percent', 0))}\n\n"
            text += "ℹ️ Chưa có lịch sử cập nhật.\n\n"
            text += "💡 _Hãy cập nhật tiến độ bằng cách nhấn nút 📊_"
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_list")
            markup.add(btn_back)
            
            bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
            return
        
        # Build history text
        # Remove old progress line from content if exists
        task_content = re.sub(r'\n?📈 Đã hoàn thành: \d+%', '', task['content'])
        
        text = f"📝 **LỊCH SỬ CẬP NHẬT TIẾN ĐỘ**\n\n"
        text += f"📌 Task: {task_content}\n"
        text += f"📊 Hiện tại: {get_progress_bar(task.get('progress_percent', 0))}\n\n"
        text += f"📜 **Lịch sử ({len(updates)} cập nhật):**\n\n"
        
        # Show ALL updates (newest first) - no limit
        # If too many, show latest 20
        display_updates = updates[-20:] if len(updates) > 20 else updates
        start_index = len(updates) - len(display_updates)
        
        for idx, update in enumerate(reversed(display_updates)):
            timestamp = datetime.fromisoformat(update['timestamp'])
            user_time = get_user_time(user_id, timestamp)
            time_str = user_time.strftime("%d/%m %H:%M")
            
            old = update.get('old_progress', 0)
            new = update['progress']
            delta = new - old
            
            actual_idx = len(updates) - idx
            text += f"{actual_idx}. {time_str}\n"
            text += f"   {old}% → {new}% ({'+' if delta >= 0 else ''}{delta}%)\n"
            if update.get('note'):
                text += f"   💬 {update['note']}\n"
            text += "\n"
        
        if len(updates) > 20:
            text += f"\n_Hiển thị 20/{len(updates)} cập nhật gần nhất_"
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_list")
        markup.add(btn_back)
        
        bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # Calendar picker handlers
    elif call.data.startswith("calendar_"):
        parts = call.data.split("_")
        action = parts[1]
        
        if action == "ignore":
            bot.answer_callback_query(call.id)
        
        elif action == "prev":
            year, month = int(parts[2]), int(parts[3])
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            calendar_markup = create_calendar(user_id, year, month)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=calendar_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "next":
            year, month = int(parts[2]), int(parts[3])
            month += 1
            if month > 12:
                month = 1
                year += 1
            calendar_markup = create_calendar(user_id, year, month)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=calendar_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "today":
            user_now = get_user_time(user_id)
            # Chuyển sang chọn giờ cho hôm nay
            time_markup = create_time_picker(user_id, user_now)
            
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_date_"):
                task_idx = int(state.split("_")[-1])
                task_content = user_tasks[user_id][task_idx]['content']
                bot.edit_message_text(
                    f"🕐 Chọn giờ cho hôm nay:\n'{task_content}'",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=time_markup
                )
                user_states[user_id] = f"selecting_remind_time_{task_idx}_{user_now.strftime('%Y_%m_%d')}"
            bot.answer_callback_query(call.id)
        
        elif action == "day":
            year, month, day = int(parts[2]), int(parts[3]), int(parts[4])
            selected_date = datetime(year, month, day)
            
            # Chuyển sang chọn giờ
            time_markup = create_time_picker(user_id, selected_date)
            
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_date_"):
                task_idx = int(state.split("_")[-1])
                task_content = user_tasks[user_id][task_idx]['content']
                bot.edit_message_text(
                    f"🕐 Chọn giờ - {selected_date.strftime('%d/%m/%Y')}:\n'{task_content}'",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=time_markup
                )
                user_states[user_id] = f"selecting_remind_time_{task_idx}_{selected_date.strftime('%Y_%m_%d')}"
            bot.answer_callback_query(call.id)
        
        elif action == "cancel":
            show_task_list(user_id, chat_id, call.message.message_id)
            user_states[user_id] = None
            bot.answer_callback_query(call.id)
    
    # Time picker handlers
    elif call.data.startswith("time_"):
        parts = call.data.split("_")
        action = parts[1]
        
        if action == "ignore":
            bot.answer_callback_query(call.id)
        
        elif action == "hour":
            hour = int(parts[2])
            date_str = "_".join(parts[3:])  # Join all remaining parts for date
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Hiển thị minute picker
            time_markup = create_time_picker(user_id, selected_date, hour)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=time_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "minute":
            hour = int(parts[2])
            minute = int(parts[3])
            date_str = "_".join(parts[4:])  # Join all remaining parts for date
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Tạo datetime với giờ local
            remind_local = selected_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            remind_utc = to_utc_time(user_id, remind_local)
            
            # Lưu reminder
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_time_"):
                task_idx = int(state.split("_")[3])
                
                user_tasks[user_id][task_idx]['remind_time'] = remind_utc
                user_tasks[user_id][task_idx]['reminded'] = False
                save_data()
                
                task_content = user_tasks[user_id][task_idx]['content']
                remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
                
                markup = types.InlineKeyboardMarkup()
                btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
                btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
                markup.add(btn_list, btn_menu)
                
                bot.edit_message_text(
                    f"⏰ Đã đặt nhắc nhở!\n\n"
                    f"📌 {task_content}\n"
                    f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                user_states[user_id] = None
                bot.answer_callback_query(call.id, "✅ Đã đặt nhắc nhở!")
        
        elif action == "quick":
            # Quick time selection (5m, 15m, 30m, 1h, 2h, 3h)
            duration = parts[2]
            
            if duration.endswith('m'):
                minutes = int(duration[:-1])
                remind_utc = datetime.utcnow() + timedelta(minutes=minutes)
            elif duration.endswith('h'):
                hours = int(duration[:-1])
                remind_utc = datetime.utcnow() + timedelta(hours=hours)
            else:
                bot.answer_callback_query(call.id, "❌ Lỗi!")
                return
            
            # Lưu reminder
            state = user_states.get(user_id, "")
            if state.startswith("selecting_remind_"):
                # Extract task_idx from state
                if state.startswith("selecting_remind_date_"):
                    task_idx = int(state.split("_")[-1])
                elif state.startswith("selecting_remind_time_"):
                    task_idx = int(state.split("_")[3])
                else:
                    bot.answer_callback_query(call.id, "❌ Lỗi!")
                    return
                
                user_tasks[user_id][task_idx]['remind_time'] = remind_utc
                user_tasks[user_id][task_idx]['reminded'] = False
                save_data()
                
                task_content = user_tasks[user_id][task_idx]['content']
                remind_local = get_user_time(user_id, remind_utc)
                remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
                
                markup = types.InlineKeyboardMarkup()
                btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
                btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
                markup.add(btn_list, btn_menu)
                
                bot.edit_message_text(
                    f"⏰ Đã đặt nhắc nhở!\n\n"
                    f"📌 {task_content}\n"
                    f"🕐 {remind_str} (sau {duration})",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                user_states[user_id] = None
                bot.answer_callback_query(call.id, f"✅ Nhắc sau {duration}!")
        
        elif action == "manual":
            # Nhập thời gian thủ công
            sub_action = parts[2]
            
            if sub_action == "full":
                # Nhập giờ đầy đủ HH:MM
                # date_str có thể có dấu _ (VD: 2026_07_25) nên phải join từ parts[3] trở đi
                date_str = "_".join(parts[3:])
                
                state = user_states.get(user_id, "")
                if state.startswith("selecting_remind_"):
                    # Extract task_idx from state
                    if state.startswith("selecting_remind_date_"):
                        task_idx = int(state.split("_")[-1])
                    elif state.startswith("selecting_remind_time_"):
                        task_idx = int(state.split("_")[3])
                    else:
                        bot.answer_callback_query(call.id, "❌ Lỗi!")
                        return
                    
                    # Đổi state để đợi input
                    user_states[user_id] = f"manual_time_input_{task_idx}_{date_str}"
                    
                    task_content = user_tasks[user_id][task_idx]['content']
                    bot.edit_message_text(
                        f"✍️ Nhập giờ cho:\n'{task_content}'\n\n"
                        f"Định dạng: HH:MM (ví dụ: 14:27, 9:05)\n"
                        f"Hoặc gửi /cancel để hủy",
                        chat_id=chat_id,
                        message_id=call.message.message_id
                    )
                    bot.answer_callback_query(call.id)
            
            elif sub_action == "minute":
                # Nhập chỉ phút
                hour = int(parts[3])
                # date_str có thể có dấu _ (VD: 2026_07_25) nên phải join từ parts[4] trở đi
                date_str = "_".join(parts[4:])
                
                state = user_states.get(user_id, "")
                if state.startswith("selecting_remind_time_"):
                    task_idx = int(state.split("_")[3])
                    
                    # Đổi state để đợi input phút
                    user_states[user_id] = f"manual_minute_input_{task_idx}_{hour}_{date_str}"
                    
                    task_content = user_tasks[user_id][task_idx]['content']
                    bot.edit_message_text(
                        f"✍️ Nhập phút cho {hour}:??\n'{task_content}'\n\n"
                        f"Nhập số phút (0-59), ví dụ: 27, 8, 42\n"
                        f"Hoặc gửi /cancel để hủy",
                        chat_id=chat_id,
                        message_id=call.message.message_id
                    )
                    bot.answer_callback_query(call.id)
        
        elif action == "back":
            # date_str có thể có dấu _ (VD: 2026_07_25) nên phải join từ parts[2] trở đi
            date_str = "_".join(parts[2:])
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Quay lại chọn giờ
            time_markup = create_time_picker(user_id, selected_date)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=time_markup)
            bot.answer_callback_query(call.id)
        
        elif action == "cancel":
            show_task_list(user_id, chat_id, call.message.message_id)
            user_states[user_id] = None
            bot.answer_callback_query(call.id)
    
    # Xóa tất cả
    elif call.data == "clear_yes":
        user_tasks[user_id] = []
        text, markup = show_main_menu(user_id, "🧹 Đã xóa toàn bộ danh sách công việc!")
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "clear_no":
        show_task_list(user_id, chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif call.data == "clear_all":
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("✅ Có, xóa hết", callback_data="clear_yes")
        btn_no = types.InlineKeyboardButton("❌ Không, giữ lại", callback_data="clear_no")
        markup.add(btn_yes, btn_no)
        bot.edit_message_text(
            "⚠️ Bạn có chắc chắn muốn xóa toàn bộ danh sách?",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    # Snooze reminder (hoãn nhắc nhở)
    elif call.data.startswith("reminder_snooze_"):
        parts = call.data.split("_")
        task_idx = int(parts[2])
        snooze_minutes = int(parts[3])
        
        if user_id in user_tasks and 0 <= task_idx < len(user_tasks[user_id]):
            task = user_tasks[user_id][task_idx]
            
            # Cập nhật remind_time thêm X phút
            if task.get('remind_time'):
                task['remind_time'] = task['remind_time'] + timedelta(minutes=snooze_minutes)
                task['reminded'] = False  # Cho phép nhắc lại
                save_data()
                
                remind_local = get_user_time(user_id, task['remind_time'])
                remind_str = remind_local.strftime("%H:%M")
                
                markup = types.InlineKeyboardMarkup()
                btn_list = types.InlineKeyboardButton("📋 Xem tất cả", callback_data="menu_list")
                btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
                markup.add(btn_list, btn_menu)
                
                try:
                    bot.edit_message_text(
                        f"💤 Đã hoãn nhắc nhở!\n\n"
                        f"📌 {task['content']}\n"
                        f"⏰ Sẽ nhắc lại lúc: {remind_str}",
                        chat_id=chat_id,
                        message_id=call.message.message_id,
                        reply_markup=markup
                    )
                except:
                    bot.send_message(
                        chat_id,
                        f"💤 Đã hoãn nhắc nhở!\n\n"
                        f"📌 {task['content']}\n"
                        f"⏰ Sẽ nhắc lại lúc: {remind_str}",
                        reply_markup=markup
                    )
                bot.answer_callback_query(call.id, f"✅ Hoãn {snooze_minutes} phút!")
            else:
                bot.answer_callback_query(call.id, "❌ Task không có reminder!")
        else:
            bot.answer_callback_query(call.id, "❌ Task không tồn tại!")

def get_progress_bar(progress):
    """Tạo progress bar từ % tiến độ với màu sắc theo mức độ"""
    filled = int(progress / 10)
    empty = 10 - filled
    
    # Chọn emoji và màu thanh bar theo mức tiến độ
    if progress == 100:
        emoji = "🎉"  # Hoàn thành
        bar_filled = "🟩"  # Khối xanh lá
    elif progress >= 75:
        emoji = "💪"  # Sắp xong
        bar_filled = "🟦"  # Khối xanh dương
    elif progress >= 50:
        emoji = "📈"  # Đang tốt
        bar_filled = "🟨"  # Khối vàng
    else:
        emoji = "🚀"  # Mới bắt đầu
        bar_filled = "🟥"  # Khối đỏ
    
    # Tạo thanh bar với màu sắc
    bar = bar_filled * filled + "⬜" * empty
    
    return f"{bar} {progress}% {emoji}"

def show_task_list_for_sharing(user_id, chat_id, message_id, selected_indices=None):
    """Hiển thị danh sách task với checkbox để chọn"""
    if selected_indices is None:
        selected_indices = []
    
    if user_id not in user_tasks or not user_tasks[user_id]:
        text = "📭 Danh sách trống! Không có gì để chia sẻ."
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_list")
        markup.add(btn_back)
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        return
    
    text = "📤 **CHIA SẺ TASK**\n\n"
    text += f"Đã chọn: {len(selected_indices)}/{len(user_tasks[user_id])}\n\n"
    text += "👇 Click để chọn/bỏ chọn task:\n\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for idx, task in enumerate(user_tasks[user_id]):
        is_selected = idx in selected_indices
        checkbox = "☑" if is_selected else "☐"
        status = "✅" if task['done'] else "⏳"
        
        task_text = f"{checkbox} {idx+1}. {status} {task['content'][:40]}"
        if len(task['content']) > 40:
            task_text += "..."
        
        btn = types.InlineKeyboardButton(
            task_text,
            callback_data=f"share_toggle_{idx}_{'_'.join(map(str, selected_indices))}"
        )
        markup.add(btn)
    
    # Control buttons
    btn_row1 = []
    if len(selected_indices) < len(user_tasks[user_id]):
        btn_row1.append(types.InlineKeyboardButton(
            "☑ Chọn tất cả",
            callback_data=f"share_all"
        ))
    if selected_indices:
        btn_row1.append(types.InlineKeyboardButton(
            "☐ Bỏ chọn tất cả",
            callback_data=f"share_none"
        ))
    if btn_row1:
        markup.row(*btn_row1)
    
    # Action buttons
    btn_row2 = []
    if selected_indices:
        btn_row2.append(types.InlineKeyboardButton(
            f"✅ Xong ({len(selected_indices)})",
            callback_data=f"share_done_{'_'.join(map(str, selected_indices))}"
        ))
    btn_row2.append(types.InlineKeyboardButton(
        "❌ Hủy",
        callback_data="menu_list"
    ))
    markup.row(*btn_row2)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def format_tasks_for_sharing(user_id, task_indices):
    """Format tasks để gửi cho người khác"""
    if user_id not in user_tasks:
        return "Không có task nào."
    
    text = "📋 **DANH SÁCH CÔNG VIỆC ĐƯỢC CHIA SẺ**\n\n"
    
    for i, idx in enumerate(sorted(task_indices)):
        if idx < len(user_tasks[user_id]):
            task = user_tasks[user_id][idx]
            status = "✅" if task['done'] else "⏳"
            text += f"{i+1}. {status} {task['content']}\n"
            
            # Progress
            if task.get('progress_percent') is not None:
                progress = task['progress_percent']
                text += f"   📊 {get_progress_bar(progress)}\n"
            
            # Deadline/Reminder
            if task.get('remind_time'):
                user_time = get_user_time(user_id, task['remind_time'])
                remind_str = user_time.strftime("%d/%m/%Y %H:%M")
                text += f"   ⏰ Deadline: {remind_str}\n"
            
            text += "\n"
    
    text += f"\n📤 Được chia sẻ bởi @PHT_TASK_BOT"
    return text

def show_user_list_for_sharing(user_id, chat_id, message_id, selected_indices):
    """Hiển thị danh sách người dùng để chọn người nhận task"""
    if not user_chat_mapping:
        # Không có user nào khác
        markup = types.InlineKeyboardMarkup()
        btn_contacts = types.InlineKeyboardButton("📱 Mở danh bạ điện thoại", callback_data=f"share_from_contacts_{'_'.join(map(str, selected_indices))}")
        btn_manual = types.InlineKeyboardButton("✍️ Nhập @username", callback_data=f"share_manual_input_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_contacts)
        markup.row(btn_manual, btn_cancel)
        
        bot.edit_message_text(
            f"📤 **CHỌN NGƯỜI NHẬN**\n\n"
            f"⚠️ Chưa có người dùng nào khác đã chat với bot.\n\n"
            f"💡 Bạn có thể:\n"
            f"• 📱 Nhấn nút *\"Mở danh bạ điện thoại\"* để chọn từ danh bạ\n"
            f"• ✍️ Nhập @username hoặc user_id\n"
            f"• 🤝 Yêu cầu người nhận gửi /start cho bot",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    # Lọc danh sách user (loại bỏ chính mình và chỉ lấy data hợp lệ)
    available_users = [
        (uid, data) 
        for uid, data in user_chat_mapping.items() 
        if uid != user_id and isinstance(data, dict)
    ]
    
    if not available_users:
        # Chỉ có mình trong danh sách
        markup = types.InlineKeyboardMarkup()
        btn_contacts = types.InlineKeyboardButton("📱 Mở danh bạ điện thoại", callback_data=f"share_from_contacts_{'_'.join(map(str, selected_indices))}")
        btn_manual = types.InlineKeyboardButton("✍️ Nhập @username", callback_data=f"share_manual_input_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_contacts)
        markup.row(btn_manual, btn_cancel)
        
        bot.edit_message_text(
            f"📤 **CHỌN NGƯỜI NHẬN**\n\n"
            f"⚠️ Chưa có người dùng nào khác đã chat với bot.\n\n"
            f"💡 Bạn có thể:\n"
            f"• 📱 Nhấn nút *\"Mở danh bạ điện thoại\"* để chọn từ danh bạ\n"
            f"• ✍️ Nhập @username hoặc user_id\n"
            f"• 🤝 Yêu cầu người nhận gửi /start cho bot",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    # Hiển thị danh sách người dùng
    text = f"📤 **CHỌN NGƯỜI NHẬN**\n\n"
    text += f"Đã chọn {len(selected_indices)} task để chia sẻ.\n\n"
    text += f"👥 Chọn người nhận từ danh sách:\n\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Sắp xếp theo username hoặc first_name
    # Kiểm tra data là dict trước khi truy cập
    available_users.sort(key=lambda x: (
        x[1].get('username', '') if isinstance(x[1], dict) else '' or 
        x[1].get('first_name', '') if isinstance(x[1], dict) else ''
    ).lower())
    
    for recipient_id, recipient_data in available_users:
        # Tạo display name
        username = recipient_data.get('username', '')
        first_name = recipient_data.get('first_name', '')
        last_name = recipient_data.get('last_name', '')
        
        if username:
            display_name = f"@{username}"
        elif first_name or last_name:
            display_name = f"{first_name} {last_name}".strip()
        else:
            display_name = f"User {recipient_id}"
        
        # Giới hạn độ dài tên hiển thị
        if len(display_name) > 30:
            display_name = display_name[:27] + "..."
        
        btn = types.InlineKeyboardButton(
            f"👤 {display_name}",
            callback_data=f"share_to_user_{recipient_id}_{'_'.join(map(str, selected_indices))}"
        )
        markup.add(btn)
    
    # Đặt nút chọn từ danh bạ ở đầu - Nổi bật nhất
    btn_contacts = types.InlineKeyboardButton("📱👉 Mở DANH BẠ ĐIỆN THOẠI", callback_data=f"share_from_contacts_{'_'.join(map(str, selected_indices))}")
    markup.add(btn_contacts)
    
    # Nút thủ công và hủy
    btn_manual = types.InlineKeyboardButton("✍️ Nhập @username", callback_data=f"share_manual_input_{'_'.join(map(str, selected_indices))}")
    btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
    markup.row(btn_manual, btn_cancel)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def send_tasks_to_recipient(sender_id, sender_chat_id, message_id, recipient_id, selected_indices):
    """Gửi tasks đã chọn cho người nhận"""
    if not selected_indices:
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_list")
        markup.add(btn_back)
        
        bot.edit_message_text(
            "❌ Không có task nào được chọn!",
            chat_id=sender_chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        return
    
    # Get recipient chat_id
    recipient_data = user_chat_mapping.get(recipient_id)
    if not recipient_data:
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data=f"share_done_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_back, btn_cancel)
        
        bot.edit_message_text(
            "❌ Không tìm thấy thông tin người nhận!\n\n"
            "Người nhận cần gửi /start cho bot trước.",
            chat_id=sender_chat_id,
            message_id=message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    recipient_chat_id = recipient_data.get('chat_id')
    if not recipient_chat_id:
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data=f"share_done_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_back, btn_cancel)
        
        bot.edit_message_text(
            "❌ Không tìm thấy chat_id của người nhận!",
            chat_id=sender_chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        return
    
    # Format and send
    share_text = format_tasks_for_sharing(sender_id, selected_indices)
    
    try:
        # Send to recipient
        bot.send_message(recipient_chat_id, share_text, parse_mode='Markdown')
        
        # Confirm to sender
        sender_name = user_chat_mapping.get(sender_id, {}).get('username', 'Unknown')
        recipient_username = recipient_data.get('username', '')
        recipient_first_name = recipient_data.get('first_name', '')
        recipient_last_name = recipient_data.get('last_name', '')
        
        if recipient_username:
            recipient_display = f"@{recipient_username}"
        elif recipient_first_name or recipient_last_name:
            recipient_display = f"{recipient_first_name} {recipient_last_name}".strip()
        else:
            recipient_display = f"User {recipient_id}"
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("📋 Danh sách", callback_data="menu_list")
        btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
        markup.add(btn_back, btn_menu)
        
        bot.edit_message_text(
            f"✅ **Đã gửi thành công!**\n\n"
            f"📤 Gửi tới: {recipient_display}\n"
            f"📦 Số task: {len(selected_indices)}\n\n"
            f"Người nhận sẽ thấy danh sách task trong chat với bot.",
            chat_id=sender_chat_id,
            message_id=message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Thử lại", callback_data=f"share_done_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_back, btn_cancel)
        
        bot.edit_message_text(
            f"❌ **Lỗi khi gửi:**\n{str(e)}\n\n"
            f"Có thể người nhận đã block bot hoặc chưa start bot.",
            chat_id=sender_chat_id,
            message_id=message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )

def show_task_list(user_id, chat_id, message_id=None):
    """Hiển thị danh sách task với các nút action"""
    if user_id not in user_tasks or not user_tasks[user_id]:
        text = "📭 Danh sách trống!"
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data="menu_main")
        markup.add(btn_back)
    else:
        text = "📋 DANH SÁCH CÔNG VIỆC:\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for idx, task in enumerate(user_tasks[user_id]):
            status = "✅" if task['done'] else "⏳"
            
            # Remove old progress line from content if exists
            task_content = re.sub(r'\n?📈 Đã hoàn thành: \d+%', '', task['content'])
            task_text = f"{idx+1}. {status} {task_content}"
            
            # Hiển thị progress bar (luôn hiện, kể cả 0%)
            progress = task.get('progress_percent', 0)
            task_text += f"\n   📊 {get_progress_bar(progress)}"
            
            if task.get('remind_time'):
                user_time = get_user_time(user_id, task['remind_time'])
                remind_str = user_time.strftime("%d/%m %H:%M")
                task_text += f"\n   ⏰ {remind_str}"
            
            text += task_text + "\n\n"
            
            # Nút action cho từng task
            btn_row = []
            if not task['done']:
                btn_row.append(types.InlineKeyboardButton(f"✅ {idx+1}", callback_data=f"task_done_{idx}"))
                btn_row.append(types.InlineKeyboardButton(f"📊 {idx+1}", callback_data=f"task_progress_{idx}"))
                btn_row.append(types.InlineKeyboardButton(f"⏰ {idx+1}", callback_data=f"task_remind_{idx}"))
            # Nút thêm ghi chú và xem chi tiết
            btn_row.append(types.InlineKeyboardButton(f"💬 {idx+1}", callback_data=f"task_note_{idx}"))
            btn_row.append(types.InlineKeyboardButton(f"📝 {idx+1}", callback_data=f"task_detail_{idx}"))
            btn_row.append(types.InlineKeyboardButton(f"🗑️ {idx+1}", callback_data=f"task_delete_{idx}"))
            markup.row(*btn_row)
        
        # Thêm hướng dẫn sử dụng
        text += "━━━━━━━━━━━━━━━\n"
        text += "💡 **Hướng dẫn:**\n"
        text += "✅ Hoàn thành | 📊 Tiến độ | ⏰ Nhắc nhở\n"
        text += "💬 Ghi chú | 📝 Lịch sử | 🗑️ Xóa\n\n"
        
        # Nút action chung
        btn_add = types.InlineKeyboardButton("➕ Thêm mới", callback_data="menu_add")
        btn_share = types.InlineKeyboardButton("📤 Chia sẻ", callback_data="share_start")
        btn_clear = types.InlineKeyboardButton("🧹 Xóa tất cả", callback_data="clear_all")
        btn_back = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.row(btn_add, btn_share)
        markup.row(btn_clear, btn_back)
    
    if message_id:
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

# Xử lý tin nhắn text từ user (thêm task, đặt reminder)
@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id])
def handle_user_input(message):
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    state = user_states[user_id]
    print(f"Handling user input, state: {state}, text: {message.text}")
    
    # Xử lý nút Hủy trong ReplyKeyboard (chỉ cho state có ReplyKeyboard)
    if message.text == "❌ Hủy" and state.startswith("waiting_share_contact_"):
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_list = types.InlineKeyboardButton("📋 Danh sách", callback_data="menu_list")
        btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
        markup.add(btn_list, btn_menu)
        
        bot.reply_to(message, 
            "❌ Đã hủy thao tác.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.send_message(chat_id, "Chọn hành động:", reply_markup=markup)
        return
    
    # ============= AI COLLECTING TASK STATE =============
    if state == "ai_collecting_task":
        # User đang trong conversation với AI Agent
        message_text = message.text.strip()
        
        # Get conversation context
        context = ai_conversation_context.get(user_id, {}).get('task', {})
        
        # Process with AI Agent
        result = ai_task_agent.process_message(message_text, context)
        
        if result['action'] == 'save_task':
            # Đủ thông tin - lưu task
            save_ai_task(user_id, result['task'])
            
            # Send confirmation
            bot.reply_to(message, result['ask_message'], parse_mode='Markdown')
            
            # Clear state
            if user_id in ai_conversation_context:
                del ai_conversation_context[user_id]
            user_states[user_id] = None
            
            # Show menu
            markup = types.InlineKeyboardMarkup()
            btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
            btn_add = types.InlineKeyboardButton("➕ Thêm task khác", callback_data="menu_smart_add")
            btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
            markup.add(btn_list)
            markup.add(btn_add, btn_menu)
            
            bot.send_message(chat_id, "Bạn muốn làm gì tiếp theo?", reply_markup=markup)
        
        else:
            # Thiếu thông tin - hỏi tiếp
            ai_conversation_context[user_id] = {
                'task': result['task'],
                'state': 'collecting',
                'last_update': datetime.now()
            }
            
            bot.reply_to(message, result['ask_message'], parse_mode='Markdown')
    
    # ============= END AI COLLECTING TASK STATE =============
    
    # Thêm task
    elif state == "waiting_task_content":
        task_content = message.text.strip()
        if user_id not in user_tasks:
            user_tasks[user_id] = []
        
        user_tasks[user_id].append({
            'content': task_content,
            'done': False,
            'remind_time': None,
            'reminded': False,
            'progress_percent': 0,
            'progress_updates': []
        })
        save_data()
        
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{len(user_tasks[user_id])-1}")
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="menu_add")
        btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
        markup.add(btn_remind)
        markup.add(btn_list, btn_add)
        markup.add(btn_menu)
        
        bot.reply_to(message, 
            f"✅ Đã thêm: '{task_content}'\n\n"
            f"Bạn muốn làm gì tiếp theo?",
            reply_markup=markup
        )
    
    # Share recipient input
    elif state.startswith("waiting_share_recipient_"):
        state_parts = state.split("_")
        if len(state_parts) > 3:
            selected_indices = [int(x) for x in state_parts[3:] if x]
        else:
            selected_indices = []
        
        if not selected_indices:
            bot.reply_to(message, "❌ Lỗi: Không tìm thấy task đã chọn.")
            user_states[user_id] = None
            return
        
        recipient_input = message.text.strip()
        
        # Try to get recipient user_id
        recipient_id = None
        
        # Case 1: @username
        if recipient_input.startswith('@'):
            username = recipient_input[1:]
            # Search in user_chat_mapping (chỉ tìm trong data hợp lệ)
            for uid, data in user_chat_mapping.items():
                if isinstance(data, dict) and data.get('username', '').lower() == username.lower():
                    recipient_id = uid
                    break
            
            if not recipient_id:
                bot.reply_to(message,
                    f"⚠️ Không tìm thấy user @{username}\n\n"
                    f"Lưu ý: Bot chỉ gửi được cho user đã từng chat với bot.\n\n"
                    f"Vui lòng:\n"
                    f"1. Yêu cầu họ gửi /start cho bot trước\n"
                    f"2. Hoặc nhập user_id của họ\n"
                    f"3. Hoặc forward tin nhắn của họ")
                return
        
        # Case 2: user_id (number)
        elif recipient_input.isdigit():
            recipient_id = int(recipient_input)
            if recipient_id not in user_chat_mapping:
                bot.reply_to(message,
                    f"⚠️ User ID {recipient_id} chưa từng chat với bot.\n\n"
                    f"Yêu cầu họ gửi /start cho bot trước.")
                return
        
        # Case 3: Forward message (check if message is forward)
        elif message.forward_from:
            recipient_id = message.forward_from.id
            if recipient_id not in user_chat_mapping:
                bot.reply_to(message,
                    f"⚠️ User này chưa từng chat với bot.\n\n"
                    f"Yêu cầu họ gửi /start cho bot trước.")
                return
        
        else:
            bot.reply_to(message,
                "⚠️ Định dạng không hợp lệ!\n\n"
                "Vui lòng nhập:\n"
                "• @username\n"
                "• user_id (số)\n"
                "• Hoặc forward tin nhắn của họ")
            return
        
        # Get recipient chat_id
        recipient_chat_id = user_chat_mapping.get(recipient_id, {}).get('chat_id')
        if not recipient_chat_id:
            bot.reply_to(message, "❌ Không tìm thấy chat_id của người nhận.")
            user_states[user_id] = None
            return
        
        # Format and send
        share_text = format_tasks_for_sharing(user_id, selected_indices)
        
        try:
            # Send to recipient
            bot.send_message(recipient_chat_id, share_text, parse_mode='Markdown')
            
            # Confirm to sender
            recipient_data = user_chat_mapping.get(recipient_id, {})
            recipient_username = recipient_data.get('username', '')
            recipient_first_name = recipient_data.get('first_name', '')
            recipient_last_name = recipient_data.get('last_name', '')
            
            if recipient_username:
                recipient_display = f"@{recipient_username}"
            elif recipient_first_name or recipient_last_name:
                recipient_display = f"{recipient_first_name} {recipient_last_name}".strip()
            else:
                recipient_display = f"User {recipient_id}"
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("📋 Danh sách", callback_data="menu_list")
            btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
            markup.add(btn_back, btn_menu)
            
            bot.reply_to(message,
                f"✅ **Đã gửi thành công!**\n\n"
                f"📤 Gửi tới: {recipient_display}\n"
                f"📦 Số task: {len(selected_indices)}\n\n"
                f"Người nhận sẽ thấy danh sách task trong chat với bot.",
                reply_markup=markup,
                parse_mode='Markdown')
            
            user_states[user_id] = None
            
        except Exception as e:
            bot.reply_to(message,
                f"❌ Lỗi khi gửi:\n{str(e)}\n\n"
                f"Có thể người nhận đã block bot hoặc chưa start bot.")
            user_states[user_id] = None
    
    # Manual progress input
    elif state.startswith("manual_progress_input_"):
        state_parts = state.split("_")
        task_idx = int(state_parts[3])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.reply_to(message, "❌ Task không tồn tại!")
            user_states[user_id] = None
            return
        
        # Parse progress input
        try:
            progress = int(message.text.strip())
            if progress < 0 or progress > 100:
                bot.reply_to(message, "⚠️ Tiến độ phải từ 0 đến 100%. Vui lòng nhập lại:")
                return
        except ValueError:
            bot.reply_to(message, "⚠️ Vui lòng nhập số từ 0-100. Ví dụ: 95")
            return
        
        # Set state to ask for note
        user_states[user_id] = f"progress_note_{task_idx}_{progress}"
        
        task_content = user_tasks[user_id][task_idx]['content']
        markup = types.InlineKeyboardMarkup()
        btn_skip = types.InlineKeyboardButton("⏭️ Bỏ qua (không ghi chú)", callback_data=f"skip_progress_note_{task_idx}_{progress}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_skip)
        markup.add(btn_cancel)
        
        bot.reply_to(message,
            f"📝 **THÊM GHI CHÚ CẬP NHẬT**\n\n"
            f"Task: {task_content[:50]}\n"
            f"Đã hoàn thành: {progress}%\n\n"
            f"Nhập nội dung chi tiết về cập nhật này:\n"
            f"(Ví dụ: Đã hoàn thành phân tích requirements)",
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # Add task note (without changing progress)
    elif state.startswith("add_task_note_"):
        state_parts = state.split("_")
        task_idx = int(state_parts[3])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.reply_to(message, "❌ Task không tồn tại!")
            user_states[user_id] = None
            return
        
        note = message.text.strip()
        current_progress = user_tasks[user_id][task_idx].get('progress_percent', 0)
        
        # Initialize progress_updates if not exists
        if 'progress_updates' not in user_tasks[user_id][task_idx]:
            user_tasks[user_id][task_idx]['progress_updates'] = []
        
        # Add note record (progress unchanged)
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'progress': current_progress,
            'old_progress': current_progress,
            'note': note
        }
        user_tasks[user_id][task_idx]['progress_updates'].append(update_record)
        print(f"💬 [add_task_note handler] Added note at {current_progress}% (total: {len(user_tasks[user_id][task_idx]['progress_updates'])})]")
        
        # Clear state
        user_states[user_id] = None
        save_data()
        
        # Remove old progress line from content if exists
        task_content = re.sub(r'\n?📈 Đã hoàn thành: \d+%', '', user_tasks[user_id][task_idx]['content'])
        
        markup = types.InlineKeyboardMarkup()
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_detail = types.InlineKeyboardButton("📝 Xem lịch sử", callback_data=f"task_detail_{task_idx}")
        btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
        markup.add(btn_list)
        markup.add(btn_detail, btn_menu)
        
        bot.reply_to(message,
            f"✅ **Đã thêm ghi chú!**\n\n"
            f"📌 Task: {task_content}\n"
            f"📊 Tiến độ: {get_progress_bar(current_progress)}\n"
            f"💬 Ghi chú: {note}",
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # Progress note input
    elif state.startswith("progress_note_"):
        state_parts = state.split("_")
        task_idx = int(state_parts[2])
        progress = int(state_parts[3])
        
        if user_id not in user_tasks or task_idx >= len(user_tasks[user_id]):
            bot.reply_to(message, "❌ Task không tồn tại!")
            user_states[user_id] = None
            return
        
        note = message.text.strip()
        
        # Update progress with note
        old_progress = user_tasks[user_id][task_idx].get('progress_percent', 0)
        user_tasks[user_id][task_idx]['progress_percent'] = progress
        
        # Initialize progress_updates if not exists
        if 'progress_updates' not in user_tasks[user_id][task_idx]:
            user_tasks[user_id][task_idx]['progress_updates'] = []
        
        # Add update record
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'progress': progress,
            'old_progress': old_progress,
            'note': note
        }
        user_tasks[user_id][task_idx]['progress_updates'].append(update_record)
        print(f"📝 [progress_note handler] Added update: {old_progress}% → {progress}% (total: {len(user_tasks[user_id][task_idx]['progress_updates'])})")
        
        # Auto mark as done if 100%
        if progress == 100:
            user_tasks[user_id][task_idx]['done'] = True
            # Update status to "Hoàn thành" if it exists (for AI tasks)
            if 'status' in user_tasks[user_id][task_idx]:
                user_tasks[user_id][task_idx]['status'] = 'Hoàn thành'
        
        # Clear state
        user_states[user_id] = None
        
        save_data()
        
        # Remove old progress line from content if exists
        task_content = re.sub(r'\n?📈 Đã hoàn thành: \d+%', '', user_tasks[user_id][task_idx]['content'])
        
        markup = types.InlineKeyboardMarkup()
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_detail = types.InlineKeyboardButton("📝 Xem lịch sử", callback_data=f"task_detail_{task_idx}")
        btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
        markup.add(btn_list)
        markup.add(btn_detail, btn_menu)
        
        bot.reply_to(message,
            f"✅ **Đã cập nhật tiến độ!**\n\n"
            f"📌 Task: {task_content}\n"
            f"📊 Đã hoàn thành: {get_progress_bar(progress)}\n"
            f"💬 Ghi chú: {note}",
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # Nhập giờ thủ công (HH:MM)
    elif state.startswith("manual_time_input_"):
        # State format: manual_time_input_{task_idx}_{date_str}
        # date_str có thể là "today" hoặc "YYYY_MM_DD"
        state_parts = state.split("_")
        task_idx = int(state_parts[3])
        
        # date_str có thể có dấu _ nên phải lấy từ index 4 trở đi
        date_str = "_".join(state_parts[4:])
        
        time_str = message.text.strip()
        print(f"Manual time input: task_idx={task_idx}, date_str={date_str}, time_str='{time_str}'")
        
        # Parse HH:MM hoặc H:MM
        try:
            # Kiểm tra format
            if ':' not in time_str:
                bot.reply_to(message, "⚠️ Sai định dạng! Nhập lại theo format HH:MM (ví dụ: 14:27)")
                return
            
            time_parts = time_str.split(':')
            
            # Phải có đúng 2 phần (giờ và phút)
            if len(time_parts) != 2:
                bot.reply_to(message, "⚠️ Sai định dạng! Nhập lại theo format HH:MM (ví dụ: 14:27)")
                return
            
            # Validate giờ và phút là số
            hour_str = time_parts[0].strip()
            minute_str = time_parts[1].strip()
            
            if not hour_str.isdigit() or not minute_str.isdigit():
                bot.reply_to(message, f"⚠️ Giờ và phút phải là số!\n\nBạn đã nhập: '{time_str}'\nVí dụ đúng: 14:27, 9:05")
                return
            
            hour = int(hour_str)
            minute = int(minute_str)
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                bot.reply_to(message, f"⚠️ Giờ phải từ 0-23 (bạn nhập {hour}), phút từ 0-59 (bạn nhập {minute})! Nhập lại:")
                return
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Tạo datetime với giờ local
            remind_local = selected_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            remind_utc = to_utc_time(user_id, remind_local)
            
            # Kiểm tra nếu là quá khứ
            if remind_utc <= datetime.utcnow():
                bot.reply_to(message, "⚠️ Thời gian phải là tương lai! Nhập lại:")
                return
            
            # Lưu reminder
            user_tasks[user_id][task_idx]['remind_time'] = remind_utc
            user_tasks[user_id][task_idx]['reminded'] = False
            save_data()
            user_states[user_id] = None
            
            task_content = user_tasks[user_id][task_idx]['content']
            remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
            
            markup = types.InlineKeyboardMarkup()
            btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
            btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
            markup.add(btn_list, btn_menu)
            
            bot.reply_to(message,
                f"⏰ Đã đặt nhắc nhở!\n\n"
                f"📌 {task_content}\n"
                f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
                reply_markup=markup
            )
        
        except (ValueError, IndexError) as e:
            print(f"Error parsing date or time: {e}")
            bot.reply_to(message, f"⚠️ Đã xảy ra lỗi khi xử lý!\n\nVui lòng thử lại hoặc dùng /cancel để hủy.")
    
    # Nhập phút thủ công
    elif state.startswith("manual_minute_input_"):
        # State format: manual_minute_input_{task_idx}_{hour}_{date_str}
        state_parts = state.split("_")
        task_idx = int(state_parts[3])
        hour = int(state_parts[4])
        
        # date_str có thể có dấu _ nên phải lấy từ index 5 trở đi
        date_str = "_".join(state_parts[5:])
        
        minute_str = message.text.strip()
        print(f"Manual minute input: task_idx={task_idx}, hour={hour}, date_str={date_str}, minute_str='{minute_str}'")
        
        try:
            # Validate là số
            if not minute_str.isdigit():
                bot.reply_to(message, f"⚠️ Phút phải là số từ 0-59!\n\nBạn đã nhập: '{minute_str}'")
                return
            
            minute = int(minute_str)
            print(f"Parsed minute: {minute}")
            
            if not (0 <= minute <= 59):
                bot.reply_to(message, f"⚠️ Phút phải từ 0-59 (bạn nhập {minute})! Nhập lại:")
                return
            
            # Parse date
            if date_str == "today":
                selected_date = get_user_time(user_id)
            else:
                y, m, d = date_str.split("_")
                selected_date = datetime(int(y), int(m), int(d))
            
            # Tạo datetime với giờ local
            remind_local = selected_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            remind_utc = to_utc_time(user_id, remind_local)
            
            # Kiểm tra nếu là quá khứ
            if remind_utc <= datetime.utcnow():
                bot.reply_to(message, "⚠️ Thời gian phải là tương lai! Nhập lại:")
                return
            
            # Lưu reminder
            user_tasks[user_id][task_idx]['remind_time'] = remind_utc
            user_tasks[user_id][task_idx]['reminded'] = False
            save_data()
            user_states[user_id] = None
            
            task_content = user_tasks[user_id][task_idx]['content']
            remind_str = remind_local.strftime("%d/%m/%Y %H:%M")
            
            markup = types.InlineKeyboardMarkup()
            btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
            btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
            markup.add(btn_list, btn_menu)
            
            bot.reply_to(message,
                f"⏰ Đã đặt nhắc nhở!\n\n"
                f"📌 {task_content}\n"
                f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
                reply_markup=markup
            )
        
        except (ValueError, IndexError) as e:
            print(f"Error in manual minute input: {e}")
            bot.reply_to(message, "⚠️ Đã xảy ra lỗi!\n\nVui lòng thử lại hoặc dùng /cancel để hủy.")
    
    # Đặt reminder
    elif state.startswith("waiting_remind_time_"):
        task_idx = int(state.split("_")[-1])
        time_str = message.text.strip()
        
        remind_time = parse_time(time_str, chat_id)
        
        if remind_time is None:
            bot.reply_to(message,
                "⚠️ Định dạng thời gian không hợp lệ!\n\n"
                "Thử lại (VD: 14:30, 2m, 30m, 2h):"
            )
            return
        
        if remind_time <= datetime.utcnow():
            bot.reply_to(message, "⚠️ Thời gian phải là tương lai!\n\nThử lại:")
            return
        
        user_tasks[user_id][task_idx]['remind_time'] = remind_time
        user_tasks[user_id][task_idx]['reminded'] = False
        save_data()
        user_states[user_id] = None
        
        task_content = user_tasks[user_id][task_idx]['content']
        user_time = get_user_time(user_id, remind_time)
        remind_str = user_time.strftime("%d/%m/%Y %H:%M")
        
        markup = types.InlineKeyboardMarkup()
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
        btn_menu = types.InlineKeyboardButton("🔙 Menu chính", callback_data="menu_main")
        markup.add(btn_list, btn_menu)
        
        bot.reply_to(message,
            f"⏰ Đã đặt nhắc nhở!\n\n"
            f"📌 {task_content}\n"
            f"🕐 {remind_str} (GMT+{get_user_timezone(user_id)})",
            reply_markup=markup
        )
    
    # ===== AI KNOWLEDGE BASE STATES =====
    
    # Nhập câu hỏi cho knowledge base
    elif state == "waiting_kb_question":
        question = message.text.strip()
        if len(question) < 3:
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="ai_knowledge_menu")
            markup.add(btn_cancel)
            bot.reply_to(message, "⚠️ Câu hỏi quá ngắn! Nhập lại:\n\n💡 Gõ /cancel để hủy", reply_markup=markup)
            return
        
        # Lưu câu hỏi tạm thời
        if user_id not in user_states:
            user_states[user_id] = {}
        user_states[user_id] = f"waiting_kb_answer||{question}"
        
        markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="ai_knowledge_menu")
        markup.add(btn_cancel)
        
        bot.reply_to(message,
            f"📝 Câu hỏi: {question}\n\n"
            f"Bây giờ nhập câu trả lời:\n\n"
            f"💡 Gõ /cancel để hủy",
            reply_markup=markup
        )
    
    # Nhập câu trả lời cho knowledge base
    elif state.startswith("waiting_kb_answer||"):
        question = state.split("||", 1)[1]
        answer = message.text.strip()
        
        if len(answer) < 3:
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="ai_knowledge_menu")
            markup.add(btn_cancel)
            bot.reply_to(message, "⚠️ Câu trả lời quá ngắn! Nhập lại:\n\n💡 Gõ /cancel để hủy", reply_markup=markup)
            return
        
        # Thêm vào knowledge base
        add_to_knowledge_base(
            user_id, 
            question, 
            answer,
            source='manual',
            metadata={'added_via': 'telegram_manual_entry'}
        )
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="kb_add")
        btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="kb_list")
        btn_back = types.InlineKeyboardButton("🔙 Menu AI", callback_data="category_ai")
        markup.add(btn_add, btn_list)
        markup.add(btn_back)
        
        bot.reply_to(message,
            f"✅ Đã thêm vào dữ liệu AI!\n\n"
            f"**Q:** {question}\n"
            f"**A:** {answer}\n\n"
            f"AI sẽ sử dụng dữ liệu này để trả lời.",
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # ===== ENTERPRISE STATES =====
    
    # Confirm web source (đang chờ user click button confirmation)
    elif state.startswith("confirm_scrape_data||"):
        # User đang ở state chờ confirm, nhưng lại gửi text message
        # Không làm gì, chỉ nhắc user click button
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Menu", callback_data="org_import")
        markup.add(btn_back)
        
        bot.reply_to(message,
            "⏳ **Đang chờ xác nhận...**\n\n"
            "Vui lòng click nút **✅ Có, thêm nguồn web** hoặc **❌ Không, hủy bỏ** ở tin nhắn trước đó.\n\n"
            "💡 Hoặc quay lại menu để hủy.",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    # Tạo organization
    elif state == "waiting_org_name":
        org_name = message.text.strip()
        
        if len(org_name) < 2:
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="category_enterprise")
            markup.add(btn_cancel)
            bot.reply_to(message, "⚠️ Tên quá ngắn! Nhập lại:\n\n💡 Gõ /cancel để hủy", reply_markup=markup)
            return
        
        # Create organization
        org_id = create_organization(user_id, org_name)
        user_states[user_id] = None
        save_data()
        
        markup = types.InlineKeyboardMarkup()
        btn_dept = types.InlineKeyboardButton("🏛️ Thêm Phòng Ban", callback_data="dept_add")
        btn_contact = types.InlineKeyboardButton("👥 Thêm Nhân Viên", callback_data="contact_add")
        btn_import = types.InlineKeyboardButton("📥 Import Dữ Liệu", callback_data="org_import")
        btn_back = types.InlineKeyboardButton("🔙 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_dept, btn_contact)
        markup.add(btn_import)
        markup.add(btn_back)
        
        bot.reply_to(message,
            f"✅ Đã tạo organization: **{org_name}**\n\n"
            f"🎯 Bước tiếp theo?\n\n"
            f"💡 Thêm phòng ban & nhân viên\n"
            f"hoặc import dữ liệu hàng loạt!",
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # Thêm department
    elif state == "waiting_dept_name":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.reply_to(message, "⚠️ Lỗi: Không tìm thấy organization!")
            return
        
        dept_name = message.text.strip()
        
        if len(dept_name) < 2:
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_departments")
            markup.add(btn_cancel)
            bot.reply_to(message, "⚠️ Tên quá ngắn! Nhập lại:\n\n💡 Gõ /cancel để hủy", reply_markup=markup)
            return
        
        # Add department
        dept_id = add_department(org_id, dept_name)
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_add = types.InlineKeyboardButton("➕ Thêm Phòng Ban Khác", callback_data="dept_add")
        btn_list = types.InlineKeyboardButton("📋 Xem Danh Sách", callback_data="org_departments")
        btn_menu = types.InlineKeyboardButton("🏠 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_add, btn_list)
        markup.add(btn_menu)
        
        bot.reply_to(message,
            f"✅ Đã thêm phòng ban: **{dept_name}**\n\n"
            f"💡 Tiếp tục thêm hoặc xem danh sách?",
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # Thêm contact
    elif state == "waiting_contact_name":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.reply_to(message, "⚠️ Lỗi: Không tìm thấy organization!")
            return
        
        contact_name = message.text.strip()
        
        if len(contact_name) < 2:
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_contacts")
            markup.add(btn_cancel)
            bot.reply_to(message, "⚠️ Tên quá ngắn! Nhập lại:\n\n💡 Gõ /cancel để hủy", reply_markup=markup)
            return
        
        # Ask for position (optional)
        user_states[user_id] = f"waiting_contact_position||{contact_name}"
        
        markup = types.InlineKeyboardMarkup()
        btn_skip = types.InlineKeyboardButton("⏭️ Bỏ qua", callback_data="contact_skip_position")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_contacts")
        markup.add(btn_skip, btn_cancel)
        
        bot.reply_to(message,
            f"👤 Tên: {contact_name}\n\n"
            f"📋 Nhập chức vụ (hoặc bỏ qua):\n\n"
            f"(Ví dụ: Kỹ sư phần mềm, Trưởng phòng IT)\n\n"
            f"💡 Gõ /cancel để hủy",
            reply_markup=markup
        )
    
    # Contact - Position
    elif state.startswith("waiting_contact_position||"):
        contact_name = state.split("||", 1)[1]
        position = message.text.strip()
        
        # Ask for email
        user_states[user_id] = f"waiting_contact_email||{contact_name}||{position}"
        
        markup = types.InlineKeyboardMarkup()
        btn_skip = types.InlineKeyboardButton("⏭️ Bỏ qua", callback_data="contact_skip_email")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_contacts")
        markup.add(btn_skip, btn_cancel)
        
        bot.reply_to(message,
            f"👤 Tên: {contact_name}\n"
            f"📋 Chức vụ: {position}\n\n"
            f"📧 Nhập email (hoặc bỏ qua):\n\n"
            f"(Ví dụ: name@company.com)\n\n"
            f"💡 Gõ /cancel để hủy",
            reply_markup=markup
        )
    
    # Contact - Email
    elif state.startswith("waiting_contact_email||"):
        parts = state.split("||")
        contact_name = parts[1]
        position = parts[2] if len(parts) > 2 else ""
        email = message.text.strip()
        
        org_id = get_active_org(user_id)
        if not org_id:
            bot.reply_to(message, "⚠️ Lỗi: Không tìm thấy organization!")
            return
        
        # Add contact
        contact_id = add_contact(org_id, contact_name, position=position, email=email)
        user_states[user_id] = None
        
        markup = types.InlineKeyboardMarkup()
        btn_add = types.InlineKeyboardButton("➕ Thêm Nhân Viên Khác", callback_data="contact_add")
        btn_list = types.InlineKeyboardButton("📋 Xem Danh Bạ", callback_data="org_contacts")
        btn_menu = types.InlineKeyboardButton("🏠 Menu Doanh Nghiệp", callback_data="category_enterprise")
        markup.add(btn_add, btn_list)
        markup.add(btn_menu)
        
        bot.reply_to(message,
            f"✅ Đã thêm nhân viên:\n\n"
            f"👤 {contact_name}\n"
            + (f"📋 {position}\n" if position else "")
            + (f"📧 {email}\n" if email else "")
            + f"\n💡 Tiếp tục thêm hoặc xem danh bạ?",
            reply_markup=markup
        )
    
    # Import từ text
    elif state == "waiting_import_text":
        org_id = get_active_org(user_id)
        if not org_id:
            bot.reply_to(message, "⚠️ Lỗi: Không tìm thấy organization!")
            return
        
        import_data = message.text.strip()
        
        if len(import_data) < 10:
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_import")
            markup.add(btn_cancel)
            bot.reply_to(message, "⚠️ Dữ liệu quá ngắn! Nhập lại:\n\n💡 Gõ /cancel để hủy", reply_markup=markup)
            return
        
        # Processing message
        processing_msg = bot.reply_to(message, "📊 Đang phân tích dữ liệu...")
        
        # Parse data first
        results = import_from_text(import_data, org_id)
        
        # Count Q&A pairs
        qa_pairs = []
        for line in import_data.split('\n'):
            line = line.strip()
            if '|' in line and not line.startswith('['):
                parts = line.split('|', 1)
                if len(parts) == 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    if question and answer and not question.startswith('#'):
                        qa_pairs.append({'question': question, 'answer': answer})
        
        # ===== PREVIEW & ASK CONFIRMATION =====
        total_items = results['qa_pairs'] + results['departments'] + results['contacts']
        
        # Build preview text
        preview_text = f"🔍 **PREVIEW DỮ LIỆU**\n\n"
        preview_text += f"📊 Tổng số items:\n"
        preview_text += f"   📚 Q&A: {results['qa_pairs']}\n"
        preview_text += f"   🏛️ Phòng ban: {results['departments']}\n"
        preview_text += f"   👥 Nhân viên: {results['contacts']}\n\n"
        
        if qa_pairs:
            preview_text += "📋 **Mẫu Q&A:**\n\n"
            for i, qa in enumerate(qa_pairs[:3], 1):
                q = qa['question'][:60] + '...' if len(qa['question']) > 60 else qa['question']
                a = qa['answer'][:80] + '...' if len(qa['answer']) > 80 else qa['answer']
                preview_text += f"{i}. **Q:** {q}\n"
                preview_text += f"   **A:** {a}\n\n"
            
            if len(qa_pairs) > 3:
                preview_text += f"_...và {len(qa_pairs) - 3} cặp Q&A khác_\n\n"
        
        if results['errors']:
            preview_text += f"⚠️ **Lỗi:** {len(results['errors'])} dòng\n\n"
        
        preview_text += "❓ **Bạn có muốn thêm dữ liệu này vào Knowledge Base?**"
        
        # Store import data temporarily
        if not hasattr(user_states, '_temp_import_data'):
            user_states._temp_import_data = {}
        user_states._temp_import_data[user_id] = {
            'import_data': import_data,
            'qa_pairs': qa_pairs,
            'results': results,
            'org_id': org_id
        }
        
        user_states[user_id] = "confirm_import_text"
        
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("✅ Có, thêm vào KB", callback_data="import_confirm_yes")
        btn_no = types.InlineKeyboardButton("❌ Không, hủy bỏ", callback_data="import_confirm_no")
        markup.add(btn_yes, btn_no)
        
        try:
            bot.edit_message_text(
                preview_text,
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            bot.reply_to(message, preview_text, reply_markup=markup, parse_mode='Markdown')
    
    # Import từ URL
    elif state == "waiting_import_url":
        org_id = get_active_org(user_id)
        if not org_id:
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Menu", callback_data="category_enterprise")
            markup.add(btn_back)
            user_states[user_id] = None  # Clear state
            bot.reply_to(message, "⚠️ Lỗi: Không tìm thấy organization!", reply_markup=markup)
            return
        
        url = message.text.strip()
        
        # Validate URL
        if not url.startswith('http'):
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_retry = types.InlineKeyboardButton("🔄 Thử lại", callback_data="import_web")
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="org_import")
            markup.add(btn_retry, btn_cancel)
            bot.reply_to(message, "⚠️ URL không hợp lệ! Nhập lại:\n\n💡 Gõ /cancel để hủy", reply_markup=markup)
            return
        
        # Clear state immediately so user can /cancel while scraping
        user_states[user_id] = None
        scraping_cancelled[user_id] = False  # Initialize cancel flag
        
        # Processing message with Cancel button
        cancel_markup = types.InlineKeyboardMarkup()
        btn_cancel = types.InlineKeyboardButton("❌ Hủy & Về Menu", callback_data="scrape_cancel")
        cancel_markup.add(btn_cancel)
        processing_msg = bot.reply_to(message, "🌐 Đang tải và kiểm tra website...\n\n💡 Nhấn nút bên dưới để hủy", reply_markup=cancel_markup)
        
        # Scrape with error handling
        try:
            data, error = scrape_website(url)
        except Exception as e:
            error = f"Lỗi không xác định: {str(e)[:100]}"
            data = None
        
        # Check if user cancelled during scraping
        if scraping_cancelled.get(user_id, False):
            scraping_cancelled.pop(user_id, None)  # Clear flag
            return  # User cancelled, don't show results
        
        # Clear cancel flag
        scraping_cancelled.pop(user_id, None)
        
        if error:
            markup = types.InlineKeyboardMarkup()
            btn_retry = types.InlineKeyboardButton("🔄 Thử Lại", callback_data="import_web")
            btn_back = types.InlineKeyboardButton("🔙 Menu", callback_data="org_import")
            markup.add(btn_retry, btn_back)
            
            try:
                bot.edit_message_text(
                    f"❌ Lỗi khi tải:\n\n{error}\n\n"
                    f"💡 Kiểm tra URL và thử lại.",
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    reply_markup=markup
                )
            except:
                bot.reply_to(message, f"❌ {error}", reply_markup=markup)
            return
        
        # ===== AUTO SAVE - Tự động lưu nguồn web =====
        content_length = data.get('content_length', 0)
        
        # Lưu nguồn web tự động (không cần confirm)
        if org_id not in web_sources:
            web_sources[org_id] = []
        
        web_sources[org_id].append({
            'id': generate_id('source'),
            'url': url,
            'title': data.get('title', 'Untitled'),
            'description': data.get('description', ''),
            'raw_content': data.get('raw_content', ''),
            'content_length': content_length,
            'type': 'web_passive',
            'added_at': datetime.utcnow().isoformat(),
            'status': 'ready',
            'added_by': user_id
        })
        save_data()
        
        # Clear state
        user_states[user_id] = None
        
        # Success message - Ngắn gọn và quay về menu
        result_text = f"✅ **ĐÃ THÊM NGUỒN WEB**\n\n"
        result_text += f"📄 {data.get('title', 'Untitled')[:60]}\n"
        result_text += f"📊 {content_length:,} ký tự\n\n"
        result_text += f"🤖 AI sẽ tự tìm khi bạn hỏi câu hỏi!"
        
        markup = types.InlineKeyboardMarkup()
        btn_more = types.InlineKeyboardButton("➕ Thêm nguồn khác", callback_data="import_web")
        btn_back = types.InlineKeyboardButton("🔙 Import Menu", callback_data="org_import")
        markup.add(btn_more, btn_back)
        
        try:
            bot.edit_message_text(
                result_text,
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            bot.reply_to(message, result_text, reply_markup=markup, parse_mode='Markdown')
    
    # ===== END ENTERPRISE STATES =====

# ============= NATURAL LANGUAGE HANDLER với AI =============

# ============= VOICE TO TEXT FEATURES =============

def download_voice_file(file_id):
    """Download voice file từ Telegram"""
    try:
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        
        # Download file
        response = requests.get(file_url, timeout=30)
        if response.status_code == 200:
            # Lưu tạm thời
            temp_filename = f"voice_{file_id}.ogg"
            with open(temp_filename, 'wb') as f:
                f.write(response.content)
            return temp_filename
        return None
    except Exception as e:
        print(f"Error downloading voice: {e}")
        return None

def transcribe_audio(audio_file_path):
    """Chuyển đổi audio thành text bằng OpenAI Whisper API"""
    if not OPENAI_API_KEY:
        return None
    
    try:
        # Sử dụng OpenAI Whisper API
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'file': (audio_file_path, audio_file, 'audio/ogg'),
                'model': (None, 'whisper-1'),
                'language': (None, 'vi'),  # Tiếng Việt
                'response_format': (None, 'text')
            }
            
            response = requests.post(url, headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Whisper API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

@bot.message_handler(content_types=['contact'])
def handle_contact_message(message):
    """Xử lý khi người dùng gửi contact từ danh bạ"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    # Check if user is in share contact state
    state = user_states.get(user_id)
    
    if state and state.startswith("waiting_share_contact_"):
        # Đang trong quá trình chọn contact để share task
        state_parts = state.split("_")
        if len(state_parts) > 3:
            selected_indices = [int(x) for x in state_parts[3:] if x]
        else:
            selected_indices = []
        
        if not selected_indices:
            bot.reply_to(message, "❌ Lỗi: Không tìm thấy task đã chọn.", 
                        reply_markup=types.ReplyKeyboardRemove())
            user_states[user_id] = None
            return
        
        # Get contact info
        contact = message.contact
        recipient_id = contact.user_id
        
        if not recipient_id:
            markup = types.InlineKeyboardMarkup()
            btn_retry = types.InlineKeyboardButton("🔄 Thử lại", callback_data=f"share_from_contacts_{'_'.join(map(str, selected_indices))}")
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
            markup.add(btn_retry, btn_cancel)
            
            bot.reply_to(message,
                "⚠️ **Không thể lấy User ID**\n\n"
                "Contact này chưa có tài khoản Telegram hoặc không cho phép tìm kiếm theo số điện thoại.\n\n"
                "Vui lòng chọn người khác hoặc nhập thủ công @username.",
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )
            bot.send_message(chat_id, "Chọn hành động:", reply_markup=markup)
            user_states[user_id] = None
            return
        
        # Check if contact is the sender themselves
        if recipient_id == user_id:
            markup = types.InlineKeyboardMarkup()
            btn_retry = types.InlineKeyboardButton("🔄 Chọn lại", callback_data=f"share_from_contacts_{'_'.join(map(str, selected_indices))}")
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
            markup.add(btn_retry, btn_cancel)
            
            bot.reply_to(message,
                "⚠️ Bạn không thể gửi task cho chính mình!\n\n"
                "Vui lòng chọn người khác.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            bot.send_message(chat_id, "Chọn hành động:", reply_markup=markup)
            user_states[user_id] = None
            return
        
        # Check if recipient has chatted with bot
        if recipient_id not in user_chat_mapping:
            # Save contact info to mapping
            user_chat_mapping[recipient_id] = {
                'chat_id': None,  # Will be updated when they start the bot
                'username': '',
                'first_name': contact.first_name or '',
                'last_name': contact.last_name or ''
            }
            save_data()
            
            recipient_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip() or str(recipient_id)
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data=f"share_done_{'_'.join(map(str, selected_indices))}")
            btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
            markup.add(btn_back, btn_cancel)
            
            bot.reply_to(message,
                f"⚠️ **Chưa thể gửi**\n\n"
                f"👤 {recipient_name} chưa từng chat với bot.\n\n"
                f"Yêu cầu họ gửi /start cho @PHT_TASK_BOT trước, sau đó bạn có thể thử lại.",
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )
            bot.send_message(chat_id, "Chọn hành động:", reply_markup=markup)
            user_states[user_id] = None
            return
        
        # All checks passed, send tasks
        user_states[user_id] = None
        
        # Remove keyboard first
        bot.send_message(chat_id, "✅ Đã chọn contact, đang gửi...", 
                        reply_markup=types.ReplyKeyboardRemove())
        
        # Send tasks
        send_tasks_to_recipient_from_contact(user_id, chat_id, recipient_id, selected_indices, contact)
    
    else:
        # Not in share state, just acknowledge
        bot.reply_to(message, 
            "👤 Đã nhận contact!\n\n"
            "💡 Bạn có thể sử dụng tính năng này khi chia sẻ task bằng cách:\n"
            "1. Chọn task cần chia sẻ (/share)\n"
            "2. Chọn 'Chọn từ danh bạ'\n"
            "3. Gửi contact người nhận",
            reply_markup=types.ReplyKeyboardRemove()
        )

def send_tasks_to_recipient_from_contact(sender_id, sender_chat_id, recipient_id, selected_indices, contact):
    """Gửi tasks cho người nhận được chọn từ contact"""
    if not selected_indices:
        bot.send_message(sender_chat_id, "❌ Không có task nào được chọn!")
        return
    
    # Get recipient data
    recipient_data = user_chat_mapping.get(recipient_id)
    if not recipient_data or not recipient_data.get('chat_id'):
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Quay lại", callback_data=f"share_done_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_back, btn_cancel)
        
        recipient_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip() or str(recipient_id)
        
        bot.send_message(
            sender_chat_id,
            f"⚠️ **Không thể gửi**\n\n"
            f"👤 {recipient_name} chưa từng chat với bot.\n\n"
            f"Yêu cầu họ gửi /start cho bot trước.",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    recipient_chat_id = recipient_data.get('chat_id')
    
    # Format and send tasks
    share_text = format_tasks_for_sharing(sender_id, selected_indices)
    
    try:
        # Send to recipient
        bot.send_message(recipient_chat_id, share_text, parse_mode='Markdown')
        
        # Display name from contact
        recipient_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip() or str(recipient_id)
        if contact.phone_number:
            recipient_name += f" ({contact.phone_number})"
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("📋 Danh sách", callback_data="menu_list")
        btn_menu = types.InlineKeyboardButton("🏠 Menu chính", callback_data="menu_main")
        markup.add(btn_back, btn_menu)
        
        bot.send_message(
            sender_chat_id,
            f"✅ **Đã gửi thành công!**\n\n"
            f"📤 Gửi tới: {recipient_name}\n"
            f"📦 Số task: {len(selected_indices)}\n\n"
            f"Người nhận sẽ thấy danh sách task trong chat với bot.",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 Thử lại", callback_data=f"share_done_{'_'.join(map(str, selected_indices))}")
        btn_cancel = types.InlineKeyboardButton("❌ Hủy", callback_data="menu_list")
        markup.add(btn_back, btn_cancel)
        
        bot.send_message(
            sender_chat_id,
            f"❌ **Lỗi khi gửi:**\n{str(e)}\n\n"
            f"Có thể người nhận đã block bot.",
            reply_markup=markup,
            parse_mode='Markdown'
        )

@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    """Xử lý tin nhắn voice - chuyển đổi thành text"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    
    print(f"Voice message from user_id {user_id} (chat_id {chat_id})")
    
    # Kiểm tra có OpenAI API key không
    if not OPENAI_API_KEY:
        bot.reply_to(message, 
            "🎤 Tính năng chuyển đổi giọng nói cần OpenAI API key!\n\n"
            "📝 Thêm OPENAI_API_KEY vào file .env để sử dụng tính năng này.\n"
            "💡 Xem hướng dẫn: /help"
        )
        return
    
    # Gửi typing indicator
    bot.send_chat_action(chat_id, 'typing')
    
    # Thông báo đang xử lý
    processing_msg = bot.reply_to(message, "🎤 Đang xử lý giọng nói...")
    
    try:
        # Download voice file
        voice_file_id = message.voice.file_id
        audio_path = download_voice_file(voice_file_id)
        
        if not audio_path:
            bot.edit_message_text(
                "❌ Không thể tải xuống file giọng nói.",
                chat_id=chat_id,
                message_id=processing_msg.message_id
            )
            return
        
        # Cập nhật status
        bot.edit_message_text(
            "🤖 Đang chuyển đổi giọng nói thành văn bản...",
            chat_id=chat_id,
            message_id=processing_msg.message_id
        )
        
        # Transcribe audio
        transcribed_text = transcribe_audio(audio_path)
        
        # Xóa file tạm
        try:
            os.remove(audio_path)
        except:
            pass
        
        if not transcribed_text:
            bot.edit_message_text(
                "❌ Không thể chuyển đổi giọng nói. Vui lòng thử lại.",
                chat_id=chat_id,
                message_id=processing_msg.message_id
            )
            return
        
        # Tạo file txt (riêng tư cho từng user)
        txt_filename = f"transcription_{user_id}_{int(time.time())}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=== CHUYỂN ĐỔI GIỌNG NÓI THÀNH VĂN BẢN ===\n")
            f.write(f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Người dùng: {message.from_user.first_name}\n")
            f.write("="*50 + "\n\n")
            f.write(transcribed_text)
        
        # Gửi file txt VỀ PRIVATE CHAT của user (không gửi vào group)
        # Đảm bảo privacy: mỗi user chỉ nhìn thấy transcription của chính mình
        try:
            # Tạo inline keyboard với nút quay lại menu
            markup = types.InlineKeyboardMarkup()
            btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
            markup.add(btn_menu)
            
            with open(txt_filename, 'rb') as f:
                bot.send_document(
                    user_id,  # Gửi về user_id (private chat), không gửi vào group
                    f,
                    caption=f"📝 **Nội dung văn bản:**\n\n{transcribed_text}\n\n✅ File đã được tạo!",
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            
            # Nếu voice được gửi từ group, thông báo user check private chat
            if chat_id != user_id:  # Nếu là group chat
                # Xóa file txt tạm
                try:
                    os.remove(txt_filename)
                except:
                    pass
                
                # Tạo inline keyboard với nút quay lại menu
                markup = types.InlineKeyboardMarkup()
                btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
                markup.add(btn_menu)
                
                bot.edit_message_text(
                    "✅ Đã chuyển đổi xong! Tôi đã gửi file txt vào chat riêng với bạn để đảm bảo riêng tư. 🔒",
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    reply_markup=markup
                )
                return
                
        except telebot.apihelper.ApiTelegramException as api_error:
            # Không thể gửi vào private chat (user chưa start bot)
            if "bot can't initiate conversation" in str(api_error) or "Forbidden" in str(api_error):
                # Xóa file txt tạm
                try:
                    os.remove(txt_filename)
                except:
                    pass
                
                # Tạo inline keyboard với nút quay lại menu
                markup = types.InlineKeyboardMarkup()
                btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
                markup.add(btn_menu)
                
                bot.edit_message_text(
                    "⚠️ **Không thể gửi file txt vào chat riêng!**\n\n"
                    "📝 Để nhận transcription riêng tư, bạn cần:\n"
                    "1️⃣ Mở chat riêng với bot\n"
                    "2️⃣ Gửi lệnh /start\n"
                    "3️⃣ Sau đó gửi lại voice message\n\n"
                    "🔒 Điều này đảm bảo các members khác không thấy nội dung của bạn!",
                    chat_id=chat_id,
                    message_id=processing_msg.message_id,
                    reply_markup=markup
                )
                return
            else:
                # Lỗi khác, re-raise để exception handler chính xử lý
                raise
        
        # Xóa file txt tạm (private chat)
        try:
            os.remove(txt_filename)
        except:
            pass
        
        # Xóa processing message (private chat)
        bot.delete_message(chat_id, processing_msg.message_id)
        
    except Exception as e:
        print(f"Error handling voice message: {e}")
        # Cleanup file nếu còn
        try:
            if 'txt_filename' in locals():
                os.remove(txt_filename)
        except:
            pass
        try:
            if 'audio_path' in locals():
                os.remove(audio_path)
        except:
            pass
        
        # Hiển thị lỗi cho user
        error_msg = "⚠️ Đã xảy ra lỗi khi xử lý!\n\n"
        
        # Phân tích lỗi cụ thể
        if "insufficient_quota" in str(e) or "quota" in str(e).lower():
            error_msg += "💳 **Lỗi OpenAI API:** Tài khoản hết credits\n\n"
            error_msg += "📝 Giải pháp:\n"
            error_msg += "• Thêm payment method tại: platform.openai.com\n"
            error_msg += "• Nạp credits ($5 = 833 phút voice)\n"
            error_msg += "• Kiểm tra usage tại: platform.openai.com/usage"
        elif "401" in str(e) or "authentication" in str(e).lower():
            error_msg += "🔑 **Lỗi API Key:** OpenAI key không hợp lệ\n\n"
            error_msg += "📝 Giải pháp:\n"
            error_msg += "• Kiểm tra OPENAI_API_KEY trong .env\n"
            error_msg += "• Tạo key mới tại: platform.openai.com/api-keys"
        elif "timeout" in str(e).lower() or "connection" in str(e).lower():
            error_msg += "🌐 **Lỗi mạng:** Không thể kết nối OpenAI API\n\n"
            error_msg += "📝 Vui lòng thử lại sau vài phút"
        else:
            error_msg += f"📝 Chi tiết: {str(e)[:100]}\n\n"
            error_msg += "💡 Vui lòng thử lại hoặc liên hệ admin"
        
        try:
            bot.edit_message_text(
                error_msg,
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
        except:
            try:
                bot.reply_to(message, error_msg, parse_mode='Markdown')
            except:
                bot.reply_to(message, "⚠️ Đã xảy ra lỗi khi xử lý! Vui lòng thử lại.")

# Xử lý tin nhắn ngôn ngữ tự nhiên (không phải lệnh, không trong state)
@bot.message_handler(func=lambda message: message.from_user.id not in user_states or not user_states[message.from_user.id])
def handle_natural_language(message):
    """Xử lý ngôn ngữ tự nhiên với AI"""
    user_id = get_user_id(message)
    chat_id = message.chat.id
    update_user_chat_mapping(message)
    user_text = message.text.strip()
    
    # Bỏ qua nếu là lệnh
    if user_text.startswith('/'):
        return
    
    print(f"Natural language input from user_id {user_id} (chat_id {chat_id}): {user_text}")
    
    # ===== KIỂM TRA AI CHAT MODE =====
    if user_ai_chat_mode.get(user_id, False):
        # Chế độ AI Chat đang bật - Tự động trả lời
        bot.send_chat_action(chat_id, 'typing')
        
        # Use enhanced AI response với enterprise features
        org_id = get_active_org(user_id)
        ai_response = get_enhanced_ai_response(user_id, user_text, org_id)
        
        if ai_response:
            markup = types.InlineKeyboardMarkup()
            btn_save = types.InlineKeyboardButton("💾 Lưu Q&A này", callback_data="kb_save_last")
            markup.add(btn_save)
            
            btn_ai = types.InlineKeyboardButton("🤖 Menu AI", callback_data="category_ai")
            btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
            markup.add(btn_ai, btn_menu)
            
            bot.reply_to(message, ai_response, reply_markup=markup, parse_mode='Markdown')
        else:
            markup = types.InlineKeyboardMarkup()
            btn_ai = types.InlineKeyboardButton("🤖 Menu AI", callback_data="category_ai")
            btn_menu = types.InlineKeyboardButton("🏠 Menu Chính", callback_data="menu_main")
            markup.add(btn_ai, btn_menu)
            
            bot.reply_to(message,
                "😅 Xin lỗi, tôi chưa thể trả lời câu hỏi này.\n\n"
                "💡 Bạn có thể:\n"
                "• Thêm dữ liệu Q&A vào Menu AI\n"
                "• Import dữ liệu từ Menu Doanh Nghiệp\n"
                "• Cấu hình GitHub Token để dùng AI",
                reply_markup=markup
            )
        return
    
    # ===== CHẾ ĐỘ THƯỜNG - Tạo task từ ngôn ngữ tự nhiên =====
    
    # Nếu không có GitHub token, sử dụng mode thông thường
    if not GITHUB_TOKEN:
        bot.reply_to(message, 
            "💡 Gửi tin nhắn tự do! Nhưng cần GitHub token để kích hoạt AI.\n\n"
            "Dùng /add để thêm task hoặc chọn menu bên dưới.",
            reply_markup=show_main_menu(user_id)[1]
        )
        return
    
    # Gửi typing indicator
    bot.send_chat_action(chat_id, 'typing')
    
    # Parse với AI
    ai_result = parse_natural_language_task(user_text, user_id)
    
    if not ai_result:
        # AI không trả về kết quả, fallback
        bot.reply_to(message,
            "🤔 Tôi chưa hiểu rõ ý bạn.\n\n"
            "Thử lại hoặc dùng /add để thêm task.",
            reply_markup=show_main_menu(user_id)[1]
        )
        return
    
    # Tạo task từ AI result
    task_content = ai_result.get('task', user_text)
    has_reminder = ai_result.get('has_reminder', False)
    time_str = ai_result.get('time', '')
    
    # Thêm task
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    
    task_idx = len(user_tasks[user_id])
    user_tasks[user_id].append({
        'content': task_content,
        'done': False,
        'remind_time': None,
        'reminded': False,
        'progress_percent': 0,
        'progress_updates': []
    })
    save_data()
    
    response_text = f"✅ Đã thêm: '{task_content}'"
    
    # Xử lý reminder nếu có
    if has_reminder and time_str:
        remind_time = parse_time(time_str, user_id)
        if remind_time and remind_time > datetime.utcnow():
            user_tasks[user_id][task_idx]['remind_time'] = remind_time
            user_tasks[user_id][task_idx]['reminded'] = False
            save_data()
            
            user_time = get_user_time(user_id, remind_time)
            remind_str = user_time.strftime("%d/%m/%Y %H:%M")
            response_text += f"\n⏰ Nhắc nhở: {remind_str}"
    
    # Hiển thị với buttons
    markup = types.InlineKeyboardMarkup()
    if not has_reminder or not time_str:
        btn_remind = types.InlineKeyboardButton("⏰ Đặt nhắc nhở", callback_data=f"task_remind_{task_idx}")
        markup.add(btn_remind)
    btn_list = types.InlineKeyboardButton("📋 Xem danh sách", callback_data="menu_list")
    btn_add = types.InlineKeyboardButton("➕ Thêm tiếp", callback_data="menu_add")
    markup.add(btn_list, btn_add)
    
    bot.reply_to(message, response_text + "\n\n🤖 Phân tích bởi AI", reply_markup=markup)

# Chạy bot
if __name__ == "__main__":
    print("🤖 Bot đang khởi động...")
    
    # Load existing data from JSON files
    print("📂 Loading data...")
    load_data()
    
    # Create daily backup
    print("💾 Creating backup...")
    auto_backup()
    
    try:
        bot_info = bot.get_me()
        print(f"📱 Bot name: @{bot_info.username}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print("✅ Bot đã sẵn sàng và đang lắng nghe tin nhắn...")
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Lỗi khởi động bot: {e}")
