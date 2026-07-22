# Contributing to Telegram Task Bot

Cảm ơn bạn quan tâm đến việc đóng góp cho dự án! 🎉

## Cách đóng góp

### Báo lỗi (Bug Report)
1. Kiểm tra xem lỗi đã được báo cáo chưa trong [Issues](https://github.com/rambo247/task_bot/issues)
2. Nếu chưa, tạo issue mới với:
   - Mô tả chi tiết lỗi
   - Các bước tái hiện lỗi
   - Kết quả mong đợi vs kết quả thực tế
   - Screenshot (nếu có)

### Đề xuất tính năng
1. Tạo issue với label `enhancement`
2. Mô tả chi tiết tính năng bạn muốn
3. Giải thích tại sao tính năng này hữu ích

### Pull Request
1. Fork repository
2. Tạo branch mới: `git checkout -b feature/ten-tinh-nang`
3. Commit changes: `git commit -m 'Thêm tính năng ABC'`
4. Push lên branch: `git push origin feature/ten-tinh-nang`
5. Tạo Pull Request

## Code Style
- Sử dụng 4 spaces cho indentation
- Đặt tên biến/hàm rõ ràng, dễ hiểu
- Thêm comments cho logic phức tạp
- Tuân theo PEP 8 cho Python code

## Testing
Trước khi submit PR, hãy test:
- Các lệnh cơ bản: /start, /add, /list, /done, /delete, /clear
- Edge cases: danh sách rỗng, số thứ tự không hợp lệ
- Bot hoạt động với nhiều user đồng thời

Cảm ơn bạn đã đóng góp! 💖
