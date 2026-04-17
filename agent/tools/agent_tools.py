import re
import os
import json
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv
import requests

from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from utils.cache_manager import get_career_cache
from utils.retry_utils import with_retry, llm_retry_config
from model.factory import chat_model
from data.data_manager import (
    student_profile_manager,
    report_manager
)
from data.excel_importer import search_jobs
from data.vector_db_manager import vector_db_manager

load_dotenv()


@with_retry(config=llm_retry_config)
def _career_assessment(student_info: str, student_name: str = "学生") -> str:
    prompt_path = get_abs_path("prompts/career_assessment_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_content = f.read()
    
    prompt_template = PromptTemplate.from_template(prompt_content)
    chain = prompt_template | chat_model | StrOutputParser()
    
    result = chain.invoke({"student_info": student_info, "student_name": student_name})
    
    return result


def career_assessment_from_info(student_info: str, student_name: Optional[str] = None) -> str:
    cache = get_career_cache()
    cache_key = f"assessment:{hash(student_info)}"
    
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"[缓存] 职业测评命中缓存")
        return cached_result
    
    name = student_name if student_name else "学生"
    result = _career_assessment(student_info, name)
    
    cache.set(cache_key, result)
    logger.info(f"[缓存] 职业测评已缓存")
    
    return result


@tool(description="进行职业测评分析，需要提供学生的基本信息（年级、专业、兴趣、能力等）")
def career_assessment(student_info: str, student_name: str = "学生") -> str:
    return career_assessment_from_info(student_info, student_name)


@with_retry(config=llm_retry_config)
def _course_recommendation(student_info: str, career_goal: str) -> str:
    prompt_path = get_abs_path("prompts/course_recommendation_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_content = f.read()
    
    prompt_template = PromptTemplate.from_template(prompt_content)
    chain = prompt_template | chat_model | StrOutputParser()
    
    result = chain.invoke({"student_info": student_info, "career_goal": career_goal})
    
    return result


def course_recommendation_from_info(student_info: str, career_goal: str) -> str:
    cache = get_career_cache()
    cache_key = f"course:{hash(student_info + career_goal)}"
    
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"[缓存] 课程推荐命中缓存")
        return cached_result
    
    result = _course_recommendation(student_info, career_goal)
    
    cache.set(cache_key, result)
    logger.info(f"[缓存] 课程推荐已缓存")
    
    return result


@tool(description="推荐学习课程，需要提供学生信息和职业目标")
def course_recommendation(student_info: str, career_goal: str) -> str:
    return course_recommendation_from_info(student_info, career_goal)


@with_retry(config=llm_retry_config)
def _job_guidance(student_info: str, target_position: str) -> str:
    prompt_path = get_abs_path("prompts/job_guidance_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_content = f.read()
    
    prompt_template = PromptTemplate.from_template(prompt_content)
    chain = prompt_template | chat_model | StrOutputParser()
    
    result = chain.invoke({"student_info": student_info, "target_position": target_position})
    
    return result


def job_guidance_from_info(student_info: str, target_position: str) -> str:
    cache = get_career_cache()
    cache_key = f"job:{hash(student_info + target_position)}"
    
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"[缓存] 就业指导命中缓存")
        return cached_result
    
    result = _job_guidance(student_info, target_position)
    
    cache.set(cache_key, result)
    logger.info(f"[缓存] 就业指导已缓存")
    
    return result


@tool(description="提供就业指导，需要提供学生信息和目标行业/职位")
def job_guidance(student_info: str, target_position: str) -> str:
    return job_guidance_from_info(student_info, target_position)


@tool(description="获取所有岗位列表（从向量库）")
def get_all_job_portraits() -> str:
    """获取所有岗位列表（通过检索所有文档）"""
    try:
        all_ids = vector_db_manager.get_all_ids()
        if not all_ids:
            return "暂无岗位数据，请先导入 Excel 文件"
        
        result = f"共找到 {len(all_ids)} 个岗位:\n\n"
        
        results = search_jobs("岗位", top_k=min(20, len(all_ids)))
        for i, doc in enumerate(results, 1):
            metadata = doc.get("metadata", {})
            result += f"{i}. {metadata.get('job_name', '未知')}"
            if metadata.get('company_name'):
                result += f" - {metadata.get('company_name')}"
            if metadata.get('salary_range'):
                result += f" ({metadata.get('salary_range')})"
            result += "\n"
        
        if len(all_ids) > 20:
            result += f"\n... 还有 {len(all_ids) - 20} 个岗位，请使用 search_relevant_jobs 进行具体检索"
        
        return result
        
    except Exception as e:
        logger.error(f"获取岗位列表失败: {e}")
        return f"获取岗位列表失败: {str(e)}"


