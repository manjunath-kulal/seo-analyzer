#!/bin/bash

echo "🚀 Starting Writesonic SEO Analyzer..."
echo ""

# Start backend
echo "📦 Starting backend server..."
cd backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
uvicorn main:app --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"

echo ""
echo "🎉 All servers started successfully!"
echo ""
echo "📝 To stop servers, run: ./stop-all.sh"
echo "📊 Backend logs: tail -f backend.log"
echo "📊 Frontend logs: tail -f frontend.log"
echo ""
echo "🌐 Open http://localhost:3000 in your browser"
