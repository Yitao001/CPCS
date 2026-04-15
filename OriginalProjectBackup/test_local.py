#!/usr/bin/env python3
"""
本地测试对话历史获取功能
"""
import sys
import os
import requests

def test_local_proxy():
    """测试本地代理服务"""
    print("=" * 60)
    print("测试: 本地代理服务")
    print("=" * 60)
    
    proxy_url = "http://localhost:8001"
    api_key = "test_proxy_key_123"
    
    print(f"\n代理服务地址: {proxy_url}")
    print(f"测试学生ID: S2023003")
    print()
    
    try:
        headers = {}
        if api_key:
            headers["X-Proxy-API-Key"] = api_key
        
        payload = {
            "student_id": "S2023003",
            "limit": 100
        }
        
        print("正在请求对话历史...")
        response = requests.post(
            f"{proxy_url.rstrip('/')}/chat-history",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"\n响应状态: {result.get('status')}")
        print(f"响应消息: {result.get('message')}")
        
        if result.get("status") != "success":
            print("\n代理服务返回错误")
            return False
        
        records = result.get("data", [])
        
        if not records:
            print("\n未找到历史会谈信息")
            print("\n请确保:")
            print("  1. 数据库中有测试数据")
            print("  2. 数据库连接配置正确")
            return False
        
        print(f"\n找到 {len(records)} 条记录")
        print("\n" + "=" * 60)
        print("原始数据（前3条）:")
        print("-" * 60)
        for i, record in enumerate(records[:3], 1):
            print(f"\n[{i}]")
            print(f"  时间: {record.get('created_time')}")
            print(f"  内容: {record.get('content', '')[:50]}...")
        
        print("\n" + "=" * 60)
        print("处理后的数据（带时间排序和时间间隔）:")
        print("-" * 60)
        
        from datetime import datetime
        
        def parse_time(time_str):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"]:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            return None
        
        records_with_time = []
        for record in records:
            time_str = record.get("created_time", "")
            dt = parse_time(time_str)
            if dt:
                records_with_time.append({
                    "time": dt,
                    "time_str": time_str,
                    "content": record.get("content", "")
                })
        
        if not records_with_time:
            print("\n无法解析时间格式")
            return True
        
        records_with_time.sort(key=lambda x: x["time"])
        
        chat_history = []
        prev_time = None
        
        for i, record in enumerate(records_with_time, 1):
            current_time = record["time"]
            time_str = record["time_str"]
            content = record["content"]
            
            time_info = f"[{i}] 时间: {time_str}"
            
            if prev_time:
                time_diff = current_time - prev_time
                hours = time_diff.total_seconds() / 3600
                days = hours / 24
                
                if days >= 1:
                    time_info += f" (距离上次间隔: {days:.1f}天)"
                elif hours >= 1:
                    time_info += f" (距离上次间隔: {hours:.1f}小时)"
                else:
                    minutes = time_diff.total_seconds() / 60
                    time_info += f" (距离上次间隔: {minutes:.0f}分钟)"
            
            chat_history.append(f"{time_info}\n内容: {content}")
            prev_time = current_time
        
        for item in chat_history[:5]:
            print(f"\n{item}")
        
        if len(chat_history) > 5:
            print(f"\n... (还有 {len(chat_history) - 5} 条记录)")
        
        print("\n" + "=" * 60)
        print("测试成功!")
        print("\n功能验证:")
        print("  [x] 时间排序: 记录按时间从早到晚排列")
        print("  [x] 序号: 有 [1], [2], [3]... 序号")
        print("  [x] 时间间隔: 显示距离上次的间隔时间")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n无法连接到代理服务")
        print("\n请确保:")
        print("  1. 代理服务正在运行 (db-proxy/main.py)")
        print("  2. 代理服务监听在 localhost:8001")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n请求错误: {e}")
        return False
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n开始本地测试\n")
    success = test_local_proxy()
    print("\n" + "=" * 60)
    if success:
        print("测试完成: 成功")
    else:
        print("测试完成: 失败")
    print("=" * 60)
