"""
简单向量数据库 - 使用 JSON 存储和关键词搜索（替代 ChromaDB）
"""
import os
import json
from typing import List, Dict, Optional
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


class SimpleVectorDBManager:
    """简单向量数据库管理器"""
    
    def __init__(self):
        self.persist_directory = get_abs_path("data/vector_db")
        self.data_file = os.path.join(self.persist_directory, "job_data.json")
        self.documents = []
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"[简单向量库] 加载成功，当前文档数: {len(self.documents)}")
            else:
                self.documents = []
                logger.info("[简单向量库] 初始化成功（空库）")
                
        except Exception as e:
            logger.error(f"[简单向量库] 初始化失败: {e}")
            self.documents = []
    
    def add_documents(self, documents: List[Dict]):
        """
        添加文档到数据库
        
        Args:
            documents: 文档列表，每个文档包含:
                - id: 文档ID
                - content: 文档内容
                - metadata: 元数据
        """
        try:
            for doc in documents:
                existing = next((d for d in self.documents if d["id"] == doc["id"]), None)
                if existing:
                    self.documents.remove(existing)
                self.documents.append(doc)
            
            self._save_to_disk()
            logger.info(f"[简单向量库] 成功添加 {len(documents)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"[简单向量库] 添加文档失败: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        检索相关文档（使用关键词匹配）
        
        Args:
            query: 查询文本
            top_k: 返回的文档数量
            
        Returns:
            相关文档列表
        """
        try:
            query_lower = query.lower()
            results = []
            
            for doc in self.documents:
                score = 0
                content = doc.get("content", "").lower()
                metadata = doc.get("metadata", {})
                
                job_name = metadata.get("job_name", "").lower()
                company_name = metadata.get("company_name", "").lower()
                
                if query_lower in job_name:
                    score += 10
                if query_lower in company_name:
                    score += 5
                if query_lower in content:
                    score += 3
                
                if score > 0:
                    results.append({
                        "id": doc["id"],
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "distance": 1.0 - (score / 20)
                    })
            
            results.sort(key=lambda x: x["distance"])
            results = results[:top_k]
            
            logger.info(f"[简单向量库] 检索到 {len(results)} 个相关文档")
            return results
            
        except Exception as e:
            logger.error(f"[简单向量库] 检索失败: {e}")
            return []
    
    def clear(self):
        """清空数据库"""
        try:
            self.documents = []
            self._save_to_disk()
            logger.info("[简单向量库] 已清空")
            return True
        except Exception as e:
            logger.error(f"[简单向量库] 清空失败: {e}")
            return False
    
    def count(self) -> int:
        """获取文档数量"""
        return len(self.documents)
    
    def get_all_ids(self) -> List[str]:
        """获取所有文档ID"""
        return [doc["id"] for doc in self.documents]
    
    def _save_to_disk(self):
        """保存到磁盘"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)


simple_vector_db_manager = SimpleVectorDBManager()
