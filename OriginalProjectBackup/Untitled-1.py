#!/usr/bin/env python3
"""
人物画像分析API服务
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.tools.agent_tools import _generate_persona_from_db

# 创建FastAPI应用
app = FastAPI(
    title="人物画像分析API",
    description="根据用户ID分析人物画像的API服务",
    version="1.0.0"
)

# 请求模型
class PersonaRequest(BaseModel):
    participant_id: str

# 响应模型
class PersonaResponse(BaseModel):
    status: str
    data: str
    message: str

# 健康检查端点
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API服务运行正常"}

# 人物画像分析端点
@app.post("/analyze", response_model=PersonaResponse)
def analyze_persona(request: PersonaRequest):
    """
    根据用户ID分析人物画像
    """
    try:
        # 调用人物画像分析函数
        result = _generate_persona_from_db(participant_id=request.participant_id)
        
        # 返回成功响应
        return PersonaResponse(
            status="success",
            data=result,
            message="人物画像分析成功"
        )
    except Exception as e:
        # 返回错误响应
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)