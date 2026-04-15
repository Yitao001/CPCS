#!/usr/bin/env python3
"""
完整服务流程测试脚本
"""
import asyncio
import json
import websockets
import requests
import sys
from datetime import datetime

# ==========================================
# 配置（请根据您的实际情况修改）
# ==========================================
RELAY_URL = "ws://47.102.145.89:8002"  # 您的云服务器中继服务地址
RELAY_HTTP_URL = "http://47.102.145.89:8002"
RELAY_API_KEY = "relay_secret_key_123"
CLIENT_ID = "test_client_001"

AGENT_URL = "http://47.102.145.89:8000"
AGENT_API_KEY = "your_agent_api_key_here"  # 您的智能体API Key


async def test_client():
    """模拟客户端连接并处理请求"""
    print(f"[客户端] 正在连接中继服务: {RELAY_URL}/ws/client/{CLIENT_ID}")
    
    try:
        async with websockets.connect(f"{RELAY_URL}/ws/client/{CLIENT_ID}") as websocket:
            print(f"[客户端] ✅ 已连接到中继服务！")
            
            async def handle_messages():
                while True:
                    try:
                        message = await websocket.recv()
                        print(f"\n[客户端] 📨 收到请求: {message}")
                        
                        request = json.loads(message)
                        request_id = request.get("request_id")
                        action = request.get("action")
                        params = request.get("params", {})
                        
                        # 模拟处理请求
                        if action == "chat_history":
                            print(f"[客户端] 🔍 处理 chat_history 请求...")
                            student_id = params.get("student_id", "")
                            
                            # 模拟返回测试数据
                            response = {
                                "request_id": request_id,
                                "status": "success",
                                "data": [
                                    {
                                        "content": f"这是学生 {student_id} 的测试谈话记录1",
                                        "created_time": "2026-04-01 09:00:00"
                                    },
                                    {
                                        "content": f"这是学生 {student_id} 的测试谈话记录2",
                                        "created_time": "2026-04-02 14:30:00"
                                    }
                                ]
                            }
                        elif action == "health_check":
                            response = {
                                "request_id": request_id,
                                "status": "success",
                                "data": {"database": "ok"}
                            }
                        else:
                            response = {
                                "request_id": request_id,
                                "status": "error",
                                "error": f"未知操作: {action}"
                            }
                        
                        await websocket.send(json.dumps(response))
                        print(f"[客户端] ✅ 已发送响应")
                        
                    except Exception as e:
                        print(f"[客户端] ❌ 处理消息出错: {e}")
                        break
            
            await handle_messages()
            
    except Exception as e:
        print(f"[客户端] ❌ 连接失败: {e}")
        print(f"[客户端] 请检查:")
        print(f"  1. 网络连接是否正常")
        print(f"  2. 中继服务地址 {RELAY_URL} 是否正确")
        print(f"  3. 云服务器防火墙是否开放 8002 端口")


def test_relay_health():
    """测试中继服务健康检查"""
    print("\n" + "="*60)
    print("测试1: 中继服务健康检查")
    print("="*60)
    
    try:
        response = requests.get(f"{RELAY_HTTP_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 中继服务健康检查通过！")
            return True
        else:
            print("❌ 中继服务健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 中继服务健康检查出错: {e}")
        return False


def test_relay_clients():
    """测试查看已连接的客户端"""
    print("\n" + "="*60)
    print("测试2: 查看已连接的客户端")
    print("="*60)
    
    try:
        headers = {"X-API-Key": RELAY_API_KEY}
        response = requests.get(f"{RELAY_HTTP_URL}/clients", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            clients = response.json().get("clients", [])
            if CLIENT_ID in clients:
                print(f"✅ 找到测试客户端: {CLIENT_ID}")
                return True
            else:
                print(f"⚠️  未找到测试客户端: {CLIENT_ID}")
                print(f"   请确保测试客户端正在运行")
                return False
        else:
            print("❌ 获取客户端列表失败")
            return False
    except Exception as e:
        print(f"❌ 获取客户端列表出错: {e}")
        return False


def test_agent_health():
    """测试智能体健康检查"""
    print("\n" + "="*60)
    print("测试3: 智能体健康检查")
    print("="*60)
    
    try:
        headers = {"X-API-Key": AGENT_API_KEY}
        response = requests.get(f"{AGENT_URL}/health/lite", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 智能体健康检查通过！")
            return True
        else:
            print("❌ 智能体健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 智能体健康检查出错: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("完整服务流程测试")
    print("="*60)
    print(f"中继服务: {RELAY_URL}")
    print(f"智能体服务: {AGENT_URL}")
    print(f"测试客户端ID: {CLIENT_ID}")
    print("="*60)
    
    # 步骤1: 测试中继服务健康检查
    relay_ok = test_relay_health()
    if not relay_ok:
        print("\n❌ 请先确保中继服务正在运行！")
        sys.exit(1)
    
    # 步骤2: 在后台启动测试客户端
    print("\n" + "="*60)
    print("请在另一个终端运行以下命令启动测试客户端:")
    print("  python test_full_flow.py --client")
    print("="*60)
    print("启动客户端后，按回车键继续...")
    input()
    
    # 步骤3: 检查客户端是否连接
    client_ok = test_relay_clients()
    
    # 步骤4: 测试智能体健康检查
    agent_ok = test_agent_health()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"中继服务健康检查: {'✅ 通过' if relay_ok else '❌ 失败'}")
    print(f"测试客户端连接: {'✅ 成功' if client_ok else '❌ 失败'}")
    print(f"智能体健康检查: {'✅ 通过' if agent_ok else '❌ 失败'}")
    print("="*60)
    
    if relay_ok and client_ok and agent_ok:
        print("\n🎉 所有测试通过！完整服务流程正常！")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--client":
        # 仅运行客户端
        asyncio.run(test_client())
    else:
        # 运行完整测试
        main()
