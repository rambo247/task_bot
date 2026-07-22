# Changelog

Tất cả các thay đổi quan trọng của dự án sẽ được ghi lại ở đây.

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
