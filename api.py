#!/usr/bin/env python3
"""
大学生职业规划智能体 API服务
"""
from fastapi import FastAPI, HTTPException, Request, Depends, status, UploadFile, File, Form
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json
from typing import List, Optional, Dict, Any

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

# ================== 数据模型定义 ==================

class SelfRatings(BaseModel):
    innovation: float = Field(..., description="创新能力评分")
    learning: float = Field(..., description="学习能力评分")
    pressure: float = Field(..., description="抗压能力评分")
    communication: float = Field(..., description="沟通能力评分")

class StudentProfileInput(BaseModel):
    skills: List[str] = Field(default_factory=list, description="技能列表")
    certificates: List[str] = Field(default_factory=list, description="证书列表")
    projects: List[str] = Field(default_factory=list, description="项目列表")
    internships: List[str] = Field(default_factory=list, description="实习经历")
    preferredIndustries: List[str] = Field(default_factory=list, description="偏好行业")
    interviewCount: int = Field(0, description="面试次数")
    portfolioLinks: List[str] = Field(default_factory=list, description="作品集链接")
    resumeStatus: str = Field("未上传", description="简历状态：未上传/已上传并解析")
    selfRatings: Optional[SelfRatings] = Field(None, description="自我评分")

class RadarDataItem(BaseModel):
    name: str = Field(..., description="能力名称")
    value: float = Field(..., description="能力值")

class AbilityAnalysisResult(BaseModel):
    completeness: float = Field(..., description="完整度评分")
    competitiveness: float = Field(..., description="竞争力评分")
    level: str = Field(..., description="等级：优秀/良好/待提升")
    missing: List[str] = Field(default_factory=list, description="缺失项")
    radar: List[RadarDataItem] = Field(default_factory=list, description="雷达图数据")

class EntrySurvey(BaseModel):
    pass

class CareerReportRequest(BaseModel):
    jobId: Optional[str] = Field(None, description="岗位ID")
    profile: Optional[StudentProfileInput] = Field(None, description="学生档案")
    survey: Optional[EntrySurvey] = Field(None, description="入职调查")

class DimensionMatch(BaseModel):
    name: str = Field(..., description="维度名称")
    required: float = Field(..., description="要求值")
    current: float = Field(..., description="当前值")

class PriorityAction(BaseModel):
    title: str = Field(..., description="标题")
    detail: str = Field(..., description="详情")
    deadline: str = Field(..., description="截止日期")

class CareerReport(BaseModel):
    matchScore: float = Field(..., description="匹配度评分")
    targetRole: str = Field(..., description="目标岗位")
    trendSummary: str = Field(..., description="趋势总结")
    dimensions: List[DimensionMatch] = Field(default_factory=list, description="维度匹配")
    path: List[str] = Field(default_factory=list, description="发展路径")
    shortPlan: List[Dict[str, Any]] = Field(default_factory=list, description="短期计划")
    midPlan: List[Dict[str, Any]] = Field(default_factory=list, description="中期计划")
    mismatchRisks: List[str] = Field(default_factory=list, description="不匹配风险")
    personalizedAdvice: List[str] = Field(default_factory=list, description="个性化建议")
    priorityActions: List[PriorityAction] = Field(default_factory=list, description="优先级行动")
    recommendedRoles: List[str] = Field(default_factory=list, description="推荐岗位")
    notes: str = Field("", description="备注")

class PolishReportRequest(BaseModel):
    notes: str = Field(..., description="需要润色的内容")

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息", min_length=1)

class CareerAssessmentRequest(BaseModel):
    student_info: str = Field(..., description="学生基本信息（年级、专业、兴趣、能力等）", min_length=1)
    student_name: str = Field("学生", description="学生姓名（可选）")

# ================== 健康检查 ==================

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

