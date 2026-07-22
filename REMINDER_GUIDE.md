# ⏰ Hướng dẫn sử dụng Tính năng Nhắc nhở

## 📋 Tổng quan

Bot Task đã được nâng cấp với tính năng **Nhắc nhở tự động**! Bot sẽ tự động gửi thông báo khi đến giờ bạn đã đặt.

---

## 🚀 Cách sử dụng

### 1️⃣ Thêm công việc như bình thường

```
/add Họp với khách hàng
```

Bot sẽ trả lời:
```
✅ Đã thêm công việc: 'Họp với khách hàng'

💡 Đặt nhắc nhở với:
/remind 1 [thời gian]
```

---

### 2️⃣ Đặt nhắc nhở cho công việc

Có **4 cách** để đặt thời gian nhắc nhở:

#### **Cách 1: Giờ phút trong ngày (HH:MM)**
```
/remind 1 14:30
```
- Nhắc vào **14:30 hôm nay**
- Nếu 14:30 đã qua → Nhắc vào **14:30 ngày mai**

#### **Cách 2: Ngày giờ cụ thể (YYYY-MM-DD HH:MM)**
```
/remind 1 2026-07-23 09:00
```
- Nhắc vào **9:00 sáng ngày 23/07/2026**

#### **Cách 3: Sau X phút (Xm)**
```
/remind 1 30m
```
- Nhắc sau **30 phút** kể từ bây giờ

```
/remind 1 90m
```
- Nhắc sau **90 phút** (1.5 giờ)

#### **Cách 4: Sau X giờ (Xh)**
```
/remind 1 2h
```
- Nhắc sau **2 giờ**

```
/remind 1 24h
```
- Nhắc sau **24 giờ** (1 ngày)

---

## 📱 Ví dụ thực tế

### Kịch bản 1: Cuộc họp chiều nay

```
Bạn: /add Họp team lúc 3 giờ chiều
Bot: ✅ Đã thêm công việc: 'Họp team lúc 3 giờ chiều'
     💡 Đặt nhắc nhở với: /remind 1 [thời gian]

Bạn: /remind 1 14:45
Bot: ⏰ Đã đặt nhắc nhở!
     📌 Công việc: Họp team lúc 3 giờ chiều
     🕐 Thời gian: 22/07/2026 14:45
```

Vào **14:45**, bot sẽ tự động gửi:
```
⏰ NHẮC NHỞ!

📌 Họp team lúc 3 giờ chiều
```

---

### Kịch bản 2: Uống thuốc sau 30 phút

```
Bạn: /add Uống thuốc
Bot: ✅ Đã thêm công việc: 'Uống thuốc'

Bạn: /remind 1 30m
Bot: ⏰ Đã đặt nhắc nhở!
     📌 Công việc: Uống thuốc
     🕐 Thời gian: 22/07/2026 16:23
```

Sau **30 phút**, bot gửi nhắc nhở!

---

### Kịch bản 3: Deadline ngày mai

```
Bạn: /add Nộp báo cáo cuối tháng
Bot: ✅ Đã thêm công việc: 'Nộp báo cáo cuối tháng'

Bạn: /remind 1 2026-07-23 08:00
Bot: ⏰ Đã đặt nhắc nhở!
     📌 Công việc: Nộp báo cáo cuối tháng
     🕐 Thời gian: 23/07/2026 08:00
```

Vào **8:00 sáng ngày 23/7**, bot sẽ nhắc!

---

### Kịch bản 4: Nhiều công việc với nhiều reminder

```
Bạn: /add Mua sữa
Bot: ✅ Đã thêm công việc: 'Mua sữa'

Bạn: /add Gọi điện cho mẹ
Bot: ✅ Đã thêm công việc: 'Gọi điện cho mẹ'

Bạn: /add Làm bài tập
Bot: ✅ Đã thêm công việc: 'Làm bài tập'

Bạn: /remind 1 18:00
Bot: ⏰ Đã đặt nhắc nhở! ...

Bạn: /remind 2 19:30
Bot: ⏰ Đã đặt nhắc nhở! ...

Bạn: /remind 3 2h
Bot: ⏰ Đã đặt nhắc nhở! ...
```

---

## 📝 Xem danh sách với thời gian nhắc nhở

```
Bạn: /list
Bot: 📋 Danh sách công việc:

     1. ⏳ Mua sữa
        ⏰ Nhắc lúc: 22/07/2026 18:00
     
     2. ⏳ Gọi điện cho mẹ
        ⏰ Nhắc lúc: 22/07/2026 19:30
     
     3. ⏳ Làm bài tập
        ⏰ Nhắc lúc: 22/07/2026 17:53
```

