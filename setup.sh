#!/bin/bash

# Contract Analysis Agent - Setup Script for Mac/Linux

set -e  # Exit on error

echo "🚀 Contract Analysis Agent - Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}📍 Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo -e "${BLUE}📍 Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

# Setup Backend
echo ""
echo -e "${BLUE}📍 Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Setup Frontend
echo ""
echo -e "${BLUE}📍 Setting up Frontend...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install -q
else
    echo "node_modules already exists, skipping npm install"
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"

# Success message
echo ""
echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1️⃣  Start Backend (in Terminal 1):"
echo -e "   ${YELLOW}cd /Users/ayandogra/Downloads/Manulife/backend${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}python -m uvicorn app.main:app --reload --port 8000${NC}"
echo ""
echo "2️⃣  Start Frontend (in Terminal 2):"
echo -e "   ${YELLOW}cd /Users/ayandogra/Downloads/Manulife/frontend${NC}"
echo -e "   ${YELLOW}npm run dev${NC}"
echo ""
echo "3️⃣  Open browser:"
echo -e "   ${YELLOW}http://localhost:5173${NC}"
echo ""
echo -e "${GREEN}Happy analyzing! 🎉${NC}"
