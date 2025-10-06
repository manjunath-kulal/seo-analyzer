#!/bin/bash

echo "🛑 Stopping all servers..."

# Kill backend
pkill -f "uvicorn main:app" 2>/dev/null
echo "✅ Backend stopped"

# Kill frontend
pkill -f "next dev" 2>/dev/null
echo "✅ Frontend stopped"

# Clean up log files
rm -f backend.log frontend.log 2>/dev/null

echo "🎉 All servers stopped!"
