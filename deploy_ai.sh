#!/bin/bash

# Script deploy bot với AI lên CentOS server

echo "🚀 Deploying bot with AI to server..."

# Pull latest code
cd task_bot
git pull origin main

# Setup environment variables
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-8802370170:AAEGZU_Df5OnDQTO7kn9lyf2UzeIbbh2KPk}
GITHUB_TOKEN=${GITHUB_TOKEN:-}
EOF
    echo "⚠️  .env created. Please edit and add your GITHUB_TOKEN!"
    echo "   nano .env"
else
    echo "✅ .env already exists"
fi

# Kill old bot
echo "🛑 Stopping old bot..."
pkill -f task_bot.py

# Start new bot
echo "▶️  Starting bot..."
nohup python3 task_bot.py > bot.log 2>&1 &

# Wait and check
sleep 2

# Check if bot is running
if pgrep -f task_bot.py > /dev/null; then
    echo "✅ Bot started successfully!"
    echo "📋 Process IDs:"
    pgrep -f task_bot.py
    echo ""
    echo "📄 Recent logs:"
    tail -15 bot.log
else
    echo "❌ Failed to start bot!"
    echo "📄 Error logs:"
    tail -20 bot.log
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "💡 To enable AI features:"
echo "   1. Get GitHub token from: https://github.com/settings/tokens"
echo "   2. Edit .env: nano .env"
echo "   3. Add: GITHUB_TOKEN=your_token_here"
echo "   4. Restart: pkill -f task_bot.py && nohup python3 task_bot.py > bot.log 2>&1 &"
