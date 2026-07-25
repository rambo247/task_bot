#!/bin/bash
# Script deploy bot lên server
# Chạy: bash server_deploy.sh

echo "🚀 DEPLOY TELEGRAM TASK BOT"
echo "================================"

# 1. Clone hoặc pull code
echo "📥 Step 1: Getting latest code..."
if [ -d "task_bot" ]; then
    echo "  → Updating existing repository..."
    cd task_bot
    git pull
else
    echo "  → Cloning repository..."
    git clone https://github.com/rambo247/task_bot.git
    cd task_bot
fi

# 2. Check Python
echo ""
echo "🐍 Step 2: Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "  ✅ Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "  ✅ Python found: $(python --version)"
else
    echo "  ❌ Python not found! Installing..."
    sudo yum install python3 -y || sudo apt-get install python3 -y
    PYTHON_CMD=python3
fi

# 3. Check pip
echo ""
echo "📦 Step 3: Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "  → Installing pip..."
    sudo yum install python3-pip -y || sudo apt-get install python3-pip -y
fi

# 4. Install dependencies
echo ""
echo "📚 Step 4: Installing dependencies..."
pip3 install -r requirements.txt --user

# 5. Check .env file
echo ""
echo "🔑 Step 5: Checking .env file..."
if [ ! -f ".env" ]; then
    echo "  ⚠️  .env file not found!"
    echo ""
    echo "  Please create .env file with:"
    echo "  ----------------------------------------"
    echo "  TELEGRAM_BOT_TOKEN=your_token_here"
    echo "  ----------------------------------------"
    echo ""
    read -p "  Enter your Telegram Bot Token: " TOKEN
    echo "TELEGRAM_BOT_TOKEN=$TOKEN" > .env
    echo "  ✅ .env file created!"
else
    echo "  ✅ .env file exists"
fi

# 6. Stop old bot if running
echo ""
echo "🛑 Step 6: Stopping old bot..."
pkill -f task_bot.py 2>/dev/null && echo "  ✅ Old bot stopped" || echo "  → No bot running"

# 7. Start bot
echo ""
echo "🎬 Step 7: Starting bot..."
echo "================================"

# Option A: Run in screen (recommended)
if command -v screen &> /dev/null; then
    echo "  Starting bot in screen session 'taskbot'..."
    screen -dmS taskbot $PYTHON_CMD task_bot.py
    echo ""
    echo "  ✅ Bot started in screen!"
    echo "  To view: screen -r taskbot"
    echo "  To detach: Ctrl+A then D"
    echo "  To stop: screen -X -S taskbot quit"
    
# Option B: Run in background
else
    echo "  Starting bot in background..."
    nohup $PYTHON_CMD task_bot.py > bot.log 2>&1 &
    BOT_PID=$!
    echo ""
    echo "  ✅ Bot started! PID: $BOT_PID"
    echo "  View logs: tail -f bot.log"
    echo "  Stop bot: kill $BOT_PID"
fi

# 8. Verify bot is running
echo ""
echo "🔍 Step 8: Verifying bot..."
sleep 3
if pgrep -f task_bot.py > /dev/null; then
    echo "  ✅ Bot is running!"
    echo ""
    echo "🎉 DEPLOY THÀNH CÔNG!"
    echo "================================"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Test bot in Telegram: /start"
    echo "  2. Monitor logs: tail -f bot.log (or screen -r taskbot)"
    echo "  3. Test privacy: Add 2 users to group, verify private tasks"
    echo ""
else
    echo "  ❌ Bot không chạy!"
    echo "  Check logs: tail bot.log"
fi
