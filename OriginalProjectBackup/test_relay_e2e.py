#!/usr/bin/env python3
"""
完整的中继服务端到端测试
测试中继服务、智能体API、数据库代理客户端的完整流程
"""
import asyncio
import json
import websockets
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

env_file = os.getenv("ENV_FILE", ".env.test")
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

RELAY_URL = os.getenv("RELAY_URL", "ws://47.102.145.89:8002")
RELAY_API_URL = os.getenv("RELAY_API_URL", "http://47.102.145.89:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")
AGENT_URL = os.getenv("AGENT_URL", "http://47.102.145.89:8000")
AGENT_API_KEY = os.getenv("API_KEY", "test_proxy_key_123")


def print_banner(title):
    """打印标题横幅"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_success(message):
    """打印成功信息"""
    print(f"[OK] {message}")


def print_error(message):
    """打印错误信息"""
    print(f"[FAIL] {message}")


def print_info(message):
    """打印信息"""
    print(f"[INFO] {message}")


async def test_relay_health():
    """测试中继服务健康检查"""
    print_banner("测试1: 中继服务健康检查")
    try:
        response = requests.get(f"{RELAY_API_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print_success("中继服务健康检查通过")
            return True
        else:
            print_error("中继服务健康检查失败")
            return False
    except Exception as e:
        print_error(f"中继服务健康检查异常: {e}")
        return False


async def test_agent_health():
    """测试智能体健康检查"""
    print_banner("测试2: 智能体健康检查")
    try:
        headers = {"X-API-Key": AGENT_API_KEY}
        response = requests.get(f"{AGENT_URL}/health/lite", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print_success("智能体健康检查通过")
            return True
        else:
            print(f"响应: {response.text}")
            print_error("智能体健康检查失败")
            return False
    except Exception as e:
        print_error(f"智能体健康检查异常: {e}")
        return False


async def test_relay_list_clients():
    """测试列出已连接的客户端"""
    print_banner("测试3: 列出已连接的客户端")
    try:
        headers = {"X-API-Key": RELAY_API_KEY}
        response = requests.get(f"{RELAY_API_URL}/clients", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            clients = data.get("clients", [])
            if clients:
                print_success(f"找到 {len(clients)} 个已连接的客户端: {', '.join(clients)}")
                return True, clients
            else:
                print_info("没有已连接的客户端")
                return True, []
        else:
            print_error("获取客户端列表失败")
            return False, []
    except Exception as e:
        print_error(f"获取客户端列表异常: {e}")
        return False, []


async def test_mock_client():
    """启动测试模拟客户端"""
    print_banner("测试4: 启动模拟客户端")
    test_client_id = "test_client_e2e"
    
    async def mock_client_handler():
        try:
            ws_url = f"{RELAY_URL}/ws/client/{test_client_id}"
            print_info(f"正在连接: {ws_url}")
            
            async with websockets.connect(ws_url) as websocket:
                print_success(f"模拟客户端已连接: {test_client_id}")
                
                while True:
                    try:
                        message = await websocket.recv()
                        print_info(f"[模拟客户端] 收到请求: {message}")
                        
                        request = json.loads(message)
                        request_id = request.get("request_id")
                        action = request.get("action")
                        params = request.get("params", {})
                        
                        if action == "chat_history":
                            student_id = params.get("student_id")
                            print_info(f"[模拟客户端] 处理 chat_history 请求: {student_id}")
                            
                            mock_data = [
                                {
                                    "content": f"模拟数据 - 学生 {student_id} 的谈话记录 1",
                                    "created_time": "2026-04-01 09:00:00"
                                },
                                {
                                    "content": f"模拟数据 - 学生 {student_id} 的谈话记录 2",
                                    "created_time": "2026-04-02 14:30:00"
                                }
                            ]
                            
                            response = {
                                "request_id": request_id,
                                "status": "success",
                                "data": mock_data
                            }
                            
                            print_info(f"[模拟客户端] 发送响应: {json.dumps(response, ensure_ascii=False)}")
                            await websocket.send(json.dumps(response))
                            print_success("模拟客户端已响应")
                        elif action == "health_check":
                            response = {
                                "request_id": request_id,
                                "status": "success",
                                "data": {"database": "ok"}
                            }
                            await websocket.send(json.dumps(response))
                        else:
                            response = {
                                "request_id": request_id,
                                "status": "error",
                                "error": f"未知操作: {action}"
                            }
                            await websocket.send(json.dumps(response))
                            
                    except websockets.exceptions.ConnectionClosed:
                        print_error("模拟客户端连接已断开")
                        break
                    except Exception as e:
                        print_error(f"模拟客户端处理消息出错: {e}")
                        error_response = {
                            "request_id": request.get("request_id", ""),
                            "status": "error",
                            "error": str(e)
                        }
                        try:
                            await websocket.send(json.dumps(error_response))
                        except:
                            pass
                            
        except Exception as e:
            print_error(f"模拟客户端连接失败: {e}")
    
    client_task = asyncio.create_task(mock_client_handler())
    await asyncio.sleep(2)
    
    return test_client_id, client_task


async def test_query_relay(client_id):
    """测试通过中继服务查询"""
    print_banner("测试5: 通过中继服务查询")
    try:
        headers = {
            "X-API-Key": RELAY_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "client_id": client_id,
            "action": "chat_history",
            "params": {
                "student_id": "S2023001",
                "limit": 100
            }
        }
        
        print_info(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(
            f"{RELAY_API_URL}/query",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print_success("中继服务查询成功")
            return True, data
        else:
            print(f"响应: {response.text}")
            print_error("中继服务查询失败")
            return False, None
    except Exception as e:
        print_error(f"中继服务查询异常: {e}")
        return False, None


async def test_agent_simple_analysis():
    """测试智能体简化版分析（使用模拟客户端）"""
    print_banner("测试6: 智能体简化版分析")
    try:
        headers = {
            "X-API-Key": AGENT_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "participant_id": "S2023001"
        }
        
        print_info(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(
            f"{AGENT_URL}/analyze/simple",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print_success("智能体分析成功")
            return True
        else:
            print(f"响应: {response.text}")
            print_error("智能体分析失败")
            return False
    except Exception as e:
        print_error(f"智能体分析异常: {e}")
        return False


async def main():
    """主测试函数"""
    print_banner("中继服务端到端测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    mock_client_task = None
    
    try:
        result = await test_relay_health()
        results.append(("中继服务健康检查", result))
        
        if not result:
            print_error("中继服务不可用，停止测试")
            return
        
        result = await test_agent_health()
        results.append(("智能体健康检查", result))
        
        has_clients, clients = await test_relay_list_clients()
        results.append(("列出客户端", has_clients))
        
        if not clients:
            print_info("没有已连接的客户端，启动模拟客户端")
            test_client_id, mock_client_task = await test_mock_client()
            await asyncio.sleep(2)
            
            has_clients, clients = await test_relay_list_clients()
            if test_client_id in clients:
                print_success("模拟客户端已成功连接")
            else:
                print_error("模拟客户端连接失败")
                return
        else:
            test_client_id = clients[0]
            print_info(f"使用已连接的客户端: {test_client_id}")
        
        query_success, query_data = await test_query_relay(test_client_id)
        results.append(("中继服务查询", query_success))
        
        if query_success:
            analysis_success = await test_agent_simple_analysis()
            results.append(("智能体分析", analysis_success))
        
    except Exception as e:
        print_error(f"测试异常: {e}")
    finally:
        if mock_client_task:
            print_info("停止模拟客户端")
            mock_client_task.cancel()
            try:
                await mock_client_task
            except asyncio.CancelledError:
                pass
    
    print_banner("测试总结")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("")
    if all_passed:
        print_success("所有测试通过！")
    else:
        print_error("部分测试失败，请检查上述错误信息")


if __name__ == "__main__":
    asyncio.run(main())
