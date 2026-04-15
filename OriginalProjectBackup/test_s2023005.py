#!/usr/bin/env python3
"""
测试 S2023005 学生的人物画像分析
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv(".env.test")

AGENT_URL = os.getenv("AGENT_URL", "http://47.102.145.89:8000")
AGENT_API_KEY = os.getenv("API_KEY", "test_proxy_key_123")


def test_s2023005_analysis():
    """测试 S2023005 学生的人物画像分析"""
    print("=" * 60)
    print("测试 S2023005 学生的人物画像分析")
    print("=" * 60)
    
    try:
        headers = {
            "X-API-Key": AGENT_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "participant_id": "S2023005"
        }
        
        print(f"\n[请求] 发送到: {AGENT_URL}/analyze/simple")
        print(f"[请求] 参数: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(
            f"{AGENT_URL}/analyze/simple",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"\n[响应] 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[响应] 完整数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            if data.get("status") == "success":
                print("\n" + "=" * 60)
                print("🎉 人物画像分析成功！")
                print("=" * 60)
                print("\n📊 分析结果:")
                print(data.get("data", ""))
                return True
            else:
                print(f"\n❌ 分析失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"\n❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        return False


if __name__ == "__main__":
    test_s2023005_analysis()
