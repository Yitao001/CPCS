import mysql.connector
from mysql.connector import Error, pooling
from typing import Optional
from utils.config_handler import db_conf
from utils.logger_handler import logger


class DatabaseConnectionPool:
    """
    数据库连接池管理器
    避免每次请求都创建新的数据库连接
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        """
        单例模式
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化连接池
        """
        if self._pool is None:
            self._init_pool()
    
    def _init_pool(self) -> None:
        """
        初始化连接池
        """
        try:
            mysql_config = db_conf.get("mysql", {})
            
            pool_config = {
                "pool_name": "persona_agent_pool",
                "pool_size": 5,
                "host": mysql_config.get("host", "localhost"),
                "user": mysql_config.get("user", "root"),
                "password": mysql_config.get("password", ""),
                "database": mysql_config.get("database", "chat_history"),
                "autocommit": True,
                "connection_timeout": 30
            }
            
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"[数据库连接池] 初始化成功，pool_size={pool_config['pool_size']}")
            
        except Error as e:
            logger.error(f"[数据库连接池] 初始化失败: {str(e)}")
            raise e
    
    def get_connection(self):
        """
        从连接池获取一个连接
        
        Returns:
            MySQL连接对象
        """
        try:
            if self._pool is None:
                self._init_pool()
            
            conn = self._pool.get_connection()
            logger.debug("[数据库连接池] 获取连接成功")
            return conn
            
        except Error as e:
            logger.error(f"[数据库连接池] 获取连接失败: {str(e)}")
            raise e
    
    def close_all(self) -> None:
        """
        关闭所有连接（慎用）
        """
        if self._pool:
            logger.info("[数据库连接池] 正在关闭所有连接...")
            self._pool = None


_db_pool_instance = None


def get_db_pool() -> DatabaseConnectionPool:
    """
    获取数据库连接池单例
    """
    global _db_pool_instance
    if _db_pool_instance is None:
        _db_pool_instance = DatabaseConnectionPool()
    return _db_pool_instance


def get_db_connection_from_pool():
    """
    从连接池获取数据库连接（兼容旧接口）
    """
    return get_db_pool().get_connection()
