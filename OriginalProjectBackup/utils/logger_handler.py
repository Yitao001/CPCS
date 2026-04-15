import logging
import os
import re
from datetime import datetime
from utils.path_tool import get_abs_path


#日志保存的根目录
LOG_ROOT = get_abs_path('logs')

#确保日志的目录存在
os.makedirs(LOG_ROOT,exist_ok=True)

#敏感信息模式
SENSITIVE_PATTERNS = [
    (re.compile(r'password["\s:]+([^\s,}]+)', re.IGNORECASE), 'password=***'),
    (re.compile(r'passwd["\s:]+([^\s,}]+)', re.IGNORECASE), 'passwd=***'),
    (re.compile(r'api[_-]?key["\s:]+([^\s,}]+)', re.IGNORECASE), 'api_key=***'),
    (re.compile(r'token["\s:]+([^\s,}]+)', re.IGNORECASE), 'token=***'),
    (re.compile(r'secret["\s:]+([^\s,}]+)', re.IGNORECASE), 'secret=***'),
]

class SensitiveDataFilter(logging.Filter):
    """敏感信息过滤器"""
    def filter(self, record):
        if isinstance(record.msg, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True

#日志的格式配置 srror info debug
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)



def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    #避免重复添加Handler
    if logger.handlers:
        return logger

    #添加敏感信息过滤器
    sensitive_filter = SensitiveDataFilter()
    logger.addFilter(sensitive_filter)

    #控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    console_handler.addFilter(sensitive_filter)

    logger.addHandler(console_handler)

    #文件Handle
    if not log_file:
        log_file = os.path.join(LOG_ROOT,f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file,encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    file_handler.addFilter(sensitive_filter)

    logger.addHandler(file_handler)

    return logger

#快捷获取日志器
logger = get_logger()

if __name__ == '__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")

