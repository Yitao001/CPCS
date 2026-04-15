#!/usr/bin/env python3
"""
人物画像分析API服务
"""
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from agent.tools.agent_tools import generate_persona_from_db, generate_persona_simple_from_db, generate_persona_simple_from_db_stream
from fastapi.responses import StreamingResponse
from utils.config_handler import security_conf
from utils.logger_handler import logger
from utils.cache_manager import get_persona_cache
from utils.db_pool import get_db_pool
from model.factory import chat_model

# API Key认证
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 请求限流
limiter = Limiter(key_func=get_remote_address)

# 创建FastAPI应用
app = FastAPI(
    title="学生画像分析API",
    description="根据用户ID分析学生画像的API服务。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "安全",
            "description": "API认证说明：使用X-API-Key请求头进行认证"
        }
    ],
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# 配置OpenAPI安全方案
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "请输入您的API Key进行认证"
        }
    }
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 配置限流
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 配置CORS
cors_origins = [origin.strip() for origin in security_conf.get("cors_origins", []) if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key验证函数
async def get_api_key(api_key: str = Depends(api_key_header)):
    """验证API Key"""
    configured_key = security_conf.get("api_key", "")
    
    # 如果没有配置API Key，允许访问（开发模式）
    if not configured_key:
        logger.warning("[API] API Key未配置，运行在非安全模式！")
        return None
    
    # 如果没有提供API Key
    if not api_key:
        logger.warning("[API] 缺少API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少API Key"
        )
    
    if api_key != configured_key:
        logger.warning(f"[API] 无效的API Key尝试: {api_key[:10] if api_key else 'None'}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API Key"
        )
    return api_key

# 请求模型
class PersonaRequest(BaseModel):
    participant_id: str = Field(
        ..., 
        description="参与者ID（学生ID）",
        min_length=1,
        max_length=100,
        json_schema_extra={"example": "S2023003"}
    )
    
    @field_validator('participant_id')
    @classmethod
    def validate_participant_id(cls, v: str) -> str:
        """验证参与者ID格式"""
        if v is None:
            raise ValueError('参与者ID不能为空')
        
        v = v.strip()
        
        if len(v) == 0:
            raise ValueError('参与者ID不能为空')
        
        if len(v) > 100:
            raise ValueError('参与者ID长度不能超过100字符')
        
        if not all(c.isprintable() for c in v):
            raise ValueError('参与者ID包含不可打印字符')
        
        return v

# 响应模型
class PersonaResponse(BaseModel):
    status: str = Field(..., description="响应状态，success或error")
    data: str = Field(..., description="人物画像分析结果")
    message: str = Field(..., description="响应消息")

# 异常处理：验证错误
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "请求参数验证失败，请检查请求体格式",
            "detail": "正确的请求格式：{\"participant_id\": \"学生ID\"}",
            "example": {
                "participant_id": "S2023003"
            }
        }
    )

def check_database() -> dict:
    """检查数据库连接"""
    try:
        pool = get_db_pool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "ok", "message": "数据库连接正常"}
    except Exception as e:
        logger.error(f"[健康检查] 数据库连接失败: {e}")
        return {"status": "error", "message": f"数据库连接失败: {str(e)}"}


def check_llm() -> dict:
    """检查LLM连通性"""
    try:
        test_prompt = "请回复'OK'"
        response = chat_model.invoke(test_prompt)
        if response and hasattr(response, 'content'):
            return {"status": "ok", "message": "LLM连接正常"}
        return {"status": "error", "message": "LLM响应异常"}
    except Exception as e:
        logger.error(f"[健康检查] LLM连接失败: {e}")
        return {"status": "error", "message": f"LLM连接失败: {str(e)}"}


# 健康检查端点
@app.get("/health", summary="健康检查", description="检查API服务是否正常运行")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def health_check(request: Request, api_key: str = Depends(get_api_key)):
    """完整健康检查：数据库+LLM"""
    db_status = check_database()
    llm_status = check_llm()
    
    overall_status = "ok"
    if db_status["status"] == "error" or llm_status["status"] == "error":
        overall_status = "error"
    
    return {
        "status": overall_status,
        "message": "健康检查完成",
        "checks": {
            "api": {"status": "ok", "message": "API服务运行正常"},
            "database": db_status,
            "llm": llm_status
        }
    }


