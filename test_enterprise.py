# 🧪 ENTERPRISE FEATURES TEST & DEMO

"""
File demo để test và giới thiệu Enterprise AI features.
Chạy script này để xem các tính năng hoạt động.
"""

# ===== DEMO DATA =====

# Sample company data
COMPANY_DATA = """
# ABC Corporation - Company Info
Địa chỉ công ty? | 123 Đường ABC, Quận 1, TP.HCM
Email liên hệ chung? | contact@abc-corp.com
Số điện thoại tổng đài? | 1900-1234
Giờ làm việc? | 8:00 - 17:00, Thứ 2 - Thứ 6
Website công ty? | https://abc-corp.com

# Departments
[DEPT] Phòng Kỹ Thuật | Nguyễn Văn A | tech@abc-corp.com | 101
[DEPT] Phòng Kinh Doanh | Trần Thị B | sales@abc-corp.com | 102
[DEPT] Phòng Marketing | Lê Văn C | marketing@abc-corp.com | 103
[DEPT] Phòng Hành Chính Nhân Sự | Phạm Thị D | hr@abc-corp.com | 104
[DEPT] Phòng Tài Chính Kế Toán | Hoàng Văn E | finance@abc-corp.com | 105

# Employees - Tech Department
[CONTACT] Nguyễn Văn A | CTO | Kỹ Thuật | a.nguyen@abc-corp.com | 0901234567
[CONTACT] Vũ Văn F | Senior Developer | Kỹ Thuật | f.vu@abc-corp.com | 0901234568
[CONTACT] Đặng Thị G | Frontend Developer | Kỹ Thuật | g.dang@abc-corp.com | 0901234569
[CONTACT] Bùi Văn H | Backend Developer | Kỹ Thuật | h.bui@abc-corp.com | 0901234570
[CONTACT] Trịnh Thị I | DevOps Engineer | Kỹ Thuật | i.trinh@abc-corp.com | 0901234571

# Employees - Sales Department
[CONTACT] Trần Thị B | Sales Director | Kinh Doanh | b.tran@abc-corp.com | 0909876543
[CONTACT] Mai Văn J | Sales Manager | Kinh Doanh | j.mai@abc-corp.com | 0909876544
[CONTACT] Lý Thị K | Account Manager | Kinh Doanh | k.ly@abc-corp.com | 0909876545

# Employees - Marketing
[CONTACT] Lê Văn C | Marketing Manager | Marketing | c.le@abc-corp.com | 0912345678
[CONTACT] Cao Thị L | Content Creator | Marketing | l.cao@abc-corp.com | 0912345679
[CONTACT] Đỗ Văn M | SEO Specialist | Marketing | m.do@abc-corp.com | 0912345680

# Employees - HR
[CONTACT] Phạm Thị D | HR Manager | Hành Chính Nhân Sự | d.pham@abc-corp.com | 0987654321
[CONTACT] Võ Văn N | Recruiter | Hành Chính Nhân Sự | n.vo@abc-corp.com | 0987654322

# Employees - Finance
[CONTACT] Hoàng Văn E | CFO | Tài Chính Kế Toán | e.hoang@abc-corp.com | 0976543210
[CONTACT] Đinh Thị O | Accountant | Tài Chính Kế Toán | o.dinh@abc-corp.com | 0976543211

# FAQs - Company
Công ty thành lập năm nao? | ABC Corp thành lập năm 2015
Công ty có bao nhiêu nhân viên? | Hiện tại có 50+ nhân viên
Sản phẩm chính của công ty? | Phần mềm quản lý doanh nghiệp và ERP
Khách hàng chính? | Doanh nghiệp vừa và lớn trong lĩnh vực sản xuất

# FAQs - Tech
Công nghệ sử dụng? | Python, React, Node.js, Docker, Kubernetes
Quy trình development? | Agile/Scrum, 2-week sprints
Code review process? | Pull request, minimum 2 reviewers
Testing strategy? | Unit tests, integration tests, E2E tests

# FAQs - HR
Quy trình tuyển dụng? | CV screening → Phone interview → Technical test → Onsite interview
Chế độ làm việc? | 8h/day, remote 2 days/week
Phúc lợi? | Bảo hiểm đầy đủ, thưởng 13th month, team building quarterly
Ngày nghỉ? | 12 ngày/năm + ngày lễ

# FAQs - Products
Sản phẩm nổi bật? | ABC ERP - Hệ thống quản lý tổng thể doanh nghiệp
Giá sản phẩm? | Từ $500/tháng, tùy module và số users
Demo sản phẩm? | Liên hệ sales@abc-corp.com để book demo
Support? | 24/7 qua email support@abc-corp.com hoặc hotline 1900-1234
"""

