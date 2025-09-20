#!/usr/bin/env python3
"""
Simple test script for Azure AI integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import our services
from app.services.azure_openai import AzureOpenAIService
from app.core.config import settings

async def test_azure_ai():
    """Test Azure AI integration"""
    print("🧪 Testing Azure AI Integration")
    print("=" * 50)
    
    # Check configuration
    print(f"Azure OpenAI Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    print(f"API Key configured: {bool(settings.AZURE_OPENAI_API_KEY)}")
    print(f"Deployment Name: {settings.AZURE_OPENAI_DEPLOYMENT_NAME}")
    print("")
    
    # Test service initialization
    service = AzureOpenAIService()
    print(f"Service available: {service.is_available()}")
    
    if not service.is_available():
        print("⚠️  Azure AI service not available - will test with mock responses")
        print("To enable Azure AI:")
        print("1. Update AZURE_OPENAI_ENDPOINT in .env file")
        print("2. Update AZURE_OPENAI_API_KEY in .env file")
        print("")
    
    # Test chat completion
    print("Testing chat completion...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Can you help me plan a scout activity?"}
    ]
    
    try:
        response = await service.chat_completion(messages)
        print(f"✅ Response received: {response.get('message', 'No message')[:100]}...")
        print(f"Usage: {response.get('usage', 'N/A')}")
        
        if response.get('mock'):
            print("📝 This was a mock response (Azure AI not configured)")
        else:
            print("🚀 Real Azure AI response!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Azure AI integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_azure_ai())