# 🤖 AI Smart Web Scraping & Knowledge Management

## 📋 Tổng Quan

Phiên bản v2.1.0 đã được nâng cấp với khả năng **AI tự học thông minh** từ các nguồn web. Hệ thống có thể:

✅ **Tự động trích xuất kiến thức** từ website  
✅ **Phân tích cấu trúc nội dung** (FAQ, headings, meta)  
✅ **Tạo Q&A thông minh** từ nội dung  
✅ **Lưu trữ với metadata đầy đủ** (nguồn, URL, độ tin cậy)  
✅ **Suy luận từ kiến thức đã học** khi trả lời  
✅ **Trích dẫn nguồn** khi trả lời câu hỏi  

---

## 🚀 Cách Sử Dụng

### 1️⃣ Scrape Website

```
/start → 🏢 Doanh Nghiệp → 📥 Import Dữ Liệu → 🌐 Scrape Website
```

**Nhập URL** → Bot sẽ:
- ✅ Tự động phát hiện **FAQ sections**
- ✅ Trích xuất từ **Headings + Content**
- ✅ Parse **Meta descriptions**
- ✅ Nhận dạng **Direct Q&A patterns**
- ✅ Tạo câu hỏi từ headings thông minh

**Preview** → Hiển thị:
- 🌐 URL và Title
- 📊 Tổng số Q&A tìm được
- 🤖 Breakdown theo nguồn (FAQ, Headings, Meta, etc.)
- 📋 Mẫu 3 Q&A đầu tiên với source label

**Xác nhận** → Lưu vào Knowledge Base với đầy đủ metadata

---

## 🧠 AI Intelligent Extraction

### 📌 Các Nguồn Dữ Liệu

| Nguồn | Mô Tả | Priority |
|-------|-------|----------|
| **FAQ** | Sections có class="faq" | ⭐⭐⭐ Cao nhất |
| **Heading + Content** | h1-h4 + paragraphs sau | ⭐⭐ Cao |
| **Meta Description** | Title + meta description | ⭐ Trung bình |
| **Direct Q&A** | Câu hỏi (?) + câu trả lời | ⭐ Trung bình |

### 🤖 Tạo Câu Hỏi Tự Động

Từ headings như:
- "Về chúng tôi" → "Giới thiệu về Về chúng tôi?"
- "Lợi ích sử dụng AI" → "Lợi ích của Lợi ích sử dụng AI là gì?"
- "Tính năng chatbot" → "Tính năng của Tính năng chatbot là gì?"
- "Liên hệ" → "Thông tin liên hệ Liên hệ?"
- "Giá dịch vụ" → "Giá Giá dịch vụ là bao nhiêu?"

---

## 💾 Metadata & Tracking

### Mỗi Q&A lưu với:

```json
{
  "question": "...",
  "answer": "...",
  "keywords": ["ai", "chatbot", "tính năng"],
  "source": "web_heading_content",
  "source_url": "https://example.com/about",
  "source_title": "About Us - Company",
  "created_at": "2026-08-01T16:31:24.000Z",
  "updated_at": "2026-08-01T16:31:24.000Z",
  "usage_count": 0,
  "last_used": null,
  "confidence": 0.85
}
```

### Web Sources tracking:

```json
{
  "id": "source_xxx",
  "url": "https://example.com",
  "title": "Company Website",
  "type": "scraped",
  "last_scraped": "2026-08-01T16:31:24.000Z",
  "status": "success",
  "items_count": 25,
  "source_breakdown": {
    "faq": 10,
    "heading_content": 12,
    "meta": 1,
    "direct_qa": 2
  },
  "scraped_by": 309221502
}
```

---

## 🎯 AI Response với Nguồn

### Khi AI trả lời:

**Từ Knowledge Base:**
```
📚 [Câu trả lời]

🔗 Nguồn: [Company Website](https://example.com)
✅ Độ chính xác: Cao

[Từ dữ liệu đã học]
```

**Từ AI Reasoning:**
```
🤖 [Câu trả lời có suy luận]

Suy luận từ:
- Company giới thiệu về AI chatbot...
- Website nói về tính năng automation...

[AI suy luận]
```

---

## 📊 Usage Analytics

### Hệ thống track:
- ✅ **usage_count**: Số lần Q&A được sử dụng
- ✅ **last_used**: Thời điểm sử dụng gần nhất
- ✅ **confidence**: Độ tin cậy của kết quả

### AI ưu tiên:
1. High usage items (được dùng nhiều)
2. Recent items (mới cập nhật)
3. High confidence sources (FAQ > Heading > Direct)

---

## 🔍 Smart Search

### Keyword Matching:
- Trích xuất keywords từ câu hỏi
- So sánh với keywords trong KB
- Bonus points cho nguồn đáng tin cậy

