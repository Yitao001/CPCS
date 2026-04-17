from functools import lru_cache
from typing import Optional
from datetime import datetime, timedelta
from utils.logger_handler import logger


class TTLCache:
    """
    带TTL（生存时间）的内存缓存
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._access_order = []
        logger.info(f"[缓存管理器] 初始化完成，max_size={max_size}, ttl={ttl_seconds}s")
    
    def get(self, key: str) -> Optional[str]:
        if key not in self._cache:
            return None
        
        value, expire_time = self._cache[key]
        
        if datetime.now() > expire_time:
            self.delete(key)
            logger.debug(f"[缓存管理器] 缓存已过期: {key}")
            return None
        
        self._update_access_order(key)
        logger.debug(f"[缓存管理器] 缓存命中: {key}")
        return value
    
    def set(self, key: str, value: str) -> None:
        if key in self._cache:
            self.delete(key)
        
        if len(self._cache) >= self.max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
            logger.debug(f"[缓存管理器] 缓存已满，删除最旧条目: {oldest_key}")
        
        expire_time = datetime.now() + timedelta(seconds=self.ttl_seconds)
        self._cache[key] = (value, expire_time)
        self._access_order.append(key)
        logger.debug(f"[缓存管理器] 缓存已设置: {key}")
    
    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
    
    def clear(self) -> None:
        self._cache.clear()
        self._access_order.clear()
        logger.info("[缓存管理器] 缓存已清空")
    
    def _update_access_order(self, key: str) -> None:
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def get_stats(self) -> dict:
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }


_career_cache = None


def get_career_cache() -> TTLCache:
    global _career_cache
    if _career_cache is None:
        _career_cache = TTLCache(max_size=100, ttl_seconds=3600)
    return _career_cache
