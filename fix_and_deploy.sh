#!/bin/bash
# Script fix và deploy bot lên server
# Chạy: bash fix_and_deploy.sh

echo "🔧 Đang sửa và deploy bot..."

# 1. Kill TẤT CẢ process python3
echo "🛑 Killing all bot processes..."
killall -9 python3 2>/dev/null
pkill -9 -f task_bot.py 2>/dev/null

# 2. Đợi 3 giây
sleep 3

# 3. Kiểm tra còn process nào không
if pgrep -f task_bot.py > /dev/null; then
    echo "❌ Vẫn còn zombie process! Trying harder..."
    ps aux | grep task_bot.py | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null
    sleep 2
fi

# 4. Pull code mới
echo "📥 Pulling latest code..."
cd /root/task_bot || cd ~/task_bot || cd task_bot
git pull origin main

# 5. Chạy bot MỘT LẦN duy nhất
echo "▶️  Starting bot..."
nohup python3 task_bot.py > bot.log 2>&1 &

# 6. Đợi 5 giây
sleep 5

# 7. Kiểm tra kết quả
echo ""
echo "========================================="
echo "📊 KẾT QUẢ DEPLOYMENT:"
echo "========================================="

PROCESS_COUNT=$(pgrep -f task_bot.py | wc -l)

if [ "$PROCESS_COUNT" -eq 1 ]; then
    echo "✅ THÀNH CÔNG! Bot đang chạy"
    echo "🆔 Process ID:"
    pgrep -f task_bot.py
    echo ""
    echo "📄 Log (20 dòng cuối):"
    tail -20 bot.log
elif [ "$PROCESS_COUNT" -gt 1 ]; then
    echo "⚠️  CẢNH BÁO: Có $PROCESS_COUNT processes đang chạy!"
    echo "🆔 PIDs:"
    pgrep -f task_bot.py
    echo ""
    echo "Cần kill lại:"
    echo "pkill -9 -f task_bot.py"
elif [ "$PROCESS_COUNT" -eq 0 ]; then
    echo "❌ LỖI: Bot không khởi động được"
    echo "📄 Log lỗi:"
    tail -30 bot.log
else
    echo "🤔 Trạng thái không xác định"
fi

echo "========================================="
