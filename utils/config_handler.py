"""
yaml配置加载
"""
import yaml
import os
from utils.path_tool import get_abs_path
from dotenv import load_dotenv

load_dotenv()


def load_prompts_config(config_path: str=get_abs_path("config/prompts.yml"),encoding: str="utf-8"):
    if os.path.exists(config_path):
        with open(config_path,"r",encoding=encoding) as f:
            return yaml.load(f,Loader=yaml.FullLoader)
    return {}


def load_agent_config(config_path: str=get_abs_path("config/agent.yml"),encoding: str="utf-8"):
    if os.path.exists(config_path):
        with open(config_path,"r",encoding=encoding) as f:
            return yaml.load(f,Loader=yaml.FullLoader)
    return {}


def load_database_config(config_path: str=get_abs_path("config/database.yml"),encoding: str="utf-8"):
    if os.path.exists(config_path):
        with open(config_path,"r",encoding=encoding) as f:
            config = yaml.load(f,Loader=yaml.FullLoader)
        
        mysql_config = config.get("mysql", {})
        mysql_config["host"] = os.getenv("MYSQL_HOST", mysql_config.get("host", "localhost"))
        mysql_config["user"] = os.getenv("MYSQL_USER", mysql_config.get("user", "root"))
        mysql_config["password"] = os.getenv("MYSQL_PASSWORD", mysql_config.get("password", ""))
        mysql_config["database"] = os.getenv("MYSQL_DATABASE", mysql_config.get("database", "career_planning_db"))
        config["mysql"] = mysql_config
        
        return config
    return {"mysql": {}}


def get_security_config():
    return {
        "api_key": os.getenv("API_KEY", ""),
        "cors_origins": os.getenv("CORS_ORIGINS", "").split(","),
        "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    }


def get_server_config():
    return {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000"))
    }


prompts_conf = load_prompts_config()
agent_conf = load_agent_config()
db_conf = load_database_config()
security_conf = get_security_config()
server_conf = get_server_config()

if __name__ == '__main__':
    print("配置加载成功")
