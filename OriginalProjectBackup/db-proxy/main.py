#!/usr/bin/env python3
"""
数据库代理服务 - 用户侧部署
企业级安全架构：智能体不直接访问用户数据库
"""
import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import mysql.connector
from mysql.connector import Error

load_dotenv()

app = FastAPI(
    title="数据库代理服务",
    description="用户侧数据库代理，安全访问本地数据库",
    version="1.0.0"
)

# API Key认证
api_key_header = APIKeyHeader(name="X-Proxy-API-Key", auto_error=False)
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "proxy_secure_key_change_this")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "student_talk_db"),
    "port": int(os.getenv("MYSQL_PORT", "3306"))
}

# 表结构配置
TABLE_CONFIG = {
    "table_name": os.getenv("TABLE_NAME", "talk_record"),
    "student_id_field": os.getenv("STUDENT_ID_FIELD", "student_id"),
    "content_field": os.getenv("CONTENT_FIELD", "content"),
    "created_time_field": os.getenv("CREATED_TIME_FIELD", "created_time"),
    "query_limit": int(os.getenv("QUERY_LIMIT", "100"))
}


def verify_api_key(api_key: str = Depends(api_key_header)):
    """验证API Key"""
    if not PROXY_API_KEY:
        return None
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少Proxy API Key"
        )
    if api_key != PROXY_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Proxy API Key"
        )
    return api_key


def _is_safe_identifier(identifier: str) -> bool:
    """验证SQL标识符安全"""
    return bool(re.match(r'^[A-Za-z0-9_]+$', identifier))


class ChatHistoryRequest(BaseModel):
    """获取对话历史请求"""
    student_id: str = Field(..., description="学生ID")
    limit: Optional[int] = Field(100, description="查询数量限制")


class ChatRecord(BaseModel):
    """对话记录"""
    content: str
    created_time: str


class ChatHistoryResponse(BaseModel):
    """对话历史响应"""
    status: str
    data: List[ChatRecord]
    message: str


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "数据库代理服务运行正常"}


@app.post("/chat-history", 
          summary="获取对话历史",
          response_model=ChatHistoryResponse)
async def get_chat_history(
    request: ChatHistoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    获取指定学生的对话历史
    
    Args:
        request: 包含学生ID和查询限制
        api_key: 代理API Key
    
    Returns:
        对话历史列表
    """
    try:
        table_name = TABLE_CONFIG["table_name"]
        student_id_field = TABLE_CONFIG["student_id_field"]
        content_field = TABLE_CONFIG["content_field"]
        created_time_field = TABLE_CONFIG["created_time_field"]
        query_limit = min(request.limit, TABLE_CONFIG["query_limit"])
        
        if not all(_is_safe_identifier(ident) for ident in 
                  [table_name, student_id_field, content_field, created_time_field]):
            raise HTTPException(
                status_code=400,
                detail="表结构配置包含不安全的标识符"
            )
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        query = f"""
        SELECT {content_field} as content, {created_time_field} as created_time
        FROM {table_name}
        WHERE {student_id_field} = %s
        ORDER BY {created_time_field} DESC
        LIMIT %s
        """
        
        cursor.execute(query, (request.student_id, query_limit))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        processed_results = []
        for row in results:
            processed_row = dict(row)
            if isinstance(processed_row.get("created_time"), datetime):
                processed_row["created_time"] = processed_row["created_time"].strftime("%Y-%m-%d %H:%M:%S")
            processed_results.append(processed_row)
        
        records = [ChatRecord(**row) for row in processed_results]
        
        return ChatHistoryResponse(
            status="success",
            data=records,
            message=f"获取到 {len(records)} 条记录"
        )
        
    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据库错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务错误: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("数据库代理服务启动中...")
    print("=" * 60)
    print(f"API文档: http://localhost:8001/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8001)
