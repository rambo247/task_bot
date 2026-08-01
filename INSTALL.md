# 🔧 INSTALLATION GUIDE - Enterprise AI Assistant v2.1.0

## 📋 MỤC LỤC
1. [Requirements](#requirements)
2. [Quick Install](#quick-install-5-phút)
3. [Step-by-Step Install](#step-by-step-install)
4. [Platform-Specific](#platform-specific-guides)
5. [Docker Install](#docker-install)
6. [Troubleshooting](#troubleshooting)
7. [Verify Install](#verify-installation)

---

## ✅ REQUIREMENTS

### Minimum:
```yaml
OS: Windows 10+, Linux, macOS
Python: 3.8+
RAM: 512MB
Disk: 100MB
Network: Internet connection
```

### Recommended:
```yaml
OS: Windows 11, Ubuntu 20.04+, macOS 11+
Python: 3.10+
RAM: 1GB+
Disk: 500MB+
Network: Stable internet
```

### API Keys Needed:
```
✅ Telegram Bot Token (Required)
   → Get from @BotFather

✅ GitHub Personal Access Token (Optional, for AI)
   → Get from github.com/settings/tokens

✅ OpenAI API Key (Optional, for voice)
   → Get from platform.openai.com
```

---

## ⚡ QUICK INSTALL (5 PHÚT)

### Windows:
```powershell
# 1. Clone or download
git clone https://github.com/username/bot.git
cd bot

# 2. Install Python 3.10+ (if needed)
# Download from python.org

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup .env
copy .env.example .env
# Edit .env with your keys

# 5. Run!
python task_bot.py
```

### Linux/macOS:
```bash
# 1. Clone
git clone https://github.com/username/bot.git
cd bot

# 2. Install Python 3.10+ (if needed)
# Linux: sudo apt install python3.10
# macOS: brew install python@3.10

# 3. Virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup .env
cp .env.example .env
nano .env  # Edit with your keys

# 6. Run!
python task_bot.py
```

**✅ Done! Bot should be running now.**

---

## 📖 STEP-BY-STEP INSTALL

### Step 1: Python Installation

#### Windows:
```powershell
# Download Python 3.10+ from python.org
# During install: CHECK ✅ "Add Python to PATH"

# Verify:
python --version
# Should show: Python 3.10.x or higher
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# Verify
python3 --version
```

#### macOS:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Verify
python3 --version
```

---

### Step 2: Get Bot Code

#### Option A: Git Clone (Recommended)
```bash
git clone https://github.com/username/enterprise-ai-bot.git
cd enterprise-ai-bot
```

#### Option B: Download ZIP
```
1. Go to: https://github.com/username/bot
2. Click: Code → Download ZIP
3. Extract to: f:\workspace12\ (Windows) or ~/workspace12/ (Linux/Mac)
4. cd workspace12
```

---

### Step 3: Create Virtual Environment (Recommended)

#### Windows:
```powershell
# Create venv
python -m venv venv

# Activate
.\venv\Scripts\activate

# You should see (venv) in prompt
```

#### Linux/macOS:
```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# You should see (venv) in prompt
```

**Why virtual environment?**
- Isolated dependencies
- No conflicts with other projects
- Easy to delete/recreate

---

### Step 4: Install Dependencies

```bash
# Make sure venv is activated (you should see (venv))

# Install all deps
pip install -r requirements.txt

# This will install:
#   - pyTelegramBotAPI (Telegram bot)
#   - requests (HTTP client)
#   - python-dotenv (Environment vars)
#   - beautifulsoup4 (Web scraping)
#   - lxml (HTML parsing)
#   - validators (URL validation)
```

**Expected output:**
```
Collecting pyTelegramBotAPI...
Successfully installed pyTelegramBotAPI-3.8.x
Collecting requests...
Successfully installed requests-2.31.x
...
Successfully installed 6 packages
```

---

### Step 5: Get API Keys

#### 5.1 Telegram Bot Token:
```
1. Open Telegram
2. Search: @BotFather
3. Send: /newbot
4. Follow instructions:
   - Bot name: MyCompanyBot
   - Bot username: mycompany_bot
5. Copy token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### 5.2 GitHub Token (For AI, Optional):
```
1. Go to: https://github.com/settings/tokens
2. Click: "Generate new token" → "Classic"
3. Scopes: Select "repo" (if private) or nothing (if public)
4. Click: Generate
5. Copy token: ghp_xxxxxxxxxxxxxxxxxxxx
```

#### 5.3 OpenAI Key (For Voice, Optional):
```
1. Go to: https://platform.openai.com
2. Sign up/login
3. Go to: API Keys
4. Create new secret key
5. Copy: sk-xxxxxxxxxxxxxxxxxxxx
```

---

### Step 6: Configure .env

#### Create .env file:

**Windows:**
```powershell
# Copy example
copy .env.example .env

# Edit with Notepad
notepad .env
```

**Linux/macOS:**
```bash
# Copy example
cp .env.example .env

# Edit
nano .env
# or
vi .env
# or
code .env  # VS Code
```

#### .env Content:
```env
# Telegram Bot Token (REQUIRED)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# GitHub Token (OPTIONAL - for AI)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# OpenAI Key (OPTIONAL - for voice to text)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Bot Settings (OPTIONAL)
BOT_NAME=MyCompanyBot
BOT_LANGUAGE=vi
```

**Replace with your actual keys!**

---

### Step 7: Run Bot!

```bash
python task_bot.py
```

**Expected output:**
```
🤖 Bot đang khởi động...
Enterprise features: ✅ Enabled
AI features: ✅ Enabled (GitHub Token found)
Voice features: ✅ Enabled (OpenAI Key found)
✅ Bot started successfully!
Listening for messages...
```

**If you see errors:**
- Check .env file (keys correct?)
- Check internet connection
- See [Troubleshooting](#troubleshooting) below

---

### Step 8: Test Bot

```
1. Open Telegram
2. Find your bot (search @mycompany_bot)
3. Send: /start

Expected response:
  ✅ Welcome message
  ✅ Main menu with buttons
  ✅ 🏢 Doanh Nghiệp button visible

4. Test features:
   - Click: 🏢 Doanh Nghiệp
   - Create organization
   - Test import
   - Test AI

If all works: ✅ Installation complete!
```

---

## 🖥️ PLATFORM-SPECIFIC GUIDES

### Windows 10/11

#### Using Command Prompt:
```cmd
cd f:\workspace12
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
notepad .env
python task_bot.py
```

#### Using PowerShell:
```powershell
cd f:\workspace12
python -m venv venv
.\venv\Scripts\Activate.ps1

# If error "cannot be loaded because running scripts is disabled"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

pip install -r requirements.txt
copy .env.example .env
notepad .env
python task_bot.py
```

#### Using Git Bash (if installed):
```bash
cd /f/workspace12
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python task_bot.py
```

---

### Ubuntu/Debian Linux

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & tools
sudo apt install python3.10 python3.10-venv python3-pip git -y

# Clone
cd ~
git clone https://github.com/username/bot.git
cd bot

# Setup venv
python3 -m venv venv
source venv/bin/activate

# Install deps
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Edit keys

# Run
python task_bot.py

# Run in background
nohup python task_bot.py > bot.log 2>&1 &

# Check if running
ps aux | grep task_bot

# View logs
tail -f bot.log
```

---

### CentOS/RHEL/Fedora

```bash
# Install Python
sudo dnf install python3.10 python3-pip git -y

# Rest is same as Ubuntu
cd ~
git clone https://github.com/username/bot.git
cd bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
vi .env
python task_bot.py
```

---

### macOS

```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10 git

# Clone
cd ~
git clone https://github.com/username/bot.git
cd bot

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env

# Run
python task_bot.py

# Run in background (using brew services)
# Create a plist file in ~/Library/LaunchAgents/
# Or use screen/tmux
```

---

## 🐳 DOCKER INSTALL

### Create Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY task_bot.py .
COPY .env .

# Run bot
CMD ["python", "task_bot.py"]
```

### Build & Run:

```bash
# Build image
docker build -t enterprise-ai-bot:v2.1.0 .

# Run container
docker run -d \
  --name ai-bot \
  --restart unless-stopped \
  --env-file .env \
  enterprise-ai-bot:v2.1.0

# View logs
docker logs -f ai-bot

# Stop
docker stop ai-bot

# Restart
docker restart ai-bot
```

### Docker Compose:

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: enterprise-ai-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data  # For future DB persistence
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Usage:**
```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## 🐛 TROUBLESHOOTING

### Error: "No module named 'telebot'"

```bash
# Solution:
pip install pyTelegramBotAPI

# Or reinstall all:
pip install -r requirements.txt
```

---

### Error: "Import telebot could not be resolved"

```bash
# Check Python in terminal vs VS Code
# Make sure VS Code uses correct Python interpreter

# In VS Code:
# 1. Ctrl+Shift+P
# 2. "Python: Select Interpreter"
# 3. Choose venv Python (should show ./venv/...)
```

---

### Error: "Enterprise features not enabled"

```bash
# Install optional dependencies
pip install beautifulsoup4 lxml validators

# Verify
pip list | grep beautifulsoup4
```

---

### Error: "Telegram token invalid"

```
1. Check .env file
2. Token format: 1234567890:ABCdefGHI...
3. No spaces before/after =
4. No quotes around token

Correct:
  TELEGRAM_BOT_TOKEN=1234567890:ABC...

Wrong:
  TELEGRAM_BOT_TOKEN = "1234567890:ABC..."
  TELEGRAM_BOT_TOKEN= 1234567890:ABC ...
```

---

### Error: "Connection error / Can't connect to Telegram"

```
1. Check internet connection
2. Check firewall (allow Python)
3. Check if Telegram is blocked in your country
   → Use VPN/proxy if needed

Proxy setup (in task_bot.py):
  bot = telebot.TeleBot(
      TOKEN,
      proxy='http://proxy_host:proxy_port'
  )
```

---

### Bot starts but doesn't respond:

```
1. Check bot username is correct
2. Check you're messaging the right bot
3. Check /start command works
4. Check bot logs for errors
5. Try: /setcommands in @BotFather
```

---

### Error: "ModuleNotFoundError: No module named 'dotenv'"

```bash
pip install python-dotenv
```

---

### Permission denied (Linux/macOS):

```bash
# If "python: command not found"
# Use python3 instead:
python3 task_bot.py

# If permission denied on venv activate:
chmod +x venv/bin/activate

# If permission denied on task_bot.py:
chmod +x task_bot.py
```

---

### High memory usage:

```
Causes:
- Large knowledge base (1000+ Q&A)
- Many contacts (1000+)
- Multiple web scrapings

Solutions:
1. Upgrade to v2.2 with database (coming soon)
2. Use SQLite instead of in-memory
3. Add more RAM
4. Limit data per org
```

---

### Bot crashes/restarts:

```bash
# Check logs
python task_bot.py 2>&1 | tee bot.log

# Use screen (Linux/macOS):
screen -S bot
python task_bot.py
# Ctrl+A, D to detach
# screen -r bot to reattach

# Use systemd (Linux):
# Create /etc/systemd/system/ai-bot.service
# See Production Deployment below
```

---

## ✅ VERIFY INSTALLATION

### Checklist:

```bash
# 1. Python version
python --version
# Expected: Python 3.8+ (3.10+ recommended)

# 2. Pip version
pip --version
# Expected: pip 20.0+ from venv

# 3. Dependencies installed
pip list
# Expected: pyTelegramBotAPI, requests, python-dotenv, beautifulsoup4, lxml, validators

# 4. .env file exists
cat .env  # Linux/Mac
type .env  # Windows
# Expected: Keys configured

# 5. Bot starts
python task_bot.py
# Expected: "Bot started successfully!"

# 6. Telegram response
# Send /start to bot
# Expected: Welcome message + menu

# 7. Enterprise features
# Menu → 🏢 Doanh Nghiệp
# Expected: Organization menu visible

# 8. Import test
# Import sample data from test_enterprise.py
# Expected: Success message

# 9. AI test (if GitHub token set)
# Enable AI → Ask question
# Expected: AI response

# 10. All green? ✅ Installation verified!
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Systemd Service (Linux):

**Create `/etc/systemd/system/ai-bot.service`:**
```ini
[Unit]
Description=Enterprise AI Assistant Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/bot
Environment="PATH=/home/botuser/bot/venv/bin"
ExecStart=/home/botuser/bot/venv/bin/python task_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable & start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-bot
sudo systemctl start ai-bot

# Check status
sudo systemctl status ai-bot

# View logs
sudo journalctl -u ai-bot -f
```

---

### Supervisor (Alternative):

**Install supervisor:**
```bash
sudo apt install supervisor
```

**Create `/etc/supervisor/conf.d/ai-bot.conf`:**
```ini
[program:ai-bot]
command=/home/botuser/bot/venv/bin/python task_bot.py
directory=/home/botuser/bot
user=botuser
autostart=true
autorestart=true
stderr_logfile=/var/log/ai-bot.err.log
stdout_logfile=/var/log/ai-bot.out.log
```

**Start:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-bot

# Status
sudo supervisorctl status ai-bot
```

---

### Cloud Deployment (Render.com):

**1. Prepare code:**
```bash
# Add Procfile (already exists)
web: python task_bot.py

# Add runtime.txt
python-3.10.8

# Push to GitHub
git add .
git commit -m "Prepare for Render"
git push
```

**2. Deploy on Render:**
```
1. Go to: render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Name: enterprise-ai-bot
   - Environment: Python
   - Build: pip install -r requirements.txt
   - Start: python task_bot.py
5. Add environment variables:
   - TELEGRAM_BOT_TOKEN
   - GITHUB_TOKEN
   - OPENAI_API_KEY
6. Deploy!
```

---

### Heroku Deployment:

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create my-ai-bot

# Set env vars
heroku config:set TELEGRAM_BOT_TOKEN=xxx
heroku config:set GITHUB_TOKEN=xxx
heroku config:set OPENAI_API_KEY=xxx

# Deploy
git push heroku main

# Logs
heroku logs --tail
```

---

## 📚 NEXT STEPS

After successful installation:

1. ✅ Read **README_ENTERPRISE.md** - Overview
2. ✅ Read **QUICK_REFERENCE.md** - Quick ref
3. ✅ Read **ENTERPRISE_GUIDE.md** - Detailed guide
4. ✅ Run **test_enterprise.py** - Demo & examples
5. ✅ Import your data
6. ✅ Test all features
7. ✅ Deploy to production
8. ✅ Train your team
9. ✅ Go live! 🚀

---

## 💡 TIPS

### Tip 1: Use Virtual Environment
```
Always use venv for Python projects
Prevents dependency conflicts
Easy to reset if something breaks
```

### Tip 2: Keep .env Secure
```
Never commit .env to Git
Add .env to .gitignore
Use different tokens for dev/prod
```

### Tip 3: Monitor Resources
```bash
# Check memory
free -h  # Linux
Get-Process python  # Windows

# Check CPU
top  # Linux
```

### Tip 4: Regular Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for security updates
pip list --outdated
```

### Tip 5: Backup Data
```
Future v2.2+ will have database
For now: Document your Q&A/contacts
Easy to re-import if needed
```

---

## 🆘 SUPPORT

### Can't install?
1. Read troubleshooting above
2. Check requirements.txt
3. Try manual install: `pip install package_name`

### Still stuck?
- GitHub Issues
- Telegram support group
- Email: support@example.com

### Want commercial support?
- Enterprise license
- Priority support
- Custom development
- Training sessions

---

**✅ INSTALLATION COMPLETE!**

**Now run:**
```bash
python task_bot.py
```

**And enjoy your Enterprise AI Assistant! 🎉**

---

**Version:** 2.1.0  
**Last Updated:** 01/08/2026  
**Tested On:** Windows 11, Ubuntu 22.04, macOS 13
