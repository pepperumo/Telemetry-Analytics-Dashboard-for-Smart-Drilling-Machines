# Dockerfile to simulate fresh environment for Windows, macOS, and Linux
FROM ubuntu:22.04

# Start with clean environment (no Python/Node)
WORKDIR /app

# Install basic tools but NOT Python/Node initially
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy your project
COPY . .

# Create comprehensive cross-platform installation simulation script
RUN echo '#!/bin/bash\n\
echo "=== Cross-Platform Fresh Machine Installation Demo ==="\n\
echo "This simulates what happens on Windows, macOS, and Linux without Python/Node"\n\
echo ""\n\
\n\
echo "=== STEP 1: Testing Fresh Machine (ALL PLATFORMS) ==="\n\
echo ""\n\
echo "🖥️  What you would see on Windows PowerShell:"\n\
echo "PS> python --version"\n\
echo "❌ ERROR: '\''python'\'' is not recognized as an internal or external command"\n\
echo "PS> node --version"\n\
echo "❌ ERROR: '\''node'\'' is not recognized as an internal or external command"\n\
echo "PS> npm --version"\n\
echo "❌ ERROR: '\''npm'\'' is not recognized as an internal or external command"\n\
echo ""\n\
echo "🍎 What you would see on macOS Terminal:"\n\
echo "$ python3 --version"\n\
echo "❌ ERROR: command not found: python3"\n\
echo "$ node --version"\n\
echo "❌ ERROR: command not found: node"\n\
echo "$ npm --version"\n\
echo "❌ ERROR: command not found: npm"\n\
echo ""\n\
echo "🐧 What you see on this Linux container (simulating fresh install):"\n\
python3 --version 2>/dev/null || echo "❌ ERROR: python3 command not found"\n\
python --version 2>/dev/null || echo "❌ ERROR: python command not found"\n\
node --version 2>/dev/null || echo "❌ ERROR: node command not found"\n\
npm --version 2>/dev/null || echo "❌ ERROR: npm command not found"\n\
echo ""\n\
echo "📁 Testing project setup (SHOULD FAIL ON ALL PLATFORMS):"\n\
echo "$ cd backend && python -m venv venv"\n\
cd /app/backend && python3 -m venv venv 2>/dev/null || echo "❌ FAILED: Cannot create venv - Python not installed"\n\
echo "$ cd frontend && npm install"\n\
cd /app/frontend && npm install 2>/dev/null || echo "❌ FAILED: Cannot run npm - Node.js not installed"\n\
echo ""\n\
\n\
echo "=== STEP 2: Installation Guide by Platform ==="\n\
echo ""\n\
echo "🖥️  WINDOWS Installation:"\n\
echo "1. Download Python 3.11+ from https://python.org/downloads/"\n\
echo "   ✅ Check '\''Add Python to PATH'\'' during installation"\n\
echo "2. Download Node.js 18+ LTS from https://nodejs.org/"\n\
echo "3. Restart PowerShell/Command Prompt"\n\
echo "4. Verify: python --version && node --version"\n\
echo ""\n\
echo "🍎 macOS Installation:"\n\
echo "Option A - Using Homebrew (recommended):"\n\
echo "1. Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""\n\
echo "2. brew install python@3.11 node"\n\
echo "Option B - Direct downloads:"\n\
echo "1. Download Python 3.11+ from https://python.org/downloads/macos/"\n\
echo "2. Download Node.js 18+ from https://nodejs.org/"\n\
echo "3. Verify: python3 --version && node --version"\n\
echo ""\n\
echo "🐧 Linux (Ubuntu/Debian) Installation:"\n\
echo "1. sudo apt update"\n\
echo "2. sudo apt install python3 python3-pip python3-venv"\n\
echo "3. curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"\n\
echo "4. sudo apt install nodejs"\n\
echo ""\n\
\n\
echo "=== STEP 3: Simulating Installation Process ==="\n\
echo ""\n\
echo "📦 Installing Python 3.11+ (simulated for this demo)..."\n\
apt-get update > /dev/null 2>&1\n\
apt-get install -y python3 python3-pip python3-venv > /dev/null 2>&1\n\
echo "✅ Python installation completed"\n\
echo ""\n\
echo "📦 Installing Node.js 18+ (simulated for this demo)..."\n\
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1\n\
apt-get install -y nodejs > /dev/null 2>&1\n\
echo "✅ Node.js installation completed"\n\
echo ""\n\
\n\
echo "=== STEP 4: Testing After Installation ==="\n\
echo ""\n\
echo "🔍 Testing Python:"\n\
python3 --version && echo "✅ Python3 is now available"\n\
pip3 --version && echo "✅ pip3 is now available"\n\
echo ""\n\
echo "🔍 Testing Node.js:"\n\
node --version && echo "✅ Node.js is now available"\n\
npm --version && echo "✅ npm is now available"\n\
echo ""\n\
echo "🔍 Testing project setup (SHOULD NOW WORK):"\n\
echo "Backend setup:"\n\
cd /app/backend\n\
python3 -m venv venv && echo "✅ SUCCESS: Virtual environment created!"\n\
source venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1 && echo "✅ SUCCESS: Python dependencies installed!"\n\
echo ""\n\
echo "Frontend setup:"\n\
cd /app/frontend\n\
npm install > /dev/null 2>&1 && echo "✅ SUCCESS: Frontend dependencies installed!"\n\
echo ""\n\
\n\
echo "=== STEP 5: Platform-Specific Project Startup Commands ==="\n\
echo ""\n\
echo "🖥️  Windows (PowerShell/Command Prompt):"\n\
echo "Backend:  cd backend && venv\\Scripts\\activate && python main.py"\n\
echo "Frontend: cd frontend && npm run dev"\n\
echo ""\n\
echo "🍎 macOS (Terminal):"\n\
echo "Backend:  cd backend && source venv/bin/activate && python3 main.py"\n\
echo "Frontend: cd frontend && npm run dev"\n\
echo ""\n\
echo "🐧 Linux (Terminal):"\n\
echo "Backend:  cd backend && source venv/bin/activate && python3 main.py"\n\
echo "Frontend: cd frontend && npm run dev"\n\
echo ""\n\
\n\
echo "=== ✅ FINAL SUMMARY ==="\n\
echo ""\n\
echo "Before Installation (ALL PLATFORMS):"\n\
echo "❌ No Python → Cannot create virtual environments"\n\
echo "❌ No Node.js → Cannot install frontend dependencies"\n\
echo "❌ Project cannot run"\n\
echo ""\n\
echo "After Installation (ALL PLATFORMS):"\n\
echo "✅ Python $(python3 --version 2>/dev/null | cut -d\" \" -f2) → Virtual environments work"\n\
echo "✅ Node.js $(node --version) → npm packages install successfully"\n\
echo "✅ Project ready to run on Windows, macOS, and Linux!"\n\
echo ""\n\
echo "📖 Key Takeaway: Virtual environments require system Python installation first"\n\
echo "📖 Cross-platform compatibility: Use python3 on macOS/Linux, python on Windows"\n\
' > /app/cross-platform-demo.sh && chmod +x /app/cross-platform-demo.sh

# Set the default command
CMD ["/app/cross-platform-demo.sh"]