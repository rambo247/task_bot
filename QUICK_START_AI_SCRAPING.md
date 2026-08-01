# 🚀 Quick Start: AI Smart Web Scraping

## 🎯 Bắt đầu trong 3 phút!

### ✅ Yêu cầu
- Bot đã running (đã deploy sẵn trên production)
- Có Telegram account
- Có URL website muốn scrape

---

## 📱 Hướng dẫn sử dụng

### Bước 1: Mở Telegram Bot

```
Tìm: @PHT_TASK_BOT
Hoặc: https://t.me/PHT_TASK_BOT
```

### Bước 2: Tạo Organization (chỉ lần đầu)

```
/start
→ 🏢 Doanh Nghiệp
→ 🏢 Tổ Chức
→ ➕ Tạo Organization Mới

Nhập tên:
"Công ty ABC"
```

✅ **Organization đã được tạo!**

---

### Bước 3: Scrape Website 🌐

```
/start
→ 🏢 Doanh Nghiệp
→ 📥 Import Dữ Liệu
→ 🌐 Scrape Website
```

**Nhập URL:**
```
https://example.com/about
```

⏳ **AI đang phân tích...**

---

### Bước 4: Xem Preview 📋

Bot sẽ hiển thị:

```
🔍 PREVIEW DỮ LIỆU (AI AUTO-LEARNING)

🌐 URL: https://example.com/about
📄 Title: About Us - Example Company
📊 Tổng số: 15 cặp Q&A

🤖 AI đã trích xuất:
   ✅ FAQ sections: 5
   ✅ Headings + Content: 8
   ✅ Direct Q&A: 2

📋 Mẫu dữ liệu:

1. Q: Công ty hoạt động từ năm nào?
   A: Công ty được thành lập từ năm 2015...
   [faq]

2. Q: Tính năng của dịch vụ là gì?
   A: Chúng tôi cung cấp các dịch vụ...
   [heading_content]

3. Q: Liên hệ qua email nào?
   A: Email: info@example.com...
   [direct_qa]

❓ Bạn có muốn thêm dữ liệu này vào AI Knowledge Base?

[✅ Có, thêm vào KB] [❌ Không, hủy bỏ]
```

---

### Bước 5: Xác nhận ✅

Nhấn: **✅ Có, thêm vào KB**

Bot trả lời:

```
✅ ĐÃ LƯU VÀO KNOWLEDGE BASE

🌐 URL: https://example.com/about
📄 Title: About Us - Example Company
📚 Đã học: 15 cặp Q&A

📊 Nguồn dữ liệu:
   • FAQ: 5
   • Headings: 8
   • Q&A trực tiếp: 2

💡 AI có thể trả lời và suy luận từ dữ liệu này!
```

✅ **Hoàn tất!** AI đã học 15 Q&A từ website.

---

### Bước 6: Test AI 🤖

```
/start
→ 🤖 Trợ Lý AI
→ Chat với AI
```

**Hỏi:**
```
Công ty hoạt động từ năm nào?
```

**AI trả lời:**
```
📚 Công ty được thành lập từ năm 2015 
và đã phát triển mạnh mẽ với hơn 1000 
khách hàng doanh nghiệp.

🔗 Nguồn: [About Us](https://example.com/about)
✅ Độ chính xác: Cao

[Từ dữ liệu đã học]
```

🎉 **Thành công!** AI đã trả lời từ kiến thức đã học!

---

## 🎯 Use Cases

### 1. Company Knowledge Base
```
Scrape:
- /about
- /faq
- /services
- /pricing
- /contact

→ AI có thể trả lời về công ty
```

### 2. Product Documentation
```
Scrape:
- /docs/features
- /docs/api
- /docs/faq
- /docs/troubleshooting

→ AI trở thành support assistant
```

### 3. Customer Support
```
Scrape:
- /help
- /support/faq
- /knowledge-base
- /how-to

→ AI tự động trả lời câu hỏi thường gặp
```