Sau khi bot đã gửi nhắc nhở:
```
     1. ✅ Mua sữa
        🔔 Đã nhắc: 22/07/2026 18:00
```

---

## ✅ Hoàn thành công việc

```
Bạn: /done 1
Bot: ✅ Đã đánh dấu hoàn thành: 'Mua sữa'
```

Khi bot gửi reminder cho task đã hoàn thành:
```
⏰ NHẮC NHỞ!

📌 Mua sữa

✅ (Đã hoàn thành)
```

---

## ⚙️ Tính năng nâng cao

### Background Checker
- Bot kiểm tra thời gian **mỗi 30 giây**
- Gửi nhắc nhở khi đến giờ (trong vòng 1 phút)
- Mỗi reminder chỉ gửi **1 lần**

### Reminder Tracking
- Bot nhớ reminder nào đã gửi (không gửi lại)
- Hiển thị trạng thái trong `/list`:
  - ⏰ Nhắc lúc: (chưa gửi)
  - 🔔 Đã nhắc: (đã gửi)

### Multiple Users
- Mỗi user có danh sách task riêng
- Reminder được gửi đúng người
- Không bị trùng lặp

---

## ⚠️ Lưu ý quan trọng

### 1. Thời gian phải trong tương lai
```
Bạn: /remind 1 08:00
     (Nếu bây giờ đã 10:00)

Bot: ⏰ Đã đặt nhắc nhở!
     📌 Công việc: ...
     🕐 Thời gian: 23/07/2026 08:00
     (Tự động chuyển sang ngày mai)
```

### 2. Data lưu trong memory
- **Khuyết điểm**: Khi restart bot → mất hết data
- **Giải pháp tương lai**: Thêm database (MongoDB/PostgreSQL)

### 3. Múi giờ
- Bot sử dụng **giờ server** (UTC)
- Nếu server ở múi giờ khác → cần điều chỉnh

---

## 🐛 Xử lý lỗi

### Lỗi: "Thời gian nhắc nhở phải là thời điểm trong tương lai!"

```
Bạn: /remind 1 08:00
     (Bây giờ đã 18:00 cùng ngày)

Bot: ⏰ Đã đặt nhắc nhở!
     🕐 Thời gian: 23/07/2026 08:00
     (Tự động sang ngày mai)
```

### Lỗi: "Định dạng thời gian không hợp lệ!"

**Nguyên nhân**: Sai format

**Giải pháp**: Dùng đúng format:
- `14:30` ✅
- `2026-07-23 09:00` ✅
- `30m` ✅
- `2h` ✅
- `14h30` ❌ (sai - phải là `14:30`)
- `23/07/2026 09:00` ❌ (sai - phải dùng `-`)

---

## 📊 So sánh các định dạng

| Định dạng | Ví dụ | Mô tả | Use Case |
|-----------|-------|-------|----------|
| `HH:MM` | `14:30` | Giờ phút hôm nay/ngày mai | Cuộc họp trong ngày |
| `YYYY-MM-DD HH:MM` | `2026-07-25 10:00` | Ngày giờ cụ thể | Deadline xa |
| `Xm` | `30m`, `90m` | Sau X phút | Nấu ăn, uống thuốc |
| `Xh` | `2h`, `24h` | Sau X giờ | Break, nghỉ ngơi |

---

## 🎯 Tips & Tricks

### 1. Reminder nhanh cho việc gấp
```
/add Tắt bếp
/remind 1 10m
```

### 2. Planning cho cả tuần
```
/add Họp sprint planning
/remind 1 2026-07-24 09:00

/add Review code
/remind 2 2026-07-24 14:00

/add 1-on-1 với manager
/remind 3 2026-07-25 10:30
```

### 3. Kết hợp với /done
```
/list          # Xem công việc
/done 1        # Hoàn thành task 1
/list          # Xem lại (task 1 có ✅)
```

### 4. Xóa task không cần nữa
```
/delete 2      # Xóa task số 2 (và reminder của nó)
```

---

## 🔮 Tính năng sắp tới

- [ ] Lặp lại reminder (daily, weekly)
- [ ] Snooze reminder (hoãn 10 phút, 1 giờ)
- [ ] Lưu data vào database
- [ ] Múi giờ tùy chỉnh
- [ ] Reminder trước X phút
- [ ] Nhắc lại nếu chưa done
- [ ] Export/import task list
- [ ] Thống kê reminder

---

## 📞 Hỗ trợ

Gặp vấn đề? Tạo [issue trên GitHub](https://github.com/rambo247/task_bot/issues)!

---

**Happy Task Managing! 🎉**
