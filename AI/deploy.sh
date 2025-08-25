#!/bin/bash

# Mobili AI Chatbot Deployment Script
# ====================================

set -e

echo "🤖 Mobili AI Chatbot Deployment"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template .env
    echo "📝 Please edit .env file and add your GOOGLE_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if GOOGLE_API_KEY is set
if ! grep -q "GOOGLE_API_KEY=your_google_api_key_here" .env; then
    echo "✅ GOOGLE_API_KEY appears to be configured"
else
    echo "⚠️  Please set your GOOGLE_API_KEY in the .env file"
    echo "   Edit .env and replace 'your_google_api_key_here' with your actual API key"
    exit 1
fi

echo "🔨 Building AI Chatbot Docker image..."
docker build -t mobili-ai-chatbot:latest .

echo "🚀 Starting AI Chatbot service..."
docker-compose up -d

echo "⏳ Waiting for service to be ready..."
sleep 10

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ AI Chatbot service is healthy and running!"
    echo ""
    echo "🌐 Service URLs:"
    echo "   Health Check: http://localhost:8003/health"
    echo "   Chat API: http://localhost:8003/chat"
    echo "   Service Info: http://localhost:8003/"
    echo ""
    echo "🧪 Test with:"
    echo "   curl -X POST http://localhost:8003/chat -H 'Content-Type: application/json' -d '{\"prompt\":\"Show me temperature data\"}'"
else
    echo "❌ Health check failed. Service may not be ready yet."
    echo "📋 Check logs with: docker-compose logs ai-chatbot"
fi

echo ""
echo "🎯 To stop the service: docker-compose down"
echo "🔍 To view logs: docker-compose logs -f ai-chatbot"