### 4. Training Materials
```
Scrape:
- /training/course-1
- /training/course-2
- /wiki

→ AI trở thành training assistant
```

---

## 💡 Tips

### ✅ DO:
- Scrape từ trang có cấu trúc rõ ràng
- Preview trước khi confirm
- Test AI sau khi scrape
- Scrape nhiều trang liên quan

### ❌ DON'T:
- Scrape trang quá lớn (bot limit 100 Q&A)
- Scrape cùng URL nhiều lần
- Skip preview (kiểm tra chất lượng trước)
- Ignore source attribution

---

## 🔍 AI Extract được gì?

### ✅ FAQ Sections
```html
<div class="faq">
  <h3>Question?</h3>
  <p>Answer...</p>
</div>

→ Q&A with high confidence
```

### ✅ Headings + Content
```html
<h2>Our Services</h2>
<p>We provide AI chatbot, automation...</p>

→ "Tính năng của Our Services là gì?"
   "We provide AI chatbot, automation..."
```

### ✅ Meta Data
```html
<title>About Us</title>
<meta name="description" content="Leading AI company...">

→ "About Us là gì?"
   "Leading AI company..."
```

### ✅ Direct Q&A
```html
<p>How to contact us?</p>
<p>Email: info@company.com</p>

→ Q&A pair
```

---

## 📊 Kết quả mong đợi

### Website tốt (có cấu trúc):
- ✅ 50-100 Q&A per page
- ✅ 70-90% từ FAQ và headings
- ✅ High confidence

### Website trung bình:
- ✅ 20-50 Q&A per page
- ✅ 50-70% từ headings và direct Q&A
- ✅ Medium confidence

### Website kém (ít cấu trúc):
- ✅ 5-20 Q&A per page
- ✅ 30-50% từ direct Q&A
- ✅ Low-medium confidence

---

## 🆘 Troubleshooting

### Q: Bot không scrape được?
**A:** Kiểm tra:
- URL có hợp lệ không? (https://...)
- Website có public không?
- Website có quá nhiều JavaScript?

**Thử:**
```
- /about (static content)
- /faq (well-structured)
- /help (simple pages)
```

### Q: Chỉ có ít Q&A?
**A:** Website có thể:
- Không có FAQ sections
- Headings không có content
- Nội dung quá ngắn
- Nhiều JavaScript (bot không render JS)

**Giải pháp:**
- Scrape nhiều pages
- Chọn pages có cấu trúc tốt
- Import thủ công nếu cần

### Q: AI không trả lời chính xác?
**A:** 
- Scrape thêm pages liên quan
- Test với câu hỏi cụ thể hơn
- Check preview để đảm bảo Q&A quality

---

## 🎓 Advanced

### Xem danh sách KB:
```
/start
→ 🤖 Trợ Lý AI
→ 📚 Quản Lý KB
→ 📋 Xem danh sách
```

### Xem web sources:
```
/start
→ 🏢 Doanh Nghiệp
→ 🌐 Web Sources
```

### Import thủ công:
```
/start
→ 🏢 Doanh Nghiệp
→ 📥 Import Dữ Liệu
→ 📋 Paste Text

Format:
Câu hỏi? | Câu trả lời
```

---

## 📚 Tài liệu chi tiết

- **Hướng dẫn đầy đủ:** [AI_SMART_SCRAPING_GUIDE.md](AI_SMART_SCRAPING_GUIDE.md)
- **Summary hoàn thành:** [AI_UPGRADE_COMPLETE.md](AI_UPGRADE_COMPLETE.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## 🎉 Kết luận

**3 bước để có AI thông minh:**

1. ✅ Scrape website (1-2 phút)
2. ✅ Confirm preview (10 giây)
3. ✅ Test AI (30 giây)

→ **Total: ~3 phút** để có AI assistant với kiến thức chuyên môn!

---

**Bot:** @PHT_TASK_BOT  
**Version:** v2.1.0 Enterprise  
**Status:** ✅ Production Ready

---

_Happy scraping! 🚀_