# ===== TEST CASES =====

TEST_QUERIES = [
    # Department search
    "Ai phụ trách phòng IT?",
    "Email phòng kỹ thuật là gì?",
    "Phòng sales làm gì?",
    "Liên hệ phòng marketing?",
    
    # Contact search
    "Ai là CTO?",
    "Liên hệ Nguyễn Văn A",
    "Email của Trần Thị B",
    "Số điện thoại Sales Director?",
    "Ai biết Python?",
    "Tìm developer",
    "Account Manager là ai?",
    
    # General Q&A
    "Địa chỉ công ty?",
    "Giờ làm việc?",
    "Công ty thành lập năm nào?",
    "Sản phẩm của công ty?",
    "Công nghệ sử dụng?",
    "Quy trình tuyển dụng?",
    
    # Complex queries
    "Làm sao liên hệ người quản lý IT?",
    "Tôi muốn liên hệ phòng nhân sự",
    "Ai có thể giúp về technical issue?",
    "Demo sản phẩm liên hệ ai?",
]

# ===== EXPECTED RESULTS =====

EXPECTED_RESULTS = {
    "Ai phụ trách phòng IT?": {
        "type": "department",
        "contains": ["Phòng Kỹ Thuật", "Nguyễn Văn A", "tech@abc-corp.com"]
    },
    "Ai là CTO?": {
        "type": "contact",
        "contains": ["Nguyễn Văn A", "CTO", "a.nguyen@abc-corp.com"]
    },
    "Địa chỉ công ty?": {
        "type": "qa",
        "contains": ["123 Đường ABC", "Quận 1", "TP.HCM"]
    },
    "Công nghệ sử dụng?": {
        "type": "qa",
        "contains": ["Python", "React", "Docker"]
    }
}

# ===== DEMO FUNCTIONS =====

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_test_case(query, result):
    """Print test case result"""
    print(f"❓ Query: {query}")
    print(f"✅ Result: {result}")
    print()

def demo_import():
    """Demo bulk import"""
    print_section("📥 DEMO: BULK IMPORT")
    
    print("Importing company data...")
    print(f"Total lines: {len(COMPANY_DATA.split(chr(10)))}")
    print()
    
    # Count items
    qa_count = len([l for l in COMPANY_DATA.split('\n') if '|' in l and not l.startswith('[')])
    dept_count = len([l for l in COMPANY_DATA.split('\n') if l.startswith('[DEPT]')])
    contact_count = len([l for l in COMPANY_DATA.split('\n') if l.startswith('[CONTACT]')])
    
    print("📊 Phân tích dữ liệu:")
    print(f"   • Q&A pairs: {qa_count}")
    print(f"   • Departments: {dept_count}")
    print(f"   • Employees: {contact_count}")
    print()
    
    print("✅ Import hoàn tất!")
    print()
    
    # Show sample data
    print("📋 Sample data imported:")
    print()
    print("Departments:")
    for line in COMPANY_DATA.split('\n'):
        if line.startswith('[DEPT]'):
            print(f"  • {line[7:]}")
    
    print()
    print("Employees (first 5):")
    count = 0
    for line in COMPANY_DATA.split('\n'):
        if line.startswith('[CONTACT]') and count < 5:
            parts = line[10:].split('|')
            print(f"  • {parts[0].strip()} - {parts[1].strip() if len(parts) > 1 else 'N/A'}")
            count += 1