@tool(description="获取指定岗位画像，需要提供职位名称或职位编码")
def get_job_portrait(job_name: str = "", job_code: str = "") -> str:
    """获取指定岗位画像（使用 RAG 检索）"""
    if not job_name and not job_code:
        return "请提供职位名称或职位编码"
    
    query = job_name if job_name else job_code
    results = search_jobs(query, top_k=1)
    
    if not results:
        return f"未找到与 '{query}' 相关的岗位画像"
    
    doc = results[0]
    metadata = doc.get("metadata", {})
    
    result = {
        "job_name": metadata.get("job_name", ""),
        "job_code": metadata.get("job_code", ""),
        "category": metadata.get("category", ""),
        "company_name": metadata.get("company_name", ""),
        "industry": metadata.get("industry", ""),
        "salary_range": metadata.get("salary_range", ""),
        "address": metadata.get("address", ""),
        "detail": doc.get("content", "")
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool(description="获取岗位关联信息，需要提供职位名称")
def get_job_relation_graph(job_name: str = "", job_code: str = "") -> str:
    """获取岗位关联信息（使用 RAG 检索相似岗位）"""
    if not job_name and not job_code:
        return "请提供职位名称或职位编码"
    
    query = job_name if job_name else job_code
    results = search_jobs(query, top_k=5)
    
    if not results:
        return f"未找到与 '{query}' 相关的岗位"
    
    main_job = results[0]
    main_metadata = main_job.get("metadata", {})
    
    result = f"主岗位: {main_metadata.get('job_name', '未知')}\n"
    result += f"公司: {main_metadata.get('company_name', '未知')}\n"
    result += f"薪资: {main_metadata.get('salary_range', '未知')}\n"
    
    if len(results) > 1:
        result += "\n相似/相关岗位推荐:\n"
        for i, doc in enumerate(results[1:], 1):
            metadata = doc.get("metadata", {})
            result += f"\n{i}. {metadata.get('job_name', '未知')}"
            if metadata.get('company_name'):
                result += f" - {metadata.get('company_name')}"
            if metadata.get('salary_range'):
                result += f" ({metadata.get('salary_range')})"
            if doc.get('distance'):
                similarity = 1 - doc['distance']
                result += f" [相似度: {similarity:.0%}]"
    
    return result


@with_retry(config=llm_retry_config)
def _parse_resume_to_profile(resume_content: str) -> Dict:
    prompt = f"""
请根据以下简历内容，提取并生成学生就业能力画像。

简历内容：
{resume_content}

请以JSON格式返回，包含以下字段：
- professional_skills: [专业技能列表]
- certificates: [证书列表]
- innovation_ability: 创新能力评分(1-10)
- learning_ability: 学习能力评分(1-10)
- stress_resistance: 抗压能力评分(1-10)
- communication_ability: 沟通能力评分(1-10)
- internship_ability: 实习能力评分(1-10)
- internship_experience: [实习经历列表]
- project_experience: [项目经历列表]
- completeness_score: 画像完整度评分(0-100)
- competitiveness_score: 竞争力评分(0-100)

只返回JSON，不要其他文字。
"""
    result = chat_model.invoke(prompt)
    try:
        content = result.content if hasattr(result, 'content') else str(result)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())
        return {}
    except Exception as e:
        logger.error(f"解析简历失败: {e}")
        return {}


def parse_resume_from_info(resume_content: str, student_id: str = "") -> str:
    profile = _parse_resume_to_profile(resume_content)
    
    if student_id:
        student_profile_manager.save_student_profile(student_id, profile)
    
    return json.dumps(profile, ensure_ascii=False, indent=2)


@tool(description="解析简历生成学生就业能力画像，需要提供简历内容")
def parse_resume(resume_content: str, student_id: str = "") -> str:
    return parse_resume_from_info(resume_content, student_id)


@with_retry(config=llm_retry_config)
def _job_matching(student_profile: Dict, job_portrait: Dict) -> Dict:
    prompt = f"""
请根据学生能力画像和岗位画像，进行人岗匹配度分析。

学生能力画像：
{json.dumps(student_profile, ensure_ascii=False, indent=2)}

岗位画像：
{json.dumps(job_portrait, ensure_ascii=False, indent=2)}

请以JSON格式返回匹配结果，包含：
- total_score: 整体匹配度(0-100)
- skill_matching: [{{name: 技能名称, score: 匹配度(0-100), gap: 差距描述}}]
- quality_matching: [{{name: 素质名称, score: 匹配度(0-100), gap: 差距描述}}]
- summary: 匹配总结

只返回JSON，不要其他文字。
"""
    result = chat_model.invoke(prompt)
    try:
        content = result.content if hasattr(result, 'content') else str(result)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())
        return {}
    except Exception as e:
        logger.error(f"人岗匹配分析失败: {e}")
        return {}


def job_matching_analysis_from_info(student_id: str, job_name: str = "", job_code: str = "") -> str:
    student_profile = student_profile_manager.load_student_profile(student_id)
    if not student_profile:
        return f"未找到学生 {student_id} 的能力画像，请先上传简历"
    
    if not job_name and not job_code:
        return "请提供目标岗位名称或编码"
    
    query = job_name if job_name else job_code
    results = search_jobs(query, top_k=1)
    
    if not results:
        return f"未找到与 '{query}' 相关的岗位画像"
    
    doc = results[0]
    metadata = doc.get("metadata", {})
    
    job = {
        "job_name": metadata.get("job_name", ""),
        "job_code": metadata.get("job_code", ""),
        "category": metadata.get("category", ""),
        "company_name": metadata.get("company_name", ""),
        "industry": metadata.get("industry", ""),
        "salary_range": metadata.get("salary_range", ""),
        "address": metadata.get("address", ""),
        "professional_skills": [],
        "certificates": [],
        "abilities": {
            "innovation": 7,
            "learning": 7,
            "stress": 7,
            "communication": 7,
            "internship": 7
        }
    }
    
    matching_result = _job_matching(student_profile, job)
    return json.dumps(matching_result, ensure_ascii=False, indent=2)


@tool(description="进行人岗匹配分析，需要提供学生ID和目标岗位名称/编码")
def job_matching_analysis(student_id: str, job_name: str = "", job_code: str = "") -> str:
    return job_matching_analysis_from_info(student_id, job_name, job_code)


@with_retry(config=llm_retry_config)
def _generate_career_report(student_info: str, student_profile: Dict, job_portrait: Dict, matching_result: Dict) -> Dict:
    prompt = f"""
请根据以下信息生成完整的大学生职业发展报告。

学生基本信息：
{student_info}

学生能力画像：
{json.dumps(student_profile, ensure_ascii=False, indent=2)}

目标岗位画像：
{json.dumps(job_portrait, ensure_ascii=False, indent=2)}

人岗匹配结果：
{json.dumps(matching_result, ensure_ascii=False, indent=2)}

请以JSON格式返回报告，包含：
- title: 报告标题
- created_time: 创建时间
- student_info: {{基本信息}}
- job_matching: {{匹配分析}}
- career_path: {{
    vertical_path: [垂直发展路径],
    job_change_options: [换岗选项],
    industry_trend: 行业趋势分析
  }}
- action_plan: {{
    short_term: [短期计划],
    mid_term: [中期计划],
    evaluation: 评估指标
  }}

只返回JSON，不要其他文字。
"""
    result = chat_model.invoke(prompt)
    try:
        content = result.content if hasattr(result, 'content') else str(result)
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())
        return {}
    except Exception as e:
        logger.error(f"生成职业发展报告失败: {e}")
        return {}


