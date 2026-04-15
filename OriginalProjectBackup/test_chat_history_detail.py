#!/usr/bin/env python3
"""
测试并完整显示中继服务返回的学生谈话记录内容
"""
import requests
import json
import os
import sys
from dotenv import load_dotenv

# 确保控制台输出使用UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# 配置
RELAY_API_URL = os.getenv("RELAY_API_URL", "http://47.102.145.89:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")
RELAY_CLIENT_ID = os.getenv("RELAY_CLIENT_ID", "test_client_001")

def test_get_chat_history_directly():
    """直接测试中继服务的 /query 接口，获取并完整显示对话历史"""
    print("=" * 80)
    print("直接测试中继服务 - 完整显示学生谈话记录")
    print("=" * 80)
    
    url = f"{RELAY_API_URL.rstrip('/')}/query"
    headers = {
        "X-API-Key": RELAY_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "client_id": RELAY_CLIENT_ID,
        "action": "chat_history",
        "params": {
            "student_id": "S2023003",
            "limit": 100
        }
    }
    
    print("\n请求信息:")
    print(f"  URL: {url}")
    print(f"  Client ID: {RELAY_CLIENT_ID}")
    print(f"  学生ID: S2023003")
    print("\n请求 Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        print("\n正在请求中继服务...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print("\n响应信息:")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n完整响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("status") == "success":
                records = result.get("data", [])
                
                print("\n" + "=" * 80)
                print(f"学生谈话记录详情 (共 {len(records)} 条)")
                print("=" * 80)
                
                if not records:
                    print("\n没有找到任何谈话记录")
                else:
                    for i, record in enumerate(records, 1):
                        print(f"\n{'─' * 80}")
                        print(f"记录 #{i}")
                        print(f"{'─' * 80}")
                        
                        content = record.get("content", "")
                        created_time = record.get("created_time", "未知时间")
                        
                        print(f"时间: {created_time}")
                        print("\n谈话内容:")
                        print(f"  {content}")
                        
                        # 显示其他可能的字段
                        other_fields = {k: v for k, v in record.items() if k not in ["content", "created_time"]}
                        if other_fields:
                            print("\n其他字段:")
                            for key, value in other_fields.items():
                                print(f"  {key}: {value}")
                
                print("\n" + "=" * 80)
                print("测试完成！")
                print("=" * 80)
            else:
                print(f"\n中继服务返回错误: {result.get('error', '未知错误')}")
        else:
            print(f"\n请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n请求超时！请确保测试客户端正在运行并连接到中继服务")
    except requests.exceptions.ConnectionError:
        print("\n连接失败！请确保中继服务正在运行")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_chat_history_directly()
