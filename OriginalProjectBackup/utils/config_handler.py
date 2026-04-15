"""
yaml
k:v
"""
import yaml
import os
from utils.path_tool import get_abs_path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def load_rag_config(config_path: str=get_abs_path("config/rag.yml"),encoding: str="utf-8"):
    try:
        with open(config_path,"r",encoding=encoding) as f:
            return yaml.load(f,Loader=yaml.FullLoader)
    except FileNotFoundError:
        return {}


def load_chroma_config(config_path: str=get_abs_path("config/chroma.yml"),encoding: str="utf-8"):
    try:
        with open(config_path,"r",encoding=encoding) as f:
            return yaml.load(f,Loader=yaml.FullLoader)
    except FileNotFoundError:
        return {}


def load_prompts_config(config_path: str=get_abs_path("config/prompts.yml"),encoding: str="utf-8"):
    with open(config_path,"r",encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)


def load_agent_config(config_path: str=get_abs_path("config/agent.yml"),encoding: str="utf-8"):
    with open(config_path,"r",encoding=encoding) as f:
        return yaml.load(f,Loader=yaml.FullLoader)


def load_database_config(config_path: str=get_abs_path("config/database.yml"),encoding: str="utf-8"):
    """
    加载数据库配置，优先使用环境变量
    """
    with open(config_path,"r",encoding=encoding) as f:
        config = yaml.load(f,Loader=yaml.FullLoader)
    
    # 从环境变量覆盖配置
    mysql_config = config.get("mysql", {})
    mysql_config["host"] = os.getenv("MYSQL_HOST", mysql_config.get("host", "localhost"))
    mysql_config["user"] = os.getenv("MYSQL_USER", mysql_config.get("user", "root"))
    mysql_config["password"] = os.getenv("MYSQL_PASSWORD", mysql_config.get("password", ""))
    mysql_config["database"] = os.getenv("MYSQL_DATABASE", mysql_config.get("database", "chat_history"))
    config["mysql"] = mysql_config
    
    return config


def get_security_config():
    """
    获取安全配置
    """
    return {
        "api_key": os.getenv("API_KEY", ""),
        "cors_origins": os.getenv("CORS_ORIGINS", "").split(","),
        "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    }


rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
agent_conf = load_agent_config()
db_conf = load_database_config()
security_conf = get_security_config()

if __name__ == '__main__':
    print(rag_conf["chat_model_name"])
