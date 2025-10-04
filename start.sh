#!/bin/bash

echo "🤖 Starting AI Agent Chatbot..."
echo "================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and add your OpenAI API key."
    echo "   Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi

# Check if AZURE_OPENAI_API_KEY is set
if ! grep -q "AZURE_OPENAI_API_KEY=8iCdXeS" .env; then
    echo "⚠️  Please add your Azure OpenAI API key to the .env file"
    echo "   AZURE_OPENAI_API_KEY=your_actual_api_key_here"
    exit 1
fi

echo "✅ Environment setup looks good!"
echo ""

echo "🚀 Starting backend server (FastAPI)..."
echo "   Backend will be available at: http://localhost:8000"
echo ""

# Start backend in background
cd backend
python main.py &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

echo "🚀 Starting frontend server (Flask)..."
echo "   Frontend will be available at: http://localhost:3000"
echo ""

# Wait a moment for backend to start
sleep 2

# Start frontend
cd ..
python app.py &
FRONTEND_PID=$!

echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "🎉 AI Agent Chatbot is now running!"
echo ""
echo "📱 Open your browser and go to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait
