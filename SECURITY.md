# Security Policy

## Supported Versions

Các phiên bản hiện đang được hỗ trợ với các bản vá bảo mật:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Nếu bạn phát hiện lỗ hổng bảo mật, vui lòng **KHÔNG** tạo public issue.

Thay vào đó, hãy:

1. Gửi email đến: [your.email@example.com] với tiêu đề "Security Vulnerability"
2. Hoặc sử dụng [GitHub Security Advisories](https://github.com/rambo247/task_bot/security/advisories/new)

Trong báo cáo, vui lòng bao gồm:
- Mô tả chi tiết về lỗ hổng
- Các bước để tái hiện
- Tác động tiềm ẩn
- Giải pháp đề xuất (nếu có)

## Best Practices

Khi sử dụng bot:

1. **Không** chia sẻ Bot Token công khai
2. **Luôn** sử dụng biến môi trường (.env) cho thông tin nhạy cảm
3. **Không** commit file .env vào Git
4. Thường xuyên cập nhật dependencies: `pip install --upgrade -r requirements.txt`
5. Sử dụng HTTPS khi deploy
6. Giới hạn quyền truy cập bot chỉ cho người dùng tin cậy

## Bảo mật Bot Token

Bot token của bạn giống như mật khẩu. Nếu bị lộ:

1. Truy cập [@BotFather](https://t.me/BotFather)
2. Gửi lệnh `/mybots`
3. Chọn bot của bạn
4. Chọn "API Token"
5. Chọn "Revoke current token"
6. Nhận token mới và cập nhật vào environment variables

## Cập nhật

Chúng tôi sẽ thông báo về các vấn đề bảo mật nghiêm trọng qua:
- GitHub Security Advisories
- Release Notes
- README updates

Cảm ơn bạn đã giúp giữ an toàn cho cộng đồng! 🔒