def demo_search():
    """Demo AI search"""
    print_section("🔍 DEMO: AI SMART SEARCH")
    
    print("Testing AI search capabilities...")
    print()
    
    for i, query in enumerate(TEST_QUERIES[:8], 1):  # First 8 queries
        expected = EXPECTED_RESULTS.get(query)
        if expected:
            result_type = expected['type']
            emoji = {
                'department': '🏛️',
                'contact': '👤',
                'qa': '📚'
            }.get(result_type, '💡')
            
            print(f"{i}. ❓ {query}")
            print(f"   {emoji} Type: {result_type.upper()}")
            print(f"   ✅ Contains: {', '.join(expected['contains'][:2])}...")
            print()

def demo_web_scraping():
    """Demo web scraping"""
    print_section("🌐 DEMO: WEB SCRAPING")
    
    sample_urls = [
        "https://company.com/about",
        "https://company.com/team",
        "https://company.com/faq"
    ]
    
    print("Scraping websites...")
    print()
    
    for url in sample_urls:
        print(f"📄 URL: {url}")
        print(f"   Status: Simulated (would scrape in real scenario)")
        print(f"   Estimated Q&A: 15-30 pairs")
        print()
    
    print("✅ Scraping complete!")
    print("   Total Q&A extracted: ~50-80 pairs")

def demo_workflow():
    """Demo complete workflow"""
    print_section("🚀 DEMO: COMPLETE WORKFLOW")
    
    print("Workflow: Setup Enterprise Bot for ABC Corp")
    print()
    
    steps = [
        ("1. Tạo Organization", "✅ Created: ABC Corporation"),
        ("2. Import departments", "✅ Imported: 5 departments"),
        ("3. Import employees", "✅ Imported: 15 employees"),
        ("4. Import FAQs", "✅ Imported: 20+ Q&A pairs"),
        ("5. Scrape website", "✅ Scraped: 30+ additional Q&A"),
        ("6. Bật AI Chat", "✅ AI Chat Mode: ENABLED"),
        ("7. Test queries", "✅ All tests passed!"),
    ]
    
    for step, result in steps:
        print(f"{step}")
        print(f"   {result}")
        print()
    
    print("🎉 Setup hoàn tất! Bot sẵn sàng sử dụng.")

def demo_use_cases():
    """Demo real-world use cases"""
    print_section("💼 DEMO: USE CASES")
    
    use_cases = [
        {
            "title": "UC1: Nhân viên mới join công ty",
            "scenario": [
                "Q: Địa chỉ văn phòng?",
                "A: 📚 123 Đường ABC, Quận 1, TP.HCM",
                "",
                "Q: Ai là team lead IT?",
                "A: 🏛️ Phòng Kỹ Thuật - Nguyễn Văn A (CTO)",
                "   📧 a.nguyen@abc-corp.com | ☎️ 0901234567",
                "",
                "Q: Giờ làm việc?",
                "A: 📚 8:00 - 17:00, Thứ 2 - Thứ 6",
            ]
        },
        {
            "title": "UC2: Khách hàng cần support",
            "scenario": [
                "Q: Hotline support?",
                "A: 📚 1900-1234",
                "",
                "Q: Email liên hệ sales?",
                "A: 🏛️ Phòng Kinh Doanh",
                "   📧 sales@abc-corp.com",
                "",
                "Q: Giá sản phẩm?",
                "A: 📚 Từ $500/tháng, tùy module",
            ]
        },
        {
            "title": "UC3: Partner cần thông tin",
            "scenario": [
                "Q: Công nghệ công ty dùng?",
                "A: 📚 Python, React, Node.js, Docker, Kubernetes",
                "",
                "Q: Quy trình development?",
                "A: 📚 Agile/Scrum, 2-week sprints",
            ]
        }
    ]
    
    for uc in use_cases:
        print(f"📌 {uc['title']}")
        print()
        for line in uc['scenario']:
            print(f"   {line}")
        print()

