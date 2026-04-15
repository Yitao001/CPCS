#!/usr/bin/env python3
"""
清晰的中继服务测试脚本 - 不带emoji
"""
import requests
import json
from dotenv import load_dotenv
import os
import sys

load_dotenv(".env.test")

RELAY_API_URL = os.getenv("RELAY_API_URL", "http://47.102.145.89:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")
AGENT_URL = os.getenv("AGENT_URL", "http://47.102.145.89:8000")
AGENT_API_KEY = os.getenv("API_KEY", "test_proxy_key_123")


def print_separator(title=""):
    print()
    print("=" * 60)
    if title:
        print(title)
        print("=" * 60)


def test_relay_query():
    print_separator("测试1: 直接从中继服务获取S2023005数据")
    
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
        
        print("请求URL:", f"{RELAY_API_URL}/query")
        print("请求参数:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        
        response = requests.post(
            f"{RELAY_API_URL}/query",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print()
        print("响应状态码:", response.status_code)
        
        if response.status_code == 200:
            data = response.json()
            print()
            print("完整响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=4))
            
            if data.get("status") == "success":
                print()
                print("查询成功!")
                records = data.get("data", [])
                print(f"找到 {len(records)} 条记录")
                
                if records:
                    print()
                    print("记录详情:")
                    for i, record in enumerate(records, 1):
                        print(f"\n[{i}]")
                        print(json.dumps(record, ensure_ascii=False, indent=4))
                
                return True, data
            else:
                print()
                print("查询失败!")
                print("错误信息:", data.get("error", "未知错误"))
                return False, data
        else:
            print()
            print("请求失败!")
            print("响应内容:", response.text)
            return False, None
            
    except Exception as e:
        print()
        print("发生异常!")
        print("异常类型:", type(e).__name__)
        print("异常信息:", str(e))
        import traceback
        print()
        print("详细堆栈:")
        traceback.print_exc()
        return False, None


def test_agent_analysis():
    print_separator("测试2: 调用智能体分析S2023005")
    
    try:
        headers = {
            "X-API-Key": AGENT_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "participant_id": "S2023005"
        }
        
        print("请求URL:", f"{AGENT_URL}/analyze/simple")
        print("请求参数:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        
        response = requests.post(
            f"{AGENT_URL}/analyze/simple",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print()
        print("响应状态码:", response.status_code)
        
        if response.status_code == 200:
            data = response.json()
            print()
            print("完整响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=4))
            
            if data.get("status") == "success":
                print()
                print("分析成功!")
                print()
                print("人物画像分析结果:")
                print("-" * 60)
                print(data.get("data", ""))
                print("-" * 60)
                return True, data
            else:
                print()
                print("分析失败!")
                print("错误信息:", data.get("message", "未知错误"))
                return False, data
        else:
            print()
            print("请求失败!")
            print("响应内容:", response.text)
            return False, None
            
    except Exception as e:
        print()
        print("发生异常!")
        print("异常类型:", type(e).__name__)
        print("异常信息:", str(e))
        import traceback
        print()
        print("详细堆栈:")
        traceback.print_exc()
        return False, None


def main():
    print_separator("S2023005 完整测试")
    
    relay_success, relay_data = test_relay_query()
    
    if relay_success and relay_data and relay_data.get("status") == "success":
        agent_success, agent_data = test_agent_analysis()
    else:
        print()
        print_separator("测试总结")
        print("中继服务查询失败，跳过智能体分析测试")
        print()
        print("请先解决中继服务的问题:")
        print("1. 确保服务器上已拉取最新代码 (git pull)")
        print("2. 确保已停止旧的db-proxy-client进程")
        print("3. 确保已使用新代码重启客户端")
        print("4. 确保.env配置正确:")
        print("   TABLE_NAME=talk_record")
        print("   STUDENT_ID_FIELD=studentNo")
        print("   CONTENT_FIELD=content")
        print("   CREATED_TIME_FIELD=talkTime")
        sys.exit(1)
    
    print_separator("测试总结")
    print()
    print("中继服务查询:", "成功" if relay_success else "失败")
    print("智能体分析:", "成功" if agent_success else "失败")
    print()


if __name__ == "__main__":
    main()
