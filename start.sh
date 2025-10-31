#!/bin/bash

# Startup script for Multi-Factor Authentication System

echo "=========================================="
echo "  MFA System Startup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Frontend will not be available."
    FRONTEND_AVAILABLE=false
else
    FRONTEND_AVAILABLE=true
fi

# Create necessary directories
echo "📁 Creating storage directories..."
mkdir -p storage/templates storage/logs

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✓ Python dependencies installed"
    else
        echo "❌ Failed to install Python dependencies"
        exit 1
    fi
fi

# Install Node dependencies if frontend is available
if [ "$FRONTEND_AVAILABLE" = true ]; then
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        echo "📦 Installing Node dependencies..."
        cd frontend
        npm install > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✓ Node dependencies installed"
        else
            echo "⚠️  Failed to install Node dependencies"
        fi
        cd ..
    fi
fi

echo ""
echo "=========================================="
echo "  Starting Services"
echo "=========================================="
echo ""

# Start backend
echo "🚀 Starting Flask backend..."
cd backend
python api/app.py &
BACKEND_PID=$!
cd ..

sleep 3

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo "✓ Backend running on http://localhost:5000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend if available
if [ "$FRONTEND_AVAILABLE" = true ] && [ -d "frontend" ]; then
    echo "🚀 Starting React frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    sleep 3
    
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "✓ Frontend running on http://localhost:3000"
    else
        echo "⚠️  Frontend failed to start"
    fi
else
    echo "⚠️  Frontend not available"
fi

echo ""
echo "=========================================="
echo "  Services Started Successfully!"
echo "=========================================="
echo ""
echo "Backend API: http://localhost:5000"
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "Frontend UI: http://localhost:3000"
fi
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID 2>/dev/null; [ ! -z '$FRONTEND_PID' ] && kill $FRONTEND_PID 2>/dev/null; echo 'Services stopped.'; exit 0" INT

# Keep script running
wait