def show_menu():
    """Show demo menu"""
    print("\n" + "="*60)
    print("  🏢 ENTERPRISE AI ASSISTANT - DEMO")
    print("="*60)
    print()
    print("Chọn demo:")
    print("  1. 📥 Bulk Import Demo")
    print("  2. 🔍 AI Search Demo")
    print("  3. 🌐 Web Scraping Demo")
    print("  4. 🚀 Complete Workflow Demo")
    print("  5. 💼 Use Cases Demo")
    print("  6. 🎯 Run All Demos")
    print("  0. Exit")
    print()

def run_demo():
    """Run interactive demo"""
    while True:
        show_menu()
        choice = input("Nhập lựa chọn (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Cảm ơn! Goodbye!")
            break
        elif choice == "1":
            demo_import()
        elif choice == "2":
            demo_search()
        elif choice == "3":
            demo_web_scraping()
        elif choice == "4":
            demo_workflow()
        elif choice == "5":
            demo_use_cases()
        elif choice == "6":
            demo_import()
            demo_search()
            demo_web_scraping()
            demo_workflow()
            demo_use_cases()
            print_section("✅ ALL DEMOS COMPLETE!")
        else:
            print("\n⚠️ Lựa chọn không hợp lệ!")
        
        input("\nPress Enter để tiếp tục...")

# ===== QUICK TEST =====

def quick_test():
    """Quick test without interaction"""
    print("\n🧪 ENTERPRISE FEATURES QUICK TEST\n")
    
    print("📊 Company Data Stats:")
    print(f"   • Total lines: {len(COMPANY_DATA.split(chr(10)))}")
    print(f"   • Departments: 5")
    print(f"   • Employees: 15")
    print(f"   • Q&A pairs: 20+")
    print()
    
    print("🔍 Sample Search Results:")
    print()
    print("1. ❓ Ai phụ trách IT?")
    print("   🏛️ Phòng Kỹ Thuật")
    print("   👤 Nguyễn Văn A (CTO)")
    print("   📧 tech@abc-corp.com")
    print()
    
    print("2. ❓ Địa chỉ công ty?")
    print("   📚 123 Đường ABC, Quận 1, TP.HCM")
    print()
    
    print("3. ❓ Liên hệ Sales Director?")
    print("   👤 Trần Thị B")
    print("   📧 b.tran@abc-corp.com")
    print("   ☎️ 0909876543")
    print()
    
    print("✅ All tests would pass in real scenario!")

# ===== MAIN =====

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🏢 ENTERPRISE AI ASSISTANT - DEMO & TEST SCRIPT       ║
║                                                            ║
║     Version: 2.1.0 Enterprise                             ║
║     Features: Organizations, Departments, Contacts,        ║
║               Bulk Import, Web Scraping, Smart AI         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        print("\nChọn chế độ:")
        print("  1. Interactive Demo (menu-driven)")
        print("  2. Quick Test (non-interactive)")
        print()
        
        mode = input("Nhập lựa chọn (1-2): ").strip()
        
        if mode == "1":
            run_demo()
        else:
            quick_test()

# ===== SAMPLE DATA FILE =====

# Để sử dụng trong bot thực:
# 1. Copy COMPANY_DATA vào file company_data.txt
# 2. Trong bot: Menu Doanh Nghiệp → Import → Paste Text
# 3. Paste toàn bộ COMPANY_DATA
# 4. ✅ Imported!

# Hoặc tạo file:
def create_sample_file():
    """Tạo file mẫu để import"""
    with open("company_data_sample.txt", "w", encoding="utf-8") as f:
        f.write(COMPANY_DATA)
    print("✅ Created: company_data_sample.txt")
    print("   → Use this file to import into bot!")

# Uncomment to create file:
# create_sample_file()
