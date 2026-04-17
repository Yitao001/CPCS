from abc import ABC, abstractmethod
from typing import Optional
import os
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from utils.logger_handler import logger

load_dotenv()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[BaseChatModel]:
        model_provider = os.getenv("MODEL_PROVIDER", "tongyi")
        model_name = os.getenv("CHAT_MODEL_NAME", "qwen-max")
        
        logger.info(f"[模型工厂] 正在加载对话模型: {model_provider}/{model_name}")
        
        if model_provider == "tongyi" or model_provider == "dashscope":
            from langchain_community.chat_models.tongyi import ChatTongyi
            api_key = os.getenv("DASHSCOPE_API_KEY", "")
            if api_key:
                os.environ["DASHSCOPE_API_KEY"] = api_key
            return ChatTongyi(model=model_name)
        
        elif model_provider == "openai":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            return ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url=base_url
            )
        
        elif model_provider == "siliconflow":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("SILICONFLOW_API_KEY", "")
            base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
            return ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url=base_url
            )
        
        elif model_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            return ChatAnthropic(
                model=model_name,
                api_key=api_key
            )
        
        else:
            raise ValueError(f"不支持的模型提供商: {model_provider}")


chat_model = ChatModelFactory().generator()
