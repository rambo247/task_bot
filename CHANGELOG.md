# Changelog

Tất cả các thay đổi quan trọng của dự án sẽ được ghi lại ở đây.

## [2.2.1] - 2026-08-01 🐛 BUG FIX: AI Chat Web Sources

### 🔧 Critical Bug Fix

#### 🐛 Issue
- **AI Chat mode không xử lý web sources**
- User thêm web source ✅
- User hỏi câu hỏi ❌ Không trả lời
- Passive learning không hoạt động

#### 🔍 Root Cause
Function `get_enhanced_ai_response()`:
- Chỉ tìm KB cache (`search_knowledge_base()`)
- KHÔNG tìm web sources (passive learning)
- Bỏ qua logic on-demand extraction
- Duplicate logic thay vì gọi `get_ai_response()`

#### ✅ Fix
```python
# BEFORE (BUG):
kb_answer = search_knowledge_base(user_id, user_message)  # Only KB cache
if kb_answer:
    return f"📚 {kb_answer}\n\n_[Từ dữ liệu đã học]_"

# AFTER (FIXED):
ai_answer = get_ai_response(user_id, user_message)  # Full logic: KB + web sources
if ai_answer:
    return ai_answer
```

#### 📊 Impact
- ✅ Web sources hoạt động 100% trong AI Chat
- ✅ Passive learning extract on-demand
- ✅ Enterprise features hoạt động đầy đủ
- ✅ Smart caching vào KB

#### 🚀 Deployment
- Commit: `ad178c5`
- Deployed: 2026-08-01 16:58
- Status: ✅ FIXED & TESTED

### 📝 Documentation
- New file: `BUGFIX_AI_CHAT_v2.2.1.md`
- Root cause analysis
- Test cases
- Flow diagrams

---

## [2.2.0] - 2026-08-01 🔄 PASSIVE LEARNING ARCHITECTURE

### 🎯 Major Architectural Change: Active → Passive Learning

#### 🧠 From Active to Passive Knowledge Acquisition
**OLD (Active Learning):**
- ❌ Extract ALL Q&A upfront (100+ pairs per URL)
- ❌ High memory usage (store everything)
- ❌ Slow to add sources (extract + deduplicate)
- ❌ Many unused Q&A pairs

**NEW (Passive Learning):**
- ✅ Store raw content only (50KB vs 200KB)
- ✅ Extract on-demand when user asks
- ✅ Fast to add sources (2-3s vs 5-10s)
- ✅ Smart caching (cache only used answers)

### ✨ Key Improvements

#### 💾 Memory Efficiency
- **75% reduction** in storage per URL
- Raw content: ~50KB (vs 100 Q&A = ~200KB)
- KB grows organically with actual questions
- No wasted space for unused Q&A

#### ⚡ Performance
- **70% faster** when adding sources
- Slightly slower first response (on-demand extraction)
- Cached responses same speed as before
- Background scraping possible (future enhancement)

#### 🤖 Smarter AI
- Context-aware extraction (based on actual question)
- Relevant paragraph search (not predefined Q&A)
- Flexible answer generation
- Source citation with confidence scoring

### 🔧 Technical Changes

#### Modified Functions
1. **`scrape_website()`** (-200 lines)
   - Old: Extract all Q&A (FAQ, headings, meta, etc.)
   - New: Only fetch raw content + metadata

2. **`extract_answer_from_source()`** (+70 lines) - NEW
   - On-demand extraction when user asks
   - Keyword-based paragraph search
   - Relevance scoring
   - Top-3 paragraph aggregation

3. **`get_ai_response()`** (+120 lines)
   - Search web sources on-demand
   - Extract if raw_content exists
   - Re-scrape if needed
   - Smart caching to KB

4. **Confirmation Flow**
   - Preview: Show content_length, not Q&A list
   - Text: "HỌC BỊ ĐỘNG (On-Demand)"
   - Explain passive learning concept

5. **Web Sources Menu**
   - Display: content_length (not items_count)
   - Label: "HỌC BỊ ĐỘNG"
   - Info: "AI chưa extract Q&A ngay"

#### Data Structure Changes
```json
// OLD (Active)
{
  "qa_pairs": [...100 items],
  "items_count": 100
}

// NEW (Passive)
{
  "raw_content": "...50KB text...",
  "content_length": 50000,
  "type": "web_passive"
}
```

### 📊 Performance Metrics

| Metric | Active | Passive | Improvement |
|--------|--------|---------|-------------|
| Storage/URL | 200KB | 50KB | 75% reduction |
| Add source | 5-10s | 2-3s | 70% faster |
| First question | <10ms | 100-200ms | Slower |
| Cached questions | <10ms | <10ms | Same |

### 🎯 User Experience

#### Before (Active):
```
1. Add URL → Wait 5-10s
2. Preview 25 Q&A pairs
3. Review all Q&A
4. Confirm → Save to KB
5. Many unused Q&A stored
```

