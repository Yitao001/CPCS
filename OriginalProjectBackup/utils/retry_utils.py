import time
from typing import Callable, TypeVar, Optional
from functools import wraps
from utils.logger_handler import logger

T = TypeVar('T')


class RetryConfig:
    """重试配置"""
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        timeout: Optional[float] = 30.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.timeout = timeout


def with_retry(
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,)
):
    """
    带重试和指数退避的装饰器
    
    Args:
        config: 重试配置
        exceptions: 需要重试的异常类型
    
    Returns:
        装饰器
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    if attempt > 0:
                        logger.info(
                            f"[重试] 函数 {func.__name__} 第 {attempt} 次重试，"
                            f"延迟 {delay:.2f}s"
                        )
                    
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt >= config.max_retries:
                        logger.error(
                            f"[重试失败] 函数 {func.__name__} 重试 {config.max_retries} 次后仍然失败: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"[重试] 函数 {func.__name__} 调用失败 (尝试 {attempt + 1}/{config.max_retries + 1}): {e}"
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * config.exponential_base, config.max_delay)
            
            raise last_exception
        
        return wrapper
    
    return decorator


# 默认重试配置（适合LLM调用）
llm_retry_config = RetryConfig(
    max_retries=3,
    initial_delay=2.0,
    max_delay=10.0,
    exponential_base=2.0,
    timeout=60.0
)
