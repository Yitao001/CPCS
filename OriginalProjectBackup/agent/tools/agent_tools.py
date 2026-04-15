import re
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import requests

from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from utils.cache_manager import get_persona_cache
from utils.retry_utils import with_retry, llm_retry_config
from model.factory import chat_model

load_dotenv()

PROXY_API_URL = os.getenv("PROXY_API_URL", "")
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "")

RELAY_MODE = os.getenv("RELAY_MODE", "false").lower() == "true"
RELAY_API_URL = os.getenv("RELAY_API_URL", "http://localhost:8002")
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "relay_secret_key_123")
RELAY_CLIENT_ID = os.getenv("RELAY_CLIENT_ID", "client_001")


def get_chat_history_from_relay(participant_id: str) -> dict:
    """
    通过中继服务获取对话历史
    
    Args:
        participant_id: 参与者ID（学生ID）
    
    Returns:
        包含 records 的字典
    """
    try:
        if not RELAY_API_URL:
            return {"status": "error", "error": "未配置中继服务地址 (RELAY_API_URL)"}
        
        headers = {
            "X-API-Key": RELAY_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "client_id": RELAY_CLIENT_ID,
            "action": "chat_history",
            "params": {
                "student_id": participant_id,
                "limit": 100
            }
        }
        
        logger.info(f"[中继调用] 请求对话历史，学生ID: {participant_id}, 客户端: {RELAY_CLIENT_ID}")
        
        response = requests.post(
            f"{RELAY_API_URL.rstrip('/')}/query",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") != "success":
            return {"status": "error", "error": result.get("error", "未知错误")}
        
        return {"status": "success", "records": result.get("data", [])}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[中继调用] 中继服务调用失败: {str(e)}")
        return {"status": "error", "error": f"中继服务调用失败: {str(e)}"}
    except Exception as e:
        logger.error(f"[中继调用] 获取对话历史失败: {str(e)}")
        return {"status": "error", "error": f"获取对话历史失败: {str(e)}"}


def get_chat_history_from_db(participant_id: str) -> str:
    """
    通过数据库代理服务获取指定参与者的对话历史
    
    Args:
        participant_id: 参与者ID（学生ID）
    
    Returns:
        对话历史文本
    """
    try:
        if RELAY_MODE:
            logger.info(f"[代理调用] 使用中继模式")
            result = get_chat_history_from_relay(participant_id)
            if result.get("status") != "success":
                return f"中继服务错误: {result.get('error', '未知错误')}"
            records = result.get("records", [])
        else:
            if not PROXY_API_URL:
                return "错误：未配置数据库代理服务地址 (PROXY_API_URL)"
            
            headers = {}
            if PROXY_API_KEY:
                headers["X-Proxy-API-Key"] = PROXY_API_KEY
            
            payload = {
                "student_id": participant_id,
                "limit": 100
            }
            
            logger.info(f"[代理调用] 请求对话历史，学生ID: {participant_id}")
            
            response = requests.post(
                f"{PROXY_API_URL.rstrip('/')}/chat-history",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") != "success":
                return f"代理服务错误: {result.get('message', '未知错误')}"
            
            records = result.get("data", [])
        
        if not records:
            return "未找到历史会谈信息"
        
        def parse_time(time_str):
            """解析时间字符串"""
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"]:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            return None
        
        records_with_time = []
        for record in records:
            time_str = record.get("created_time", "")
            dt = parse_time(time_str)
            if dt:
                records_with_time.append({
                    "time": dt,
                    "time_str": time_str,
                    "content": record.get("content", "")
                })
        
        if not records_with_time:
            chat_history = []
            for record in records:
                content = record.get("content", "")
                talk_time = record.get("created_time", "")
                chat_history.append(f"时间: {talk_time}\n内容: {content}")
            return "\n\n".join(chat_history)
        
        records_with_time.sort(key=lambda x: x["time"])
        
        chat_history = []
        prev_time = None
        
        for i, record in enumerate(records_with_time, 1):
            current_time = record["time"]
            time_str = record["time_str"]
            content = record["content"]
            
            time_info = f"[{i}] 时间: {time_str}"
            
            if prev_time:
                time_diff = current_time - prev_time
                hours = time_diff.total_seconds() / 3600
                days = hours / 24
                
                if days >= 1:
                    time_info += f" (距离上次间隔: {days:.1f}天)"
                elif hours >= 1:
                    time_info += f" (距离上次间隔: {hours:.1f}小时)"
                else:
                    minutes = time_diff.total_seconds() / 60
                    time_info += f" (距离上次间隔: {minutes:.0f}分钟)"
            
            chat_history.append(f"{time_info}\n内容: {content}")
            prev_time = current_time
        
        return "\n\n".join(chat_history)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[get_chat_history_from_db]代理服务调用失败: {str(e)}")
        return f"代理服务调用失败: {str(e)}"
    except Exception as e:
        logger.error(f"[get_chat_history_from_db]获取对话历史失败: {str(e)}")
        return f"获取对话历史失败: {str(e)}"


@with_retry(config=llm_retry_config)
def _generate_persona(chat_history: str, target_person: str = "对方", participant_id: Optional[str] = None) -> str:
    """
    根据对话记录分析指定人物的人物画像（简化版：不使用向量库）
    
    Args:
        chat_history: 对话记录内容
        target_person: 要分析的目标人物
        participant_id: 参与者ID（用于缓存，不使用向量库）
    
    Returns:
        人物画像描述
    """
    persona_prompt_path = get_abs_path("prompts/persona_prompt.txt")
    with open(persona_prompt_path, "r", encoding="utf-8") as f:
        persona_prompt = f.read()
    
    prompt_template = PromptTemplate.from_template(persona_prompt)
    chain = prompt_template | chat_model | StrOutputParser()
    
    persona_result = chain.invoke({"chat_history": chat_history, "target_person": target_person})
    
    return persona_result


def generate_persona_from_db(participant_id: str, participant_name: Optional[str] = None) -> str:
    """
    根据数据库中的历史会谈信息生成人物画像（带缓存）
    
    Args:
        participant_id: 参与者ID
        participant_name: 参与者姓名（可选）
    
    Returns:
        人物画像描述
    """
    cache = get_persona_cache()
    cache_key = f"persona:{participant_id}"
    
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"[缓存] 人物画像命中缓存: {participant_id}")
        return cached_result
    
    chat_history = get_chat_history_from_db(participant_id)
    
    if "未找到" in chat_history or "失败" in chat_history:
        return chat_history
    
    target_person = participant_name if participant_name else f"ID为{participant_id}的用户"
    result = _generate_persona(chat_history, target_person, participant_id)
    
    cache.set(cache_key, result)
    logger.info(f"[缓存] 人物画像已缓存: {participant_id}")
    
    return result


@tool(description="从数据库中拉取历史会谈信息")
def get_chat_history(participant_id: str) -> str:
    """
    从数据库获取指定参与者的对话历史（Agent工具）
    """
    return get_chat_history_from_db(participant_id)


@tool(description="根据对话记录分析指定人物的人物画像")
def generate_persona_tool(chat_history: str, target_person: str = "对方") -> str:
    """
    根据对话记录分析指定人物的人物画像（Agent工具）
    """
    return _generate_persona(chat_history, target_person)


@tool(description="根据数据库中的历史会谈信息生成人物画像")
def generate_persona_from_db_tool(participant_id: str, participant_name: Optional[str] = None) -> str:
    """
    根据数据库中的历史会谈信息生成人物画像（Agent工具）
    """
    return generate_persona_from_db(participant_id, participant_name)


@with_retry(config=llm_retry_config)
def _generate_persona_simple(chat_history: str, target_person: str = "对方") -> str:
    """
    根据对话记录生成简化版人物画像
    
    Args:
        chat_history: 对话记录内容
        target_person: 要分析的目标人物
    
    Returns:
        简化版人物画像描述
    """
    persona_prompt_path = get_abs_path("prompts/persona_simple_prompt.txt")
    with open(persona_prompt_path, "r", encoding="utf-8") as f:
        persona_prompt = f.read()
    
    prompt_template = PromptTemplate.from_template(persona_prompt)
    chain = prompt_template | chat_model | StrOutputParser()
    
    persona_result = chain.invoke({"chat_history": chat_history, "target_person": target_person})
    
    return persona_result


def generate_persona_simple_from_db(participant_id: str, participant_name: Optional[str] = None) -> str:
    """
    根据数据库中的历史会谈信息生成简化版人物画像
    
    Args:
        participant_id: 参与者ID
        participant_name: 参与者姓名（可选）
    
    Returns:
        简化版人物画像描述
    """
    chat_history = get_chat_history_from_db(participant_id)
    
    if "未找到" in chat_history or "失败" in chat_history:
        return chat_history
    
    target_person = participant_name if participant_name else f"ID为{participant_id}的用户"
    result = _generate_persona_simple(chat_history, target_person)
    
    return result


async def generate_persona_stream(chat_history: str, target_person: str = "对方"):
    """
    根据对话记录流式生成简化版人物画像
    
    Args:
        chat_history: 对话记录内容
        target_person: 要分析的目标人物
    
    Yields:
        人物画像片段
    """
    persona_prompt_path = get_abs_path("prompts/persona_simple_prompt.txt")
    with open(persona_prompt_path, "r", encoding="utf-8") as f:
        persona_prompt = f.read()
    
    prompt_template = PromptTemplate.from_template(persona_prompt)
    chain = prompt_template | chat_model | StrOutputParser()
    
    async for chunk in chain.astream({"chat_history": chat_history, "target_person": target_person}):
        yield chunk


async def generate_persona_simple_from_db_stream(participant_id: str, participant_name: Optional[str] = None):
    """
    根据数据库中的历史会谈信息流式生成简化版人物画像
    
    Args:
        participant_id: 参与者ID
        participant_name: 参与者姓名（可选）
    
    Yields:
        人物画像片段
    """
    chat_history = get_chat_history_from_db(participant_id)
    
    if "未找到" in chat_history or "失败" in chat_history:
        yield chat_history
        return
    
    target_person = participant_name if participant_name else f"ID为{participant_id}的用户"
    
    async for chunk in generate_persona_stream(chat_history, target_person):
        yield chunk
