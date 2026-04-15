#!/usr/bin/env python3
"""
数据库代理中继服务（云服务器端）
使用 WebSocket 实现智能体和客户端之间的通信
"""
import asyncio
import json
import uuid
import logging
from typing import Dict, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="数据库代理中继服务",
    description="智能体与客户端之间的 WebSocket 中继服务",
    version="1.0.0"
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")

clients: Dict[str, WebSocket] = {}
pending_requests: Dict[str, asyncio.Queue] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    client_id: str
    action: str
    params: dict


class QueryResponse(BaseModel):
    request_id: str
    status: str
    data: Optional[dict] = None
    error: Optional[str] = None


async def verify_api_key(api_key: str = Depends(api_key_header)):
    """验证 API Key"""
    if api_key != RELAY_API_KEY:
        raise HTTPException(status_code=401, detail="无效的 API Key")
    return api_key


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "connected_clients": len(clients),
        "pending_requests": len(pending_requests)
    }


@app.get("/clients")
async def list_clients(api_key: str = Depends(verify_api_key)):
    """列出已连接的客户端"""
    return {
        "status": "success",
        "clients": list(clients.keys())
    }


@app.websocket("/ws/client/{client_id}")
async def client_websocket(websocket: WebSocket, client_id: str):
    """客户端连接端点"""
    await websocket.accept()
    clients[client_id] = websocket
    logger.info(f"[中继] 客户端已连接: {client_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                request_id = message.get("request_id")
                
                if request_id and request_id in pending_requests:
                    await pending_requests[request_id].put(message)
                    del pending_requests[request_id]
            except json.JSONDecodeError:
                logger.error(f"[中继] 收到无效的 JSON: {data}")
    except WebSocketDisconnect:
        logger.info(f"[中继] 客户端已断开: {client_id}")
    except Exception as e:
        logger.error(f"[中继] 客户端连接错误: {client_id}, 错误: {e}")
    finally:
        if client_id in clients:
            del clients[client_id]


@app.post("/query")
async def query_client(request: QueryRequest, api_key: str = Depends(verify_api_key)):
    """向客户端发送查询请求"""
    client_id = request.client_id
    
    if client_id not in clients:
        raise HTTPException(status_code=404, detail=f"客户端未连接: {client_id}")
    
    request_id = str(uuid.uuid4())
    request_message = {
        "request_id": request_id,
        "action": request.action,
        "params": request.params,
        "timestamp": datetime.now().isoformat()
    }
    
    response_queue = asyncio.Queue()
    pending_requests[request_id] = response_queue
    
    try:
        await clients[client_id].send_text(json.dumps(request_message))
        logger.info(f"[中继] 已发送请求到客户端 {client_id}: {request.action}")
        
        try:
            response = await asyncio.wait_for(response_queue.get(), timeout=30.0)
            logger.info(f"[中继] 收到客户端 {client_id} 的响应")
            return response
        except asyncio.TimeoutError:
            if request_id in pending_requests:
                del pending_requests[request_id]
            raise HTTPException(status_code=504, detail="请求超时")
            
    except Exception as e:
        if request_id in pending_requests:
            del pending_requests[request_id]
        logger.error(f"[中继] 查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("数据库代理中继服务启动中...")
    print("=" * 60)
    print("API文档地址:")
    print("  - Swagger UI: http://localhost:8002/docs")
    print("  - ReDoc: http://localhost:8002/redoc")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8002)
