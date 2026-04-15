#!/usr/bin/env python3
"""
数据库代理客户端（用户端）
连接云服务器中继服务，执行本地数据库查询
支持灵活的表结构配置
"""
import asyncio
import json
import re
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import websockets
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理 datetime 类型"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)


load_dotenv()

RELAY_URL = os.getenv("RELAY_URL", "ws://localhost:8002")
CLIENT_ID = os.getenv("CLIENT_ID", "client_001")

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "student_talk_db")

TABLE_CONFIG = {
    "table_name": os.getenv("TABLE_NAME", "chat_records"),
    "student_id_field": os.getenv("STUDENT_ID_FIELD", "student_id"),
    "content_field": os.getenv("CONTENT_FIELD", "content"),
    "created_time_field": os.getenv("CREATED_TIME_FIELD", "created_time"),
    "query_limit": int(os.getenv("QUERY_LIMIT", "100"))
}


def _is_safe_identifier(identifier: str) -> bool:
    """验证SQL标识符安全"""
    return bool(re.match(r'^[A-Za-z0-9_]+$', identifier))


def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None


def execute_query(query, params=None):
    """执行 SQL 查询"""
    connection = get_db_connection()
    if not connection:
        return {"status": "error", "error": "数据库连接失败"}
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        processed_results = []
        for row in results:
            processed_row = dict(row)
            for key, value in processed_row.items():
                if isinstance(value, datetime):
                    processed_row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            processed_results.append(processed_row)
        
        return {"status": "success", "data": processed_results}
    except Error as e:
        return {"status": "error", "error": str(e)}


async def handle_request(request):
    """处理来自中继的请求"""
    action = request.get("action")
    params = request.get("params", {})
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 收到请求: {action}")
    
    try:
        if action == "chat_history":
            student_id = params.get("student_id", "")
            limit = params.get("limit", 100)
            
            table_name = TABLE_CONFIG["table_name"]
            student_id_field = TABLE_CONFIG["student_id_field"]
            content_field = TABLE_CONFIG["content_field"]
            created_time_field = TABLE_CONFIG["created_time_field"]
            query_limit = min(limit, TABLE_CONFIG["query_limit"])
            
            if not all(_is_safe_identifier(ident) for ident in 
                      [table_name, student_id_field, content_field, created_time_field]):
                return {"status": "error", "error": "表结构配置包含不安全的标识符"}
            
            query = f"""
                SELECT {content_field} as content, {created_time_field} as created_time 
                FROM {table_name} 
                WHERE {student_id_field} = %s 
                ORDER BY {created_time_field} ASC 
                LIMIT %s
            """
            result = execute_query(query, (student_id, query_limit))
            return result
            
        elif action == "health_check":
            connection = get_db_connection()
            if connection:
                connection.close()
                return {"status": "success", "data": {"database": "ok"}}
            else:
                return {"status": "error", "error": "数据库连接失败"}
        else:
            return {"status": "error", "error": f"未知的操作: {action}"}
            
    except Exception as e:
        print(f"处理请求出错: {e}")
        return {"status": "error", "error": str(e)}


async def main():
    """主函数"""
    print("=" * 60)
    print("数据库代理客户端启动中...")
    print("=" * 60)
    print(f"客户端ID: {CLIENT_ID}")
    print(f"中继服务: {RELAY_URL}")
    print(f"数据库: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    print(f"表结构: {TABLE_CONFIG['table_name']}")
    print(f"  - 学生ID字段: {TABLE_CONFIG['student_id_field']}")
    print(f"  - 内容字段: {TABLE_CONFIG['content_field']}")
    print(f"  - 时间字段: {TABLE_CONFIG['created_time_field']}")
    print(f"  - 查询限制: {TABLE_CONFIG['query_limit']}条")
    print("=" * 60)
    
    while True:
        try:
            ws_url = f"{RELAY_URL}/ws/client/{CLIENT_ID}"
            print(f"正在连接中继服务: {ws_url}")
            
            async with websockets.connect(ws_url) as websocket:
                print(f"已连接到中继服务: {CLIENT_ID}")
                
                while True:
                    try:
                        message = await websocket.recv()
                        request = json.loads(message)
                        request_id = request.get("request_id")
                        
                        response = await handle_request(request)
                        response["request_id"] = request_id
                        
                        await websocket.send(json.dumps(response, cls=DateTimeEncoder))
                        
                    except websockets.exceptions.ConnectionClosed:
                        print("与中继服务的连接已断开")
                        break
                    except Exception as e:
                        print(f"处理消息出错: {e}")
                        error_response = {
                            "request_id": request.get("request_id", ""),
                            "status": "error",
                            "error": str(e)
                        }
                        try:
                            await websocket.send(json.dumps(error_response, cls=DateTimeEncoder))
                        except:
                            pass
                        
        except Exception as e:
            print(f"连接失败: {e}")
            print("5秒后尝试重新连接...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