def generate_career_report_from_info(student_id: str, student_info: str, job_name: str = "", job_code: str = "") -> str:
    student_profile = student_profile_manager.load_student_profile(student_id)
    if not student_profile:
        return f"未找到学生 {student_id} 的能力画像，请先上传简历"
    
    if not job_name and not job_code:
        return "请提供目标岗位名称或编码"
    
    query = job_name if job_name else job_code
    results = search_jobs(query, top_k=1)
    
    if not results:
        return f"未找到与 '{query}' 相关的岗位画像"
    
    doc = results[0]
    metadata = doc.get("metadata", {})
    
    job = {
        "job_name": metadata.get("job_name", ""),
        "job_code": metadata.get("job_code", ""),
        "category": metadata.get("category", ""),
        "company_name": metadata.get("company_name", ""),
        "industry": metadata.get("industry", ""),
        "salary_range": metadata.get("salary_range", ""),
        "address": metadata.get("address", ""),
        "professional_skills": [],
        "certificates": [],
        "abilities": {
            "innovation": 7,
            "learning": 7,
            "stress": 7,
            "communication": 7,
            "internship": 7
        }
    }
    
    matching_result = _job_matching(student_profile, job)
    
    report = _generate_career_report(student_info, student_profile, job, matching_result)
    report["created_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_manager.save_report(student_id, report)
    
    return json.dumps(report, ensure_ascii=False, indent=2)


@tool(description="生成完整的职业发展报告，需要提供学生ID、学生信息、目标岗位")
def generate_career_report(student_id: str, student_info: str, job_name: str = "", job_code: str = "") -> str:
    return generate_career_report_from_info(student_id, student_info, job_name, job_code)


def export_career_report_from_info(student_id: str, format: str = "markdown") -> str:
    from data.data_manager import report_manager
    
    report_file = None
    data_dir = get_abs_path("data/reports")
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.startswith(student_id)]
        if files:
            report_file = os.path.join(data_dir, sorted(files)[-1])
    
    if not report_file:
        return "未找到该学生的报告"
    
    with open(report_file, "r", encoding="utf-8") as f:
        report = json.load(f)
    
    return report_manager.export_report(student_id, report, format)


@tool(description="导出职业发展报告，需要提供学生ID和导出格式（markdown/html/json）")
def export_career_report(student_id: str, format: str = "markdown") -> str:
    return export_career_report_from_info(student_id, format)


@tool(description="获取学生基本信息")
def get_student_profile(student_id: str) -> str:
    profile = student_profile_manager.load_student_profile(student_id)
    if profile:
        return json.dumps(profile, ensure_ascii=False, indent=2)
    return f"未找到学生 {student_id} 的能力画像"


@tool(description="从向量库检索相关岗位信息，需要提供查询关键词（如岗位名称、技能等）")
def search_relevant_jobs(query: str, top_k: int = 3) -> str:
    """
    从向量库检索相关岗位
    
    Args:
        query: 查询关键词
        top_k: 返回结果数量
        
    Returns:
        相关岗位信息
    """
    try:
        results = search_jobs(query, top_k)
        
        if not results:
            return f"未找到与 '{query}' 相关的岗位信息"
        
        result_str = f"找到 {len(results)} 个相关岗位:\n\n"
        
        for i, doc in enumerate(results, 1):
            metadata = doc.get("metadata", {})
            result_str += f"【岗位 {i}】\n"
            result_str += f"岗位名称: {metadata.get('job_name', '未知')}\n"
            result_str += f"公司名称: {metadata.get('company_name', '未知')}\n"
            result_str += f"所属行业: {metadata.get('industry', '未知')}\n"
            result_str += f"薪资范围: {metadata.get('salary_range', '未知')}\n"
            result_str += f"工作地址: {metadata.get('address', '未知')}\n"
            
            if doc.get("distance"):
                similarity = 1 - doc["distance"]
                result_str += f"匹配度: {similarity:.1%}\n"
            
            result_str += f"\n详细信息:\n{doc.get('content', '')}\n"
            result_str += "-" * 50 + "\n\n"
        
        logger.info(f"[RAG] 检索 '{query}' 返回 {len(results)} 个结果")
        return result_str
        
    except Exception as e:
        logger.error(f"[RAG] 检索失败: {e}")
        return f"检索岗位信息时出错: {str(e)}"