# 简化健康检查（快速）
@app.get("/health/lite", summary="轻量级健康检查", description="仅检查API服务状态，不检查数据库和LLM")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def health_check_lite(request: Request, api_key: str = Depends(get_api_key)):
    return {"status": "ok", "message": "API服务运行正常"}


# 系统状态端点
@app.get("/status", summary="系统状态", description="查看系统运行状态，包括缓存信息等")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def system_status(request: Request, api_key: str = Depends(get_api_key)):
    """
    查看系统状态
    """
    cache = get_persona_cache()
    cache_stats = cache.get_stats()
    
    return {
        "status": "ok",
        "cache": cache_stats,
        "performance": {
            "connection_pool": "enabled",
            "result_cache": "enabled"
        }
    }


# 清空缓存端点
@app.post("/cache/clear", summary="清空缓存", description="清空人物画像缓存")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def clear_cache(request: Request, api_key: str = Depends(get_api_key)):
    """
    清空缓存
    """
    cache = get_persona_cache()
    cache.clear()
    return {"status": "ok", "message": "缓存已清空"}

# 人物画像分析端点（完整版）
@app.post(
    "/analyze", 
    response_model=PersonaResponse,
    summary="分析人物画像（完整版）",
    description="根据参与者ID从数据库中获取对话记录并生成详细人物画像"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def analyze_persona(request: Request, persona_request: PersonaRequest, api_key: str = Depends(get_api_key)):
    """
    根据用户ID分析人物画像（完整版）
    
    - **participant_id**: 参与者ID（必填）
    """
    try:
        logger.info(f"[API] 收到人物画像分析请求，参与者ID: {persona_request.participant_id}")
        
        result = generate_persona_from_db(participant_id=persona_request.participant_id)
        
        logger.info(f"[API] 人物画像分析完成，参与者ID: {persona_request.participant_id}")
        
        return PersonaResponse(
            status="success",
            data=result,
            message="人物画像分析成功"
        )
    except Exception as e:
        logger.error(f"[API] 人物画像分析失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


# 人物画像分析端点（简化版）
@app.post(
    "/analyze/simple",
    summary="分析人物画像（简化版）",
    description="根据参与者ID生成简化版人物画像，只保留重要信息"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def analyze_persona_simple(request: Request, persona_request: PersonaRequest, api_key: str = Depends(get_api_key)):
    """
    根据用户ID分析人物画像（简化版）
    
    - **participant_id**: 参与者ID（必填）
    """
    try:
        logger.info(f"[API] 收到简化版人物画像分析请求，参与者ID: {persona_request.participant_id}")
        
        result = generate_persona_simple_from_db(participant_id=persona_request.participant_id)
        
        logger.info(f"[API] 简化版人物画像分析完成，参与者ID: {persona_request.participant_id}")
        
        return {
            "status": "success",
            "data": result,
            "message": "简化版人物画像分析成功"
        }
    except Exception as e:
        logger.error(f"[API] 简化版人物画像分析失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


# 人物画像分析端点（流式输出）
@app.post(
    "/analyze/stream",
    summary="分析人物画像（流式输出）",
    description="根据参与者ID流式生成简化版人物画像"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def analyze_persona_stream(request: Request, persona_request: PersonaRequest, api_key: str = Depends(get_api_key)):
    """
    根据用户ID分析人物画像（流式输出）
    
    - **participant_id**: 参与者ID（必填）
    """
    try:
        logger.info(f"[API] 收到流式人物画像分析请求，参与者ID: {persona_request.participant_id}")
        
        async def generate():
            async for chunk in generate_persona_simple_from_db_stream(
                participant_id=persona_request.participant_id
            ):
                yield chunk
        
        logger.info(f"[API] 流式人物画像分析完成，参与者ID: {persona_request.participant_id}")
        
        return StreamingResponse(
            generate(),
            media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"[API] 流式人物画像分析失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("人物画像分析API服务启动中...")
    print("=" * 60)
    print("API文档地址:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)