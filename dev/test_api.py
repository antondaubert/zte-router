#!/usr/bin/env python3
"""
Local test script for ZTE Router API
This mimics what the Home Assistant integration does, for quick testing
"""
import asyncio
import json
import getpass
from pathlib import Path
import importlib.util

# Load api.py directly without triggering __init__.py
api_path = Path(__file__).parent.parent / "custom_components" / "zte_router" / "api.py"
spec = importlib.util.spec_from_file_location("zte_api", api_path)
zte_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zte_api)
ZTERouterAPI = zte_api.ZTERouterAPI

HOST = "192.168.0.1"


async def main():
    """Test the API."""
    # Prompt for password
    print("=" * 70)
    print("ZTE Router API Test Script")
    print("=" * 70)
    password = getpass.getpass("Enter router password: ")
    
    if not password:
        print("❌ Password is required")
        return
    
    api = ZTERouterAPI(HOST, password)
    
    try:
        data = await api.async_update()
        
        print("\n" + "=" * 70)
        print("Final Result")
        print("=" * 70)
        print(json.dumps(data, indent=2))
        
        # Check what data we got
        print("\n" + "=" * 70)
        print("Data Summary")
        print("=" * 70)
        
        if data["router_status"]:
            print(f"✅ Router Status: {len(data['router_status'])} fields")
            print(f"   Keys: {list(data['router_status'].keys())[:10]}...")
        else:
            print("❌ Router Status: No data")
            
        if data["network_info"]:
            print(f"✅ Network Info: {len(data['network_info'])} fields")
            print(f"   Keys: {list(data['network_info'].keys())[:10]}...")
        else:
            print("❌ Network Info: No data")
            
        if data["data_usage"]:
            print(f"✅ Data Usage: {len(data['data_usage'])} fields")
            print(f"   Keys: {list(data['data_usage'].keys())[:10]}...")
        else:
            print("❌ Data Usage: No data")
            
    finally:
        await api.close()
        print("\n✅ Session closed")


if __name__ == "__main__":
    asyncio.run(main())
