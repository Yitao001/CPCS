#!/usr/bin/env python3
"""
测试并完整显示中继服务返回的学生谈话记录内容
将结果输出到文件，避免控制台编码问题
"""
import requests
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 确保控制台输出使用UTF-8编码，同时禁用特殊字符
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# 配置
RELAY_API_URL = os.getenv("RELAY_API_URL", "http://47.102.145.89:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")
RELAY_CLIENT_ID = os.getenv("RELAY_CLIENT_ID", "test_client_001")

def test_get_chat_history_directly():
    """直接测试中继服务的 /query 接口，获取并保存对话历史到文件"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"chat_history_result_{timestamp}.txt"
    
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
    
    try:
        print("正在请求中继服务...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # 将结果保存到文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("学生谈话记录详情\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("请求信息:\n")
                f.write(f"  URL: {url}\n")
                f.write(f"  Client ID: {RELAY_CLIENT_ID}\n")
                f.write(f"  学生ID: S2023003\n\n")
                
                f.write("完整响应内容:\n")
                f.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n\n")
                
                if result.get("status") == "success":
                    records = result.get("data", [])
                    f.write("=" * 80 + "\n")
                    f.write(f"学生谈话记录详情 (共 {len(records)} 条)\n")
                    f.write("=" * 80 + "\n")
                    
                    if not records:
                        f.write("\n没有找到任何谈话记录\n")
                    else:
                        for i, record in enumerate(records, 1):
                            f.write("\n" + "-" * 80 + "\n")
                            f.write(f"记录 #{i}\n")
                            f.write("-" * 80 + "\n")
                            
                            content = record.get("content", "")
                            created_time = record.get("created_time", "未知时间")
                            
                            f.write(f"时间: {created_time}\n")
                            f.write("\n谈话内容:\n")
                            f.write(f"  {content}\n")
                            
                            # 显示其他可能的字段
                            other_fields = {k: v for k, v in record.items() if k not in ["content", "created_time"]}
                            if other_fields:
                                f.write("\n其他字段:\n")
                                for key, value in other_fields.items():
                                    f.write(f"  {key}: {value}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("测试完成！\n")
                f.write("=" * 80 + "\n")
            
            print("测试完成！")
            print(f"结果已保存到文件: {output_file}")
            print("\n请打开文件查看完整的谈话记录内容！")
            
            # 同时读取并显示关键信息
            print("\n" + "=" * 80)
            print("关键信息摘要:")
            print("=" * 80)
            print(f"  状态: {result.get('status')}")
            print(f"  记录数: {len(result.get('data', []))}")
            
            records = result.get("data", [])
            if records:
                print("\n  第一条记录:")
                print(f"    时间: {records[0].get('created_time')}")
                print(f"    内容: {records[0].get('content')}")
                
                if len(records) > 1:
                    print("\n  第二条记录:")
                    print(f"    时间: {records[1].get('created_time')}")
                    print(f"    内容: {records[1].get('content')}")
            
            print(f"\n  完整内容请查看文件: {output_file}")
            print("=" * 80)
            
            # 读取并显示生成的文件内容
            print("\n" + "=" * 80)
            print("文件内容预览:")
            print("=" * 80)
            with open(output_file, 'r', encoding='utf-8') as f:
                print(f.read())
            
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("请求超时！请确保测试客户端正在运行并连接到中继服务")
    except requests.exceptions.ConnectionError:
        print("连接失败！请确保中继服务正在运行")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_chat_history_directly()
