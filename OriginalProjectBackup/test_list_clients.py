#!/usr/bin/env python3
"""
简单的测试脚本：查看已连接的客户端
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv(".env.test")

RELAY_API_URL = os.getenv("RELAY_API_URL", "http://47.102.145.89:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")


def list_clients():
    print("=" * 60)
    print("查看已连接的客户端")
    print("=" * 60)
    
    try:
        headers = {
            "X-API-Key": RELAY_API_KEY
        }
        
        print("\n[请求]")
        print(f"URL: {RELAY_API_URL}/clients")
        print(f"API Key: {RELAY_API_KEY}")
        
        response = requests.get(
            f"{RELAY_API_URL}/clients",
            headers=headers,
            timeout=5
        )
        
        print(f"\n[响应]")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n完整数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            clients = data.get("clients", [])
            if clients:
                print(f"\n找到 {len(clients)} 个已连接的客户端:")
                for i, client in enumerate(clients, 1):
                    print(f"  [{i}] {client}")
            else:
                print("\n没有已连接的客户端")
            
            return True
        else:
            print(f"\n请求失败:")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    list_clients()