### Source Priority:
```
web_faq           → +0.5 điểm
web_heading       → +0.3 điểm
web_heading_content → +0.3 điểm
manual           → +0.0 điểm
```

### Confidence Levels:
- **Cao** (≥90%): Exact match
- **Trung bình** (≥60%): Good keyword match
- **Thấp** (<60%): Fuzzy match

---

## 📝 Ví Dụ Thực Tế

### Input URL:
```
https://company.com/about
```

### Bot Extract:

**✅ FAQ Section:**
```
Q: Công ty hoạt động từ năm nào?
A: Công ty được thành lập từ năm 2015...
[faq]
```

**✅ Heading + Content:**
```
Q: Tính năng của AI Chatbot là gì?
A: AI Chatbot cung cấp các tính năng như...
[heading_content]
```

**✅ Meta Data:**
```
Q: About Us - Company là gì?
A: Chúng tôi là công ty hàng đầu về AI...
[meta]
```

### AI Response:
```
User: Công ty hoạt động từ năm nào?

Bot:
📚 Công ty được thành lập từ năm 2015 
và đã phát triển mạnh mẽ với hơn 1000 
khách hàng doanh nghiệp.

🔗 Nguồn: [About Us](https://company.com/about)
✅ Độ chính xác: Cao

[Từ dữ liệu đã học]
```

---

## 🛠️ Technical Details

### Libraries:
- **BeautifulSoup 4.9.3**: HTML parsing (Python 3.6 compatible)
- **lxml 5.4.0**: Fast XML/HTML processing
- **validators 0.20.0**: URL validation
- **requests**: HTTP requests

### Performance:
- ⚡ Up to **100 Q&A** per page
- 🚀 **Deduplication** tự động
- 💾 **JSON persistence** với auto-backup
- 📊 **Real-time analytics** tracking

### Data Structure:
```
data/
  ├── ai_knowledge_base.json   # All KB entries with metadata
  ├── web_sources.json         # Web scraping history
  └── organizations.json       # Org-level web sources

backups/
  └── backup_20260801_163124.zip  # Daily backups (7-day retention)
```

---

## 🎓 Best Practices

### ✅ DO:
- Scrape từ các trang có cấu trúc rõ ràng (FAQ, About Us, Features)
- Kiểm tra preview trước khi confirm
- Sử dụng AI để test kiến thức đã học
- Review usage analytics để tối ưu KB

### ❌ DON'T:
- Scrape từ các trang quá lớn (>100 Q&A sẽ bị limit)
- Import dữ liệu không chính xác
- Spam scraping cùng 1 URL nhiều lần
- Ignore source attribution

---

## 📈 Roadmap

### Coming Soon:
- [ ] **AI-powered Q&A generation** từ paragraphs (dùng GPT-4o)
- [ ] **Semantic search** thay vì keyword matching
- [ ] **Multi-language support** (EN, VI, etc.)
- [ ] **Image OCR** extraction
- [ ] **PDF scraping** support
- [ ] **Scheduled re-scraping** để update knowledge
- [ ] **Knowledge graph** visualization
- [ ] **Export KB** to various formats

---

## 🆘 Troubleshooting

### Q: Bot không scrape được website?
**A:** Kiểm tra:
- URL có hợp lệ không?
- Website có block robots không?
- BeautifulSoup 4.9.3 đã cài chưa?

### Q: Tại sao chỉ có ít Q&A được extract?
**A:** Website có thể:
- Không có cấu trúc FAQ rõ ràng
- Headings không có content đi kèm
- Nội dung quá ngắn (<10 chars)
- Bị filter bởi heuristics

### Q: AI không trích dẫn nguồn?
**A:** Đảm bảo:
- Dữ liệu được scrape từ web (có source_url)
- Không phải manual entry
- KB search tìm thấy exact/fuzzy match

### Q: Làm sao xem analytics?
**A:** 
```
/start → 🤖 Trợ Lý AI → 📚 Quản Lý KB → 📋 Xem danh sách
```
→ Hiển thị usage_count và confidence

---

## 💡 Tips & Tricks

### 1. Scrape Hiệu Quả:
- Chọn trang có FAQ sections
- Ưu tiên trang About Us, Features, Pricing
- Avoid pages với nhiều ads/scripts

### 2. Tối Ưu KB:
- Import từ nhiều nguồn khác nhau
- Review và xóa dữ liệu duplicate
- Update KB định kỳ

### 3. Sử Dụng AI:
- Test với các câu hỏi liên quan
- Quan sát source attribution
- Feedback để improve extraction

---

## 📞 Support

- 📧 Email: support@company.com
- 💬 Telegram: @PHT_TASK_BOT
- 🐛 Issues: https://github.com/rambo247/task_bot/issues

---

**Version:** v2.1.0 Enterprise  
**Last Updated:** 2026-08-01  
**Author:** AI Development Team

---

_Made with ❤️ by AI-powered automation_
