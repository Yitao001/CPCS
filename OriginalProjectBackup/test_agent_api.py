#!/usr/bin/env python3
"""
直接测试智能体API调用，查看完整数据流
"""
import requests
import json

# 配置
AGENT_URL = "http://47.102.145.89:8000"
AGENT_API_KEY = "test_proxy_key_123"  # 请确保这个是正确的

def test_analyze_simple():
    """测试简化版人物画像分析"""
    print("=" * 60)
    print("测试智能体API调用")
    print("=" * 60)
    
    url = f"{AGENT_URL}/analyze/simple"
    headers = {
        "X-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "participant_id": "S2023003"
    }
    
    print(f"\n请求 URL: {url}")
    print(f"请求 Headers: {json.dumps({k: v for k, v in headers.items()}, indent=2)}")
    print(f"请求 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容:")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")

if __name__ == "__main__":
    test_analyze_simple()
