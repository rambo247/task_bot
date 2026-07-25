#!/bin/bash
# Script update và restart bot trên server
# Chạy: bash update_bot.sh

echo "🔄 UPDATING TELEGRAM TASK BOT"
echo "================================"

# 1. Stop bot cũ
echo "🛑 Stopping old bot..."
pkill -f task_bot.py
sleep 2

# 2. Pull code mới từ GitHub
echo "📥 Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main
git pull

# 3. Install/Update dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --user

# 4. Verify .env file
echo "🔑 Checking .env file..."
if [ -f ".env" ]; then
    echo "  ✅ .env file exists"
else
    echo "  ⚠️  .env file not found!"
    echo "  Creating .env template..."
    cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
GITHUB_TOKEN=your_github_token_here
EOF
    echo "  ⚠️  Please edit .env file with your tokens!"
    exit 1
fi

# 5. Start bot mới
echo "🎬 Starting bot..."
screen -dmS taskbot python3 task_bot.py
sleep 3

# 6. Verify bot đang chạy
echo "🔍 Verifying bot status..."
if pgrep -f task_bot.py > /dev/null; then
    echo ""
    echo "✅ BOT UPDATED SUCCESSFULLY!"
    echo "================================"
    echo ""
    echo "📊 Bot info:"
    ps aux | grep task_bot.py | grep -v grep
    echo ""
    echo "📋 Next steps:"
    echo "  - View logs: screen -r taskbot"
    echo "  - Detach: Ctrl+A then D"
    echo "  - Stop bot: pkill -f task_bot.py"
    echo ""
else
    echo ""
    echo "❌ BOT FAILED TO START!"
    echo "================================"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  1. Check Python version: python3 --version"
    echo "  2. Check dependencies: pip3 list | grep -E 'pyTelegramBotAPI|requests|python-dotenv'"
    echo "  3. Run bot manually: python3 task_bot.py"
    echo "  4. Check .env file: cat .env"
    echo ""
fi
