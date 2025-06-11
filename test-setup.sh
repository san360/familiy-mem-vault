#!/bin/bash

# Family Memory Vault - Local Development Test Script

echo "🧪 Testing Family Memory Vault Setup..."
echo

# Test backend dependencies
echo "📦 Checking backend dependencies..."
cd backend
if python -c "import fastapi, uvicorn, pydantic" 2>/dev/null; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Backend dependencies missing"
    exit 1
fi

# Test backend API
echo "🔧 Testing backend API..."
python -m pytest tests/ -q
if [ $? -eq 0 ]; then
    echo "✅ Backend tests pass"
else
    echo "❌ Backend tests fail"
    exit 1
fi

cd ..

# Test frontend dependencies
echo "📦 Checking frontend dependencies..."
cd frontend
if npm list react 2>/dev/null | grep -q "react@"; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Frontend dependencies missing"
    exit 1
fi

# Test frontend build
echo "🔧 Testing frontend build..."
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Frontend builds successfully"
else
    echo "❌ Frontend build fails"
    exit 1
fi

cd ..

echo
echo "🎉 All tests passed! Your Family Memory Vault is ready for development."
echo
echo "📝 Next steps:"
echo "  1. Start backend: cd backend && python main.py"
echo "  2. Start frontend: cd frontend && npm run dev"
echo "  3. Visit: http://localhost:5173"
echo
echo "🚀 For deployment:"
echo "  azd up"