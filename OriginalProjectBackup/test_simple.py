#!/usr/bin/env python3
"""
简单测试：直接获取并输出JSON格式的谈话记录
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

RELAY_API_URL = os.getenv("RELAY_API_URL", "http://47.102.145.89:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")
RELAY_CLIENT_ID = os.getenv("RELAY_CLIENT_ID", "test_client_001")

url = f"{RELAY_API_URL.rstrip('/')}/query"
headers = {"X-API-Key": RELAY_API_KEY, "Content-Type": "application/json"}
payload = {
    "client_id": RELAY_CLIENT_ID,
    "action": "chat_history",
    "params": {"student_id": "S2023003", "limit": 100}
}

response = requests.post(url, json=payload, headers=headers, timeout=30)
result = response.json()

# 保存到JSON文件
with open("chat_history.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("Result saved to chat_history.json")
print("\n" + "="*80)
print(json.dumps(result, indent=2, ensure_ascii=False))
print("="*80)