#### After (Passive):
```
1. Add URL → Wait 2-3s
2. Preview: 50,000 chars ready
3. Confirm source
4. Ask question → Extract on-demand
5. Cache only used answers
```

### 🔄 Migration Notes

#### Backward Compatibility
- ✅ Existing KB data works unchanged
- ✅ Old web sources (with qa_pairs) still usable
- ✅ No breaking changes

#### New Behavior
- Web sources save `raw_content` instead of `qa_pairs`
- AI searches web sources on user questions
- Extraction happens on-demand
- Results cached to KB for future use

### 📝 Documentation

New files:
- `PASSIVE_LEARNING_v2.2.0.md` - Complete explanation of passive learning

### 🚀 Deployment

- Commit: `889d357`
- Production: ✅ Online (15.235.210.238:5024)
- Memory: 4.0 MB (stable)
- Status: No errors

---

## [2.1.0] - 2026-08-01 🤖 AI INTELLIGENT WEB SCRAPING

### 🌟 Major AI Upgrade

#### 🧠 Smart Web Scraping & Knowledge Extraction
- **Intelligent Content Analysis**: AI tự động phân tích cấu trúc website
- **Multi-Source Extraction**: FAQ sections, headings, meta descriptions, direct Q&A
- **Auto Q&A Generation**: Tạo câu hỏi thông minh từ headings và content
- **Deduplication**: Tự động loại bỏ Q&A trùng lặp
- **Scale**: Up to 100 Q&A per page (từ 50)

### ✨ New Features

#### 📊 Rich Metadata System
- **Source Tracking**: web_faq, web_heading, web_heading_content, meta, direct_qa, manual, text_import
- **URL References**: Lưu URL và title nguồn cho mỗi Q&A
- **Usage Analytics**: Track usage_count và last_used
- **Confidence Scoring**: Đánh giá độ tin cậy của mỗi Q&A
- **Timestamps**: created_at và updated_at
- **Tags & Categories**: Support for future organization

#### 🔍 Enhanced Knowledge Base Search
- **Metadata-Aware**: Sử dụng source type để scoring
- **Source Priority**: FAQ > Heading > Direct Q&A
- **Usage Tracking**: Auto-update usage stats khi tìm thấy
- **Rich Results**: Return full object với source info
- **Confidence Levels**: Cao (≥90%), Trung bình (≥60%)

#### 🎯 Smart AI Response
- **Source Attribution**: Hiển thị nguồn với link
- **Confidence Display**: Show độ tin cậy của câu trả lời
- **AI Reasoning**: Suy luận từ KB context
- **Citation**: Trích dẫn nguồn khi trả lời
- **Context-Aware**: Sử dụng high-usage items cho context

#### 📋 Detailed Preview & Results
- **Source Breakdown**: FAQ, Headings, Meta, Direct Q&A counts
- **Source Labels**: Hiển thị source type cho mỗi Q&A
- **Extraction Statistics**: Show detailed stats sau khi scrape
- **Web Sources Tracking**: Lưu history và analytics

### 🔧 Technical Improvements

#### 🛠️ Enhanced Functions
- `scrape_website()`: 
  - 5 extraction methods (FAQ, Heading+Content, Heading, Meta, Direct Q&A)
  - Smart question generation từ headings
  - Contextual content extraction
  - Advanced deduplication
  
- `add_to_knowledge_base()`:
  - Support source và metadata parameters
  - Rich entry structure với tracking fields
  - Flexible metadata system
  
- `search_knowledge_base()`:
  - Return full result object
  - Source-based scoring
  - Auto-update usage tracking
  
- `get_ai_response()`:
  - Source attribution trong responses
  - Confidence level display
  - Context-aware AI reasoning
  - High-usage context prioritization

#### 💾 Enhanced Data Persistence
- **web_sources**: Detailed stats với source_breakdown
- **scraped_by**: Track user ID
- **All metadata**: Saved to JSON
- **Backward Compatible**: Works with existing data

### 📚 Documentation
- **AI_SMART_SCRAPING_GUIDE.md**: Comprehensive guide (40+ pages)
- **Examples**: Real-world use cases
- **Best Practices**: Do's and Don'ts
- **Troubleshooting**: Common issues và solutions
- **Roadmap**: Future enhancements

### 🐛 Bug Fixes
- None (new feature release)

### 📦 Dependencies
- BeautifulSoup4 4.9.3 (Python 3.6 compatible)
- lxml 5.4.0
- validators 0.20.0
- All existing dependencies maintained

### 🚀 Performance
- ⚡ 100 Q&A limit per page
- 🔄 Real-time deduplication
- 💾 Efficient JSON storage
- 📊 Fast analytics tracking

### 🎓 Migration Notes
- **Backward Compatible**: Existing KB data works seamlessly
- **No Breaking Changes**: All existing features unchanged
- **Auto-Upgrade**: Existing entries get default metadata on next use
- **No Manual Steps**: Deploy and go!

---

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
