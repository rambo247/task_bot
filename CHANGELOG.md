# Changelog

Tất cả các thay đổi quan trọng của dự án sẽ được ghi lại ở đây.

## [2.0.0] - 2026-07-25 🎉 MAJOR UPDATE

### 🌟 Major Changes
- **Redesigned as Multi-Function Assistant** - Bot không còn chỉ là task manager đơn thuần
- **Category-Based Menu System** - Menu được tổ chức thành 6 categories dễ điều hướng
- **Extensible Architecture** - Dễ dàng thêm features mới vào các categories

### ✨ New Features

#### 🎤 Voice Tools Category
- Voice to text transcription với OpenAI Whisper API
- Hỗ trợ tiếng Việt và nhiều ngôn ngữ
- Xuất file .txt với transcription
- Privacy-first: Transcription gửi về private chat
- Chi phí ~150 VND/phút
- Hướng dẫn chi tiết trong VOICE_TO_TEXT_GUIDE.md

#### 🤖 AI Assistant Category  
- Natural language task creation với GitHub Models API
- AI tự động phân tích thời gian và tạo reminder
- Smart task parsing từ câu nói tự nhiên
- Setup guide trong AI_SETUP.md
- Roadmap cho AI features: Smart analysis, Suggestions

#### 📋 Task Manager (Enhanced)
- Filter tasks: Tất cả / Đang làm / Hoàn thành
- Task statistics: Total, Pending, Completed, With reminders
- Improved task list UI with better formatting
- Quick Add button từ menu chính

#### ⚙️ Settings Category
- Comprehensive settings menu
- Clear all data with confirmation
- About bot information  
- User statistics dashboard
- Completion rate tracking

#### ⚡ Quick Actions
- Quick Add button trên menu chính
- Faster access to common actions
- Improved navigation flow

### 🔧 Improvements
- **Menu UX**: Category-based organization thay vì flat menu
- **Help System**: Comprehensive help với category breakdown
- **Navigation**: Consistent back buttons và menu flow
- **Statistics**: Real-time stats hiển thị trên các menu
- **Markdown Support**: Rich text formatting trong messages

### 🐛 Bug Fixes
- Fixed user_states consistency (user_id vs chat_id)
- Fixed date parsing in manual time input callbacks
- Fixed voice transcription privacy (group → private chat)
- Fixed error handling với detailed error messages
- Fixed "Forbidden" error khi user chưa /start bot

### 📚 Documentation
- Updated README.md with multi-function architecture
- Created VOICE_TO_TEXT_GUIDE.md (comprehensive)
- Created VOICE_QUICK_SETUP.md (5-minute guide)
- Updated help texts to reflect new menu structure

### 🔒 Privacy & Security
- Voice transcriptions luôn gửi về private chat
- User data completely isolated (user_id based)
- Group members không thể xem data của nhau
- API keys secured in environment variables

### 🚀 Coming Soon (Announced in AI Assistant menu)
- 📊 Smart Task Analysis
- 🔮 AI Suggestions & Recommendations
- 🎯 Smart Reminders (context-aware, adaptive)
- 🤝 Team Collaboration features
- 📍 Location-based reminders

---

## [1.0.0] - 2026-07-22

### Added
- 🎉 Phiên bản đầu tiên của Telegram Task Bot
- ➕ Lệnh `/add` để thêm công việc mới
- 📝 Lệnh `/list` để xem danh sách công việc
- ✅ Lệnh `/done` để đánh dấu công việc hoàn thành
- 🗑️ Lệnh `/delete` để xóa công việc cụ thể
- 🧹 Lệnh `/clear` để xóa toàn bộ danh sách (có xác nhận)
- 📚 Lệnh `/help` với hướng dẫn chi tiết
- 💾 Lưu trữ task riêng biệt cho từng user
- 🔒 Hỗ trợ biến môi trường cho Bot Token
- 📋 Hiển thị trạng thái hoàn thành với emoji
- ⚠️ Xác nhận trước khi xóa toàn bộ danh sách

### Documentation
- 📖 README với hướng dẫn đầy đủ
- 🚀 Hướng dẫn deploy lên Heroku, Railway, Render, PythonAnywhere
- 🤝 Contributing guidelines
- 🔐 Security policy
- 📄 MIT License

### Configuration
- 📦 requirements.txt với dependencies
- 🙈 .gitignore cho Python projects
- 🔧 .env.example cho cấu hình
- 📝 Procfile cho Heroku deployment
- 🔄 GitHub Actions workflow cho CI/CD

## [Unreleased]

### Planned Features
- ⏰ Thêm reminder với thời gian cụ thể
- 🏷️ Phân loại task theo category/tag
- 📅 Lọc task theo ngày tạo
- 🔍 Tìm kiếm task
- 📊 Thống kê task hoàn thành
- 💾 Lưu trữ persistent với database
- 🔔 Notifications tự động
- 📱 Inline keyboard để thao tác nhanh
- 🌐 Đa ngôn ngữ (tiếng Anh, tiếng Việt)
- 👥 Chia sẻ task list với người khác

---

### Format
- `Added` - Tính năng mới
- `Changed` - Thay đổi trong tính năng hiện có
- `Deprecated` - Tính năng sắp bị loại bỏ
- `Removed` - Tính năng đã bị loại bỏ
- `Fixed` - Bug fixes
- `Security` - Bảo mật

Dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
