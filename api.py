#!/usr/bin/env python3
"""
大学生职业规划智能体 API服务
"""
from fastapi import FastAPI, HTTPException, Request, Depends, status, UploadFile, File
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json

from agent.tools.agent_tools import (
    career_assessment_from_info,
    course_recommendation_from_info,
    job_guidance_from_info,
    parse_resume_from_info,
    job_matching_analysis_from_info,
    generate_career_report_from_info,
    export_career_report_from_info
)
from data.data_manager import (
    student_profile_manager,
    report_manager
)
from data.excel_importer import search_jobs
from data.vector_db_manager import vector_db_manager
from agent.react_agent import ReactAgent
from utils.config_handler import security_conf, server_conf
from utils.logger_handler import logger
from utils.cache_manager import get_career_cache
from model.factory import chat_model

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="大学生职业规划智能体 API",
    description="为大学生提供职业测评、课程推荐、就业指导、岗位画像、学生能力画像、人岗匹配、职业发展报告等服务的API。",
    version="2.0.0",
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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = [origin.strip() for origin in security_conf.get("cors_origins", []) if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from utils.path_tool import get_abs_path

frontend_dir = get_abs_path("frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")
    logger.info(f"[API] 前端静态文件已挂载: {frontend_dir}")

async def get_api_key(api_key: str = Depends(api_key_header)):
    configured_key = security_conf.get("api_key", "")
    
    if not configured_key:
        logger.warning("[API] API Key未配置，运行在非安全模式！")
        return None
    
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

career_agent = ReactAgent()

class CareerAssessmentRequest(BaseModel):
    student_info: str = Field(..., description="学生基本信息（年级、专业、兴趣、能力等）", min_length=1)
    student_name: str = Field("学生", description="学生姓名（可选）")

class CourseRecommendationRequest(BaseModel):
    student_info: str = Field(..., description="学生基本信息", min_length=1)
    career_goal: str = Field(..., description="职业目标", min_length=1)

class JobGuidanceRequest(BaseModel):
    student_info: str = Field(..., description="学生基本信息", min_length=1)
    target_position: str = Field(..., description="目标行业/职位", min_length=1)

class ParseResumeRequest(BaseModel):
    resume_content: str = Field(..., description="简历内容", min_length=1)
    student_id: str = Field("", description="学生ID（可选）")

class JobMatchingRequest(BaseModel):
    student_id: str = Field(..., description="学生ID", min_length=1)
    job_name: str = Field("", description="目标岗位名称")
    job_code: str = Field("", description="目标岗位编码")

class CareerReportRequest(BaseModel):
    student_id: str = Field(..., description="学生ID", min_length=1)
    student_info: str = Field(..., description="学生基本信息", min_length=1)
    job_name: str = Field("", description="目标岗位名称")
    job_code: str = Field("", description="目标岗位编码")

class ExportReportRequest(BaseModel):
    student_id: str = Field(..., description="学生ID", min_length=1)
    format: str = Field("markdown", description="导出格式（markdown/html/json）")

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息", min_length=1)

class CareerResponse(BaseModel):
    success: bool = Field(..., description="响应状态，true或false")
    data: str = Field(..., description="分析结果")
    message: str = Field(..., description="响应消息")

def check_llm() -> dict:
    try:
        test_prompt = "请回复'OK'"
        response = chat_model.invoke(test_prompt)
        if response and hasattr(response, 'content'):
            return {"status": "ok", "message": "LLM连接正常"}
        return {"status": "error", "message": "LLM响应异常"}
    except Exception as e:
        logger.error(f"[健康检查] LLM连接失败: {e}")
        return {"status": "error", "message": f"LLM连接失败: {str(e)}"}

@app.get("/health", summary="健康检查", description="检查API服务是否正常运行")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def health_check(request: Request, api_key: str = Depends(get_api_key)):
    llm_status = check_llm()
    
    overall_success = llm_status.get("status") == "ok"
    
    return {
        "success": overall_success,
        "message": "健康检查完成",
        "data": {
            "api": {"success": True, "message": "API服务运行正常"},
            "llm": llm_status
        }
    }

@app.get("/health/lite", summary="轻量级健康检查", description="仅检查API服务状态")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def health_check_lite(request: Request, api_key: str = Depends(get_api_key)):
    return {"success": True, "message": "API服务运行正常", "data": None}

@app.get("/status", summary="系统状态", description="查看系统运行状态")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def system_status(request: Request, api_key: str = Depends(get_api_key)):
    cache = get_career_cache()
    cache_stats = cache.get_stats()
    
    return {
        "success": True,
        "data": {
            "cache": cache_stats,
            "performance": {
                "result_cache": "enabled"
            }
        },
        "message": "系统状态正常"
    }

@app.post("/cache/clear", summary="清空缓存", description="清空所有缓存")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def clear_cache(request: Request, api_key: str = Depends(get_api_key)):
    cache = get_career_cache()
    cache.clear()
    return {"success": True, "message": "缓存已清空", "data": None}

@app.post(
    "/assessment",
    summary="职业测评",
    description="根据学生信息进行职业测评分析"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def assessment_endpoint(
    request: Request,
    req: CareerAssessmentRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到职业测评请求")
        
        result = career_assessment_from_info(
            student_info=req.student_info,
            student_name=req.student_name
        )
        
        logger.info(f"[API] 职业测评完成")
        
        return {
            "success": True,
            "data": result,
            "message": "职业测评完成"
        }
    except Exception as e:
        logger.error(f"[API] 职业测评失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"测评失败: {str(e)}"
        }

@app.post(
    "/course-recommendation",
    summary="课程推荐",
    description="根据学生信息和职业目标推荐学习课程"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def course_recommendation_endpoint(
    request: Request,
    req: CourseRecommendationRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到课程推荐请求")
        
        result = course_recommendation_from_info(
            student_info=req.student_info,
            career_goal=req.career_goal
        )
        
        logger.info(f"[API] 课程推荐完成")
        
        return {
            "success": True,
            "data": result,
            "message": "课程推荐完成"
        }
    except Exception as e:
        logger.error(f"[API] 课程推荐失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"推荐失败: {str(e)}"
        }

@app.post(
    "/job-guidance",
    summary="就业指导",
    description="根据学生信息和目标岗位提供就业指导"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def job_guidance_endpoint(
    request: Request,
    req: JobGuidanceRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到就业指导请求")
        
        result = job_guidance_from_info(
            student_info=req.student_info,
            target_position=req.target_position
        )
        
        logger.info(f"[API] 就业指导完成")
        
        return {
            "success": True,
            "data": result,
            "message": "就业指导完成"
        }
    except Exception as e:
        logger.error(f"[API] 就业指导失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"指导失败: {str(e)}"
        }

@app.get("/jobs", summary="获取岗位列表", description="支持按关键词、行业、城市、薪资、阶段筛选")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def get_all_jobs(
    request: Request,
    keyword: str = "",
    industry: str = "",
    city: str = "",
    salary_range: str = "",
    stage: str = "",
    api_key: str = Depends(get_api_key)
):
    try:
        # 如果有筛选参数，使用搜索
        if keyword or industry or city or salary_range or stage:
            search_query = keyword
            if industry:
                search_query += f" {industry}"
            if city:
                search_query += f" {city}"
            if salary_range:
                search_query += f" {salary_range}"
            if stage:
                search_query += f" {stage}"
            
            results = search_jobs(search_query if search_query else "岗位", top_k=50)
        else:
            # 否则获取所有岗位
            results = search_jobs("岗位", top_k=50)
        
        jobs = []
        for doc in results:
            metadata = doc.get("metadata", {})
            job_data = {
                "job_name": metadata.get("job_name", ""),
                "job_code": metadata.get("job_code", ""),
                "company_name": metadata.get("company_name", ""),
                "industry": metadata.get("industry", ""),
                "salary_range": metadata.get("salary_range", ""),
                "address": metadata.get("address", ""),
                "description": doc.get("content", ""),
                "similarity": 1 - doc.get("distance", 0) if doc.get("distance") else None
            }
            
            # 进一步过滤结果
            if industry and industry.lower() not in job_data["industry"].lower():
                continue
            if city and city.lower() not in job_data["address"].lower():
                continue
            if salary_range and salary_range.lower() not in job_data["salary_range"].lower():
                continue
            
            jobs.append(job_data)
        
        return {
            "success": True,
            "data": jobs,
            "message": f"获取岗位列表成功，共 {len(jobs)} 个岗位"
        }
    except Exception as e:
        logger.error(f"[API] 获取岗位列表失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }

@app.get("/jobs/search", summary="搜索岗位", description="根据关键词搜索岗位（RAG检索）")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def search_jobs_endpoint(request: Request, keyword: str, top_k: int = 10, api_key: str = Depends(get_api_key)):
    try:
        logger.info(f"[API] 搜索岗位: {keyword}")
        results = search_jobs(keyword, top_k=top_k)
        
        jobs = []
        for doc in results:
            metadata = doc.get("metadata", {})
            jobs.append({
                "job_name": metadata.get("job_name", ""),
                "job_code": metadata.get("job_code", ""),
                "company_name": metadata.get("company_name", ""),
                "industry": metadata.get("industry", ""),
                "salary_range": metadata.get("salary_range", ""),
                "address": metadata.get("address", ""),
                "description": doc.get("content", ""),
                "similarity": 1 - doc.get("distance", 0)
            })
        
        logger.info(f"[API] 搜索完成，找到 {len(jobs)} 个岗位")
        
        return {
            "success": True,
            "data": jobs,
            "message": f"搜索完成，找到 {len(jobs)} 个相关岗位"
        }
    except Exception as e:
        logger.error(f"[API] 搜索岗位失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"搜索失败: {str(e)}"
        }

@app.get("/jobs/{job_identifier}", summary="获取岗位详情", description="根据岗位ID获取详细信息")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def get_job(request: Request, job_identifier: str, api_key: str = Depends(get_api_key)):
    try:
        results = search_jobs(job_identifier, top_k=1)
        
        if not results:
            return {
                "success": False,
                "data": None,
                "message": "未找到该岗位"
            }
        
        doc = results[0]
        metadata = doc.get("metadata", {})
        
        job = {
            "job_name": metadata.get("job_name", ""),
            "job_code": metadata.get("job_code", ""),
            "company_name": metadata.get("company_name", ""),
            "industry": metadata.get("industry", ""),
            "salary_range": metadata.get("salary_range", ""),
            "address": metadata.get("address", ""),
            "description": doc.get("content", "")
        }
        
        return {
            "success": True,
            "data": job,
            "message": "获取岗位详情成功"
        }
    except Exception as e:
        logger.error(f"[API] 获取岗位详情失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }

@app.get("/jobs/{job_identifier}/relations", summary="获取岗位关联信息", description="获取岗位的相似岗位推荐")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def get_job_relations(request: Request, job_identifier: str, api_key: str = Depends(get_api_key)):
    try:
        results = search_jobs(job_identifier, top_k=5)
        
        if not results:
            return {
                "success": False,
                "data": None,
                "message": "未找到该岗位"
            }
        
        main_doc = results[0]
        main_metadata = main_doc.get("metadata", {})
        
        main_job = {
            "job_name": main_metadata.get("job_name", ""),
            "job_code": main_metadata.get("job_code", ""),
            "company_name": main_metadata.get("company_name", ""),
            "salary_range": main_metadata.get("salary_range", "")
        }
        
        related_jobs = []
        for doc in results[1:]:
            metadata = doc.get("metadata", {})
            related_jobs.append({
                "job_name": metadata.get("job_name", ""),
                "company_name": metadata.get("company_name", ""),
                "salary_range": metadata.get("salary_range", ""),
                "similarity": 1 - doc.get("distance", 0) if doc.get("distance") else None
            })
        
        return {
            "success": True,
            "data": {
                "job": main_job,
                "related_jobs": related_jobs
            },
            "message": "获取岗位关联信息成功"
        }
    except Exception as e:
        logger.error(f"[API] 获取岗位关联信息失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }

@app.post(
    "/parse-resume",
    summary="解析简历",
    description="解析简历生成学生就业能力画像"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def parse_resume_endpoint(
    request: Request,
    req: ParseResumeRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到简历解析请求")
        
        result = parse_resume_from_info(
            resume_content=req.resume_content,
            student_id=req.student_id
        )
        
        logger.info(f"[API] 简历解析完成")
        
        return {
            "success": True,
            "data": json.loads(result) if result.startswith("{") else result,
            "message": "简历解析完成"
        }
    except Exception as e:
        logger.error(f"[API] 简历解析失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"解析失败: {str(e)}"
        }

@app.get("/students/{student_id}/profile", summary="获取学生能力画像", description="获取学生就业能力画像")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def get_student_profile(request: Request, student_id: str, api_key: str = Depends(get_api_key)):
    try:
        profile = student_profile_manager.load_student_profile(student_id)
        if not profile:
            return {
                "success": False,
                "data": None,
                "message": "未找到该学生的能力画像"
            }
        
        return {
            "success": True,
            "data": profile,
            "message": "获取学生能力画像成功"
        }
    except Exception as e:
        logger.error(f"[API] 获取学生能力画像失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }

@app.post(
    "/job-matching",
    summary="人岗匹配分析",
    description="进行人岗匹配度分析"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def job_matching_endpoint(
    request: Request,
    req: JobMatchingRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到人岗匹配请求")
        
        result = job_matching_analysis_from_info(
            student_id=req.student_id,
            job_name=req.job_name,
            job_code=req.job_code
        )
        
        logger.info(f"[API] 人岗匹配完成")
        
        return {
            "success": True,
            "data": json.loads(result) if result.startswith("{") else result,
            "message": "人岗匹配完成"
        }
    except Exception as e:
        logger.error(f"[API] 人岗匹配失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"匹配失败: {str(e)}"
        }

@app.post(
    "/career-report",
    summary="生成职业发展报告",
    description="生成完整的职业发展报告"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def career_report_endpoint(
    request: Request,
    req: CareerReportRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到职业发展报告请求")
        
        result = generate_career_report_from_info(
            student_id=req.student_id,
            student_info=req.student_info,
            job_name=req.job_name,
            job_code=req.job_code
        )
        
        logger.info(f"[API] 职业发展报告生成完成")
        
        return {
            "success": True,
            "data": json.loads(result) if result.startswith("{") else result,
            "message": "职业发展报告生成完成"
        }
    except Exception as e:
        logger.error(f"[API] 职业发展报告生成失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"生成失败: {str(e)}"
        }

@app.post(
    "/export-report",
    summary="导出职业发展报告",
    description="导出职业发展报告为指定格式"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def export_report_endpoint(
    request: Request,
    req: ExportReportRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到导出报告请求")
        
        result = export_career_report_from_info(
            student_id=req.student_id,
            format=req.format
        )
        
        logger.info(f"[API] 报告导出完成")
        
        if req.format == "html":
            return StreamingResponse(
                iter([result]),
                media_type="text/html; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=career_report_{req.student_id}.html"}
            )
        elif req.format == "markdown":
            return StreamingResponse(
                iter([result]),
                media_type="text/markdown; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=career_report_{req.student_id}.md"}
            )
        else:
            return {
                "success": True,
                "data": json.loads(result) if result.startswith("{") else result,
                "message": "报告导出完成"
            }
    except Exception as e:
        logger.error(f"[API] 报告导出失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"导出失败: {str(e)}"
        }

@app.post(
    "/chat",
    summary="对话交互",
    description="与职业规划智能体进行自然语言对话"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def chat_endpoint(
    request: Request,
    req: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到对话请求")
        
        result = career_agent.execute(req.message)
        
        logger.info(f"[API] 对话完成")
        
        return {
            "success": True,
            "data": result,
            "message": "对话完成"
        }
    except Exception as e:
        logger.error(f"[API] 对话失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"对话失败: {str(e)}"
        }

@app.post(
    "/chat/stream",
    summary="对话交互（流式）",
    description="与职业规划智能体进行自然语言对话（流式输出）"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def chat_stream_endpoint(
    request: Request,
    req: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到流式对话请求")
        
        async def generate():
            for chunk in career_agent.execute_stream(req.message):
                yield chunk
        
        logger.info(f"[API] 流式对话完成")
        
        return StreamingResponse(
            generate(),
            media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"[API] 流式对话失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"对话失败: {str(e)}"
        )

@app.post(
    "/resume/parse",
    summary="解析简历",
    description="上传PDF/Word简历，解析为结构化数据"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def resume_parse_endpoint(
    request: Request,
    req: ParseResumeRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到简历解析请求")
        
        result = parse_resume_from_info(
            resume_content=req.resume_content,
            student_id=req.student_id
        )
        
        logger.info(f"[API] 简历解析完成")
        
        return {
            "success": True,
            "data": json.loads(result) if result.startswith("{") else result,
            "message": "简历解析完成"
        }
    except Exception as e:
        logger.error(f"[API] 简历解析失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"解析失败: {str(e)}"
        }

@app.post(
    "/report",
    summary="生成职业报告",
    description="生成完整的职业匹配报告，包含发展规划"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def report_endpoint(
    request: Request,
    req: CareerReportRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到职业报告请求")
        
        result = generate_career_report_from_info(
            student_id=req.student_id,
            student_info=req.student_info,
            job_name=req.job_name,
            job_code=req.job_code
        )
        
        logger.info(f"[API] 职业报告生成完成")
        
        return {
            "success": True,
            "data": json.loads(result) if result.startswith("{") else result,
            "message": "职业报告生成完成"
        }
    except Exception as e:
        logger.error(f"[API] 职业报告生成失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"生成失败: {str(e)}"
        }

@app.get(
    "/report/export",
    summary="导出报告",
    description="导出PDF/Word格式报告"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def report_export_endpoint(
    request: Request,
    student_id: str,
    format: str = "markdown",
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到导出报告请求")
        
        result = export_career_report_from_info(
            student_id=student_id,
            format=format
        )
        
        logger.info(f"[API] 报告导出完成")
        
        if format == "html":
            return StreamingResponse(
                iter([result]),
                media_type="text/html; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=career_report_{student_id}.html"}
            )
        elif format == "markdown":
            return StreamingResponse(
                iter([result]),
                media_type="text/markdown; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=career_report_{student_id}.md"}
            )
        else:
            return {
                "success": True,
                "data": json.loads(result) if result.startswith("{") else result,
                "message": "报告导出完成"
            }
    except Exception as e:
        logger.error(f"[API] 报告导出失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"导出失败: {str(e)}"
        }

@app.post(
    "/student/ability",
    summary="学生能力分析",
    description="分析学生综合能力，返回雷达图数据"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def student_ability_endpoint(
    request: Request,
    req: CareerReportRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到学生能力分析请求")
        
        result = career_assessment_from_info(
            student_info=req.student_info,
            student_name=req.student_id
        )
        
        logger.info(f"[API] 学生能力分析完成")
        
        return {
            "success": True,
            "data": result,
            "message": "学生能力分析完成"
        }
    except Exception as e:
        logger.error(f"[API] 学生能力分析失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"分析失败: {str(e)}"
        }

@app.post(
    "/report/polish",
    summary="润色报告",
    description="AI润色报告文案"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def report_polish_endpoint(
    request: Request,
    req: dict,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到润色报告请求")
        
        result = career_agent.execute(f"请帮我润色以下职业报告内容，使其更加专业、专业、易读：\n\n{json.dumps(req)}")
        
        logger.info(f"[API] 报告润色完成")
        
        return {
            "success": True,
            "data": result,
            "message": "报告润色完成"
        }
    except Exception as e:
        logger.error(f"[API] 报告润色失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"润色失败: {str(e)}"
        }

@app.get(
    "/user/info",
    summary="获取用户信息",
    description="获取当前登录用户基本信息"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def user_info_endpoint(
    request: Request,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到获取用户信息请求")
        
        return {
            "success": True,
            "data": {
                "user_id": "demo_user",
                "username": "演示用户",
                "email": "demo@example.com"
            },
            "message": "获取用户信息成功"
        }
    except Exception as e:
        logger.error(f"[API] 获取用户信息失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }

@app.get(
    "/history/reports",
    summary="获取历史报告",
    description="获取用户历史生成的职业报告"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def history_reports_endpoint(
    request: Request,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到获取历史报告请求")
        
        all_reports = report_manager.load_all_reports()
        
        reports_list = []
        for report_id, report_data in all_reports.items():
            reports_list.append({
                "id": report_id,
                "student_id": report_data.get("student_id", ""),
                "created_at": report_data.get("created_at", ""),
                "job_name": report_data.get("job_name", "")
            })
        
        return {
            "success": True,
            "data": reports_list,
            "message": "获取历史报告成功"
        }
    except Exception as e:
        logger.error(f"[API] 获取历史报告失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }

@app.get(
    "/community/articles",
    summary="获取官方文章",
    description="获取就业指导文章"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def community_articles_endpoint(
    request: Request,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到获取官方文章请求")
        
        articles = [
            {
                "id": 1,
                "title": "2024年计算机行业就业趋势分析",
                "summary": "详细分析2024年计算机行业的就业趋势、热门岗位、薪资水平等",
                "content": "本文将详细介绍2024年计算机行业的就业趋势...",
                "created_at": "2024-01-01"
            },
            {
                "id": 2,
                "title": "如何写出一份优秀的简历",
                "summary": "简历撰写技巧、常见问题、优秀案例",
                "content": "简历是求职的第一步...",
                "created_at": "2024-01-05"
            },
            {
                "id": 3,
                "title": "面试常见问题及回答技巧",
                "summary": "常见面试问题、回答技巧、注意事项",
                "content": "面试是求职的关键环节...",
                "created_at": "2024-01-10"
            }
        ]
        
        return {
            "success": True,
            "data": articles,
            "message": "获取官方文章成功"
        }
    except Exception as e:
        logger.error(f"[API] 获取官方文章失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"获取失败: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    host = server_conf.get("host", "0.0.0.0")
    port = server_conf.get("port", 8000)
    print("=" * 60)
    print("大学生职业规划智能体 API服务启动中...")
    print("=" * 60)
    print(f"服务地址: http://{host}:{port}")
    print("API文档地址:")
    print(f"  - Swagger UI: http://localhost:{port}/docs")
    print(f"  - ReDoc: http://localhost:{port}/redoc")
    print("=" * 60)
    uvicorn.run(app, host=host, port=port)