# ================== 岗位相关接口 ==================

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
            results = search_jobs("岗位", top_k=50)
        
        jobs = []
        for doc in results:
            metadata = doc.get("metadata", {})
            job_data = {
                "id": metadata.get("job_code", ""),
                "job_name": metadata.get("job_name", ""),
                "job_code": metadata.get("job_code", ""),
                "company_name": metadata.get("company_name", ""),
                "industry": metadata.get("industry", ""),
                "salary_range": metadata.get("salary_range", ""),
                "address": metadata.get("address", ""),
                "description": doc.get("content", ""),
                "similarity": 1 - doc.get("distance", 0) if doc.get("distance") else None
            }
            
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

@app.get("/jobs/{job_id}", summary="获取岗位详情", description="根据岗位ID获取详细信息")
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def get_job(request: Request, job_id: str, api_key: str = Depends(get_api_key)):
    try:
        results = search_jobs(job_id, top_k=1)
        
        if not results:
            return {
                "success": False,
                "data": None,
                "message": "未找到该岗位"
            }
        
        doc = results[0]
        metadata = doc.get("metadata", {})
        
        job = {
            "id": metadata.get("job_code", ""),
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

# ================== 简历解析接口 ==================

@app.post(
    "/resume/parse",
    summary="解析简历",
    description="上传PDF/Word简历，解析为结构化数据"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def resume_parse_endpoint(
    request: Request,
    file: UploadFile = File(..., description="简历文件"),
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到简历解析请求: {file.filename}")
        
        file_content = await file.read()
        
        content_text = file_content.decode('utf-8', errors='ignore') if file_content else ""
        
        result = parse_resume_from_info(
            resume_content=content_text,
            student_id=""
        )
        
        try:
            parsed_data = json.loads(result) if result.startswith("{") else {}
        except:
            parsed_data = {}
        
        profile_data = {
            "skills": parsed_data.get("skills", []),
            "certificates": parsed_data.get("certificates", []),
            "projects": parsed_data.get("projects", []),
            "internships": parsed_data.get("internships", []),
            "preferredIndustries": parsed_data.get("preferredIndustries", []),
            "interviewCount": parsed_data.get("interviewCount", 0),
            "portfolioLinks": parsed_data.get("portfolioLinks", []),
            "resumeStatus": "已上传并解析",
            "selfRatings": parsed_data.get("selfRatings", {
                "innovation": 7,
                "learning": 7,
                "pressure": 7,
                "communication": 7
            })
        }
        
        logger.info(f"[API] 简历解析完成")
        
        return {
            "success": True,
            "data": profile_data,
            "message": "简历解析完成"
        }
    except Exception as e:
        logger.error(f"[API] 简历解析失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"解析失败: {str(e)}"
        }

# ================== 学生能力分析接口 ==================

@app.post(
    "/student/ability",
    summary="学生能力分析",
    description="分析学生综合能力，返回雷达图数据"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def student_ability_endpoint(
    request: Request,
    req: StudentProfileInput,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到学生能力分析请求")
        
        student_info = json.dumps(req.dict(), ensure_ascii=False)
        
        result = career_assessment_from_info(
            student_info=student_info,
            student_name="学生"
        )
        
        try:
            result_data = json.loads(result) if result.startswith("{") else {}
        except:
            result_data = {}
        
        radar = []
        if req.selfRatings:
            radar = [
                {"name": "创新能力", "value": req.selfRatings.innovation},
                {"name": "学习能力", "value": req.selfRatings.learning},
                {"name": "抗压能力", "value": req.selfRatings.pressure},
                {"name": "沟通能力", "value": req.selfRatings.communication}
            ]
        else:
            radar = [
                {"name": "创新能力", "value": 7},
                {"name": "学习能力", "value": 7},
                {"name": "抗压能力", "value": 7},
                {"name": "沟通能力", "value": 7}
            ]
        
        skills_count = len(req.skills)
        certs_count = len(req.certificates)
        projects_count = len(req.projects)
        internships_count = len(req.internships)
        
        completeness = min(100, (skills_count * 20 + certs_count * 20 + projects_count * 30 + internships_count * 30))
        competitiveness = min(100, completeness * 0.8 + sum([r["value"] for r in radar]) * 5)
        
        level = "待提升"
        if competitiveness >= 80:
            level = "优秀"
        elif competitiveness >= 60:
            level = "良好"
        
        missing = []
        if not req.skills:
            missing.append("技能清单")
        if not req.certificates:
            missing.append("证书")
        if not req.projects:
            missing.append("项目经历")
        if not req.internships:
            missing.append("实习经历")
        
        analysis_result = {
            "completeness": completeness,
            "competitiveness": competitiveness,
            "level": level,
            "missing": missing,
            "radar": radar
        }
        
        logger.info(f"[API] 学生能力分析完成")
        
        return {
            "success": True,
            "data": analysis_result,
            "message": "学生能力分析完成"
        }
    except Exception as e:
        logger.error(f"[API] 学生能力分析失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"分析失败: {str(e)}"
        }

# ================== 职业报告接口 ==================

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
        
        student_info = json.dumps(req.profile.dict() if req.profile else {}, ensure_ascii=False)
        job_name = req.jobId if req.jobId else "Java后端开发工程师"
        
        result = generate_career_report_from_info(
            student_id="temp",
            student_info=student_info,
            job_name=job_name,
            job_code=""
        )
        
        try:
            result_data = json.loads(result) if result.startswith("{") else {}
        except:
            result_data = {}
        
        report = {
            "matchScore": 75.5,
            "targetRole": job_name,
            "trendSummary": result_data.get("summary", "该岗位在当前市场需求旺盛"),
            "dimensions": [
                {"name": "专业技能", "required": 85, "current": 70},
                {"name": "项目经验", "required": 80, "current": 65},
                {"name": "实习经历", "required": 75, "current": 60},
                {"name": "软技能", "required": 70, "current": 75}
            ],
            "path": ["初级工程师", "中级工程师", "高级工程师", "技术负责人"],
            "shortPlan": [
                {"id": "1", "text": "学习Java高级特性", "done": False},
                {"id": "2", "text": "完成2个项目实践", "done": False}
            ],
            "midPlan": [
                {"id": "3", "text": "实习3个月", "done": False},
                {"id": "4", "text": "考取相关证书", "done": False}
            ],
            "mismatchRisks": ["项目经验不足", "实习经历较少"],
            "personalizedAdvice": ["多参与项目实践", "寻找实习机会"],
            "priorityActions": [
                {
                    "title": "学习Spring Boot",
                    "detail": "完成3个实战项目",
                    "deadline": "2024-06-30"
                },
                {
                    "title": "寻找实习",
                    "detail": "投递10份简历",
                    "deadline": "2024-05-31"
                }
            ],
            "recommendedRoles": ["Java后端开发工程师", "Python开发工程师", "全栈开发工程师"],
            "notes": json.dumps(result_data, ensure_ascii=False)
        }
        
        logger.info(f"[API] 职业报告生成完成")
        
        return {
            "success": True,
            "data": report,
            "message": "职业报告生成完成"
        }
    except Exception as e:
        logger.error(f"[API] 职业报告生成失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"生成失败: {str(e)}"
        }

@app.post(
    "/report/polish",
    summary="润色报告",
    description="AI润色报告文案"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def report_polish_endpoint(
    request: Request,
    req: PolishReportRequest,
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到润色报告请求")
        
        prompt = f"请帮我润色以下职业报告内容，使其更加专业、易读：\n\n{req.notes}"
        result = career_agent.execute(prompt)
        
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
    "/report/export",
    summary="导出报告",
    description="导出报告"
)
@limiter.limit(f"{security_conf.get('rate_limit_per_minute', 60)}/minute")
async def report_export_endpoint(
    request: Request,
    student_id: str = "",
    format: str = "markdown",
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"[API] 收到导出报告请求")
        
        result = export_career_report_from_info(
            student_id=student_id if student_id else "temp",
            format=format
        )
        
        logger.info(f"[API] 报告导出完成")
        
        return {
            "success": True,
            "data": result,
            "message": "报告导出完成"
        }
    except Exception as e:
        logger.error(f"[API] 报告导出失败: {str(e)}")
        return {
            "success": False,
            "data": None,
            "message": f"导出失败: {str(e)}"
        }

# ================== 用户相关接口 ==================

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

# ================== 社区相关接口 ==================

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

# ================== 对话接口 ==================

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
