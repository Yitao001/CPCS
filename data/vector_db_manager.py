"""
向量数据库管理模块 - RAG 支持
"""
import os
os.environ["CHROMA_PYTHON_ONLY"] = "1"
from typing import List, Dict, Optional
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


class VectorDBManager:
    """向量数据库管理器"""
    
    def __init__(self):
        self.persist_directory = get_abs_path("data/vector_db")
        self.collection_name = "job_portraits"
        self._init_db()
    
    def _init_db(self):
        """初始化向量数据库"""
        try:
            import chromadb
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            self.sentence_transformer_ef = None
            logger.info("[向量库] 使用默认嵌入函数")
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.sentence_transformer_ef,
                metadata={"description": "岗位画像向量数据库"}
            )
            
            count = self.collection.count()
            logger.info(f"[向量库] 初始化成功，当前文档数: {count}")
            
        except Exception as e:
            logger.error(f"[向量库] 初始化失败: {e}")
            self.collection = None
    
    def add_documents(self, documents: List[Dict]):
        """
        添加文档到向量库
        
        Args:
            documents: 文档列表，每个文档包含:
                - id: 文档ID
                - content: 文档内容
                - metadata: 元数据
        """
        if not self.collection:
            logger.error("[向量库] 向量库未初始化")
            return False
        
        try:
            batch_size = 500
            total_added = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                ids = [doc["id"] for doc in batch]
                contents = [doc["content"] for doc in batch]
                metadatas = [doc.get("metadata", {}) for doc in batch]
                
                self.collection.add(
                    ids=ids,
                    documents=contents,
                    metadatas=metadatas
                )
                
                total_added += len(batch)
                logger.info(f"[向量库] 已添加 {total_added}/{len(documents)} 个文档")
            
            logger.info(f"[向量库] 成功添加 {len(documents)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"[向量库] 添加文档失败: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回的文档数量
            
        Returns:
            相关文档列表
        """
        if not self.collection:
            logger.error("[向量库] 向量库未初始化")
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            documents = []
            for i in range(len(results["ids"][0])):
                doc = {
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                }
                documents.append(doc)
            
            logger.info(f"[向量库] 检索到 {len(documents)} 个相关文档")
            return documents
            
        except Exception as e:
            logger.error(f"[向量库] 检索失败: {e}")
            return []
    
    def clear(self):
        """清空向量库"""
        if not self.collection:
            return False
        
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.sentence_transformer_ef,
                metadata={"description": "岗位画像向量数据库"}
            )
            logger.info("[向量库] 已清空")
            return True
        except Exception as e:
            logger.error(f"[向量库] 清空失败: {e}")
            return False
    
    def count(self) -> int:
        """获取文档数量"""
        if not self.collection:
            return 0
        return self.collection.count()
    
    def get_all_ids(self) -> List[str]:
        """获取所有文档ID"""
        if not self.collection:
            return []
        try:
            results = self.collection.get()
            return results["ids"]
        except Exception as e:
            logger.error(f"[向量库] 获取ID失败: {e}")
            return []


vector_db_manager = VectorDBManager()
