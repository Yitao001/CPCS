#!/usr/bin/env python3
"""
详细测试：直接从中继服务获取原始数据
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv(".env.test")

RELAY_API_URL = os.getenv("RELAY_API_URL", "http://47.102.145.89:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")


def test_direct_relay_query():
    """直接测试中继服务查询"""
    print("=" * 60)
    print("直接测试中继服务查询")
    print("=" * 60)
    
    try:
        headers = {
            "X-API-Key": RELAY_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "client_id": "client_001",
            "action": "chat_history",
            "params": {
                "student_id": "S2023005",
                "limit": 100
            }
        }
        
        print(f"\n[1] 发送请求到中继服务")
        print(f"    URL: {RELAY_API_URL}/query")
        print(f"    参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            f"{RELAY_API_URL}/query",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n[2] 收到响应")
        print(f"    状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[3] 原始响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=4))
            
            print(f"\n[4] 响应详情:")
            print(f"    status: {data.get('status')}")
            print(f"    error: {data.get('error')}")
            
            if data.get("data"):
                print(f"    data 类型: {type(data.get('data'))}")
                if isinstance(data.get("data"), list):
                    print(f"    data 长度: {len(data.get('data'))}")
                    if len(data.get("data")) > 0:
                        print(f"\n[5] 第一条记录:")
                        print(json.dumps(data.get("data")[0], ensure_ascii=False, indent=4))
            return True, data
        else:
            print(f"\n[错误] 响应: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"\n[异常] {e}")
        import traceback
        traceback.print_exc()
        return False, None


if __name__ == "__main__":
    success, data = test_direct_relay_query()
    
    if success:
        print("\n" + "=" * 60)
        if data.get("status") == "success":
            print("✓ 中继服务查询成功！")
        else:
            print("✗ 中继服务返回错误")
        print("=" * 60)
