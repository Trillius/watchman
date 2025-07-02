#!/usr/bin/env python3
"""
Example script to test the Discord bot API endpoints.
This demonstrates how to send status reports, events, and news updates to the bot.
"""

import requests
import json
from datetime import datetime
import os
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8080"
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your_api_key_here")

def make_api_request(endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make an authenticated API request."""
    headers = {
        "Authorization": f"Bearer {API_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}{endpoint}", 
                                   headers=headers, 
                                   json=data)
        else:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    result = make_api_request("/health")
    if result:
        print(f"✅ Health check passed: {json.dumps(result, indent=2)}")
    else:
        print("❌ Health check failed")

def test_status_report():
    """Test sending a status report."""
    print("\nTesting status report...")
    data = {
        "server_name": "Test Server",
        "status": "online",
        "message": "Test status report from API client",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "version": "1.0.0",
            "environment": "test",
            "uptime": "1h 30m"
        }
    }
    
    result = make_api_request("/status", data)
    if result:
        print(f"✅ Status report sent: {json.dumps(result, indent=2)}")
    else:
        print("❌ Status report failed")

def test_event_report():
    """Test sending an event report."""
    print("\nTesting event report...")
    data = {
        "event_type": "test",
        "source": "API Test Script",
        "title": "Test Event",
        "description": "This is a test event from the API client script",
        "severity": "info",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "test_run": True,
            "script_version": "1.0"
        }
    }
    
    result = make_api_request("/event", data)
    if result:
        print(f"✅ Event report sent: {json.dumps(result, indent=2)}")
    else:
        print("❌ Event report failed")

def test_news_update():
    """Test sending a news update."""
    print("\nTesting news update...")
    data = {
        "title": "Test News Update",
        "content": "This is a test news update sent via the API client script.",
        "source": "API Test Script",
        "url": "https://example.com/test",
        "timestamp": datetime.now().isoformat()
    }
    
    result = make_api_request("/news", data)
    if result:
        print(f"✅ News update sent: {json.dumps(result, indent=2)}")
    else:
        print("❌ News update failed")

def main():
    """Run all API tests."""
    print("Discord Bot API Test Script")
    print("=" * 40)
    
    if API_SECRET_KEY == "your_api_key_here":
        print("⚠️  Please set your API_SECRET_KEY environment variable")
        print("   Example: export API_SECRET_KEY=your_actual_key")
        return
    
    # Test all endpoints
    test_health_check()
    test_status_report()
    test_event_report()
    test_news_update()
    
    print("\n" + "=" * 40)
    print("API testing completed!")

if __name__ == "__main__":
    main()
