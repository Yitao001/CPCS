"""
Excel 数据导入模块 - 读取 Excel 并存储到向量库
"""
import os
import json
from typing import List, Dict, Optional
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

try:
    from data.vector_db_manager import vector_db_manager
    USE_CHROMA = True
except Exception:
    USE_CHROMA = False
    logger.warning("[Excel导入] ChromaDB不可用，使用简单向量库")

from data.simple_vector_db import simple_vector_db_manager


class ExcelImporter:
    """Excel 数据导入器"""
    
    def __init__(self):
        self.excel_dir = get_abs_path("data/job_data")
        os.makedirs(self.excel_dir, exist_ok=True)
    
    def read_excel(self, file_path: str) -> List[Dict]:
        """
        读取 Excel 文件
        
        Args:
            file_path: Excel 文件路径
            
        Returns:
            岗位数据列表
        """
        try:
            import pandas as pd
            import traceback
            
            logger.info(f"[Excel导入] 正在读取文件: {file_path}")
            
            df = pd.read_excel(file_path)
            
            logger.info(f"[Excel导入] 读取到 {len(df)} 条数据")
            logger.info(f"[Excel导入] 列名: {list(df.columns)}")
            
            jobs = []
            for idx, row in df.iterrows():
                job = self._parse_row(row, idx)
                if job:
                    jobs.append(job)
            
            logger.info(f"[Excel导入] 成功解析 {len(jobs)} 个岗位")
            return jobs
            
        except ImportError as e:
            logger.error(f"[Excel导入] 请安装 pandas 和 openpyxl: pip install pandas openpyxl - {e}")
            return []
        except Exception as e:
            logger.error(f"[Excel导入] 读取失败: {e}")
            logger.error(f"[Excel导入] 详细错误: {traceback.format_exc()}")
            return []
    
    def _parse_row(self, row, idx: int) -> Optional[Dict]:
        """
        解析 Excel 行数据
        
        Args:
            row: pandas Series
            idx: 行索引
            
        Returns:
            岗位字典
        """
        try:
            job = {
                "job_name": str(row.get("岗位名称", "") or row.get(0, "")),
                "address": str(row.get("地址", "") or row.get(1, "")),
                "salary_range": str(row.get("薪资范围", "") or row.get(2, "")),
                "company_name": str(row.get("公司名称", "") or row.get(3, "")),
                "industry": str(row.get("所属行业", "") or row.get(4, "")),
                "company_size": str(row.get("公司规模", "") or row.get(5, "")),
                "company_type": str(row.get("公司类型", "") or row.get(6, "")),
                "job_code": str(row.get("岗位编码", "") or row.get(7, "")),
                "job_detail": str(row.get("岗位详情", "") or row.get(8, "")),
                "update_date": str(row.get("更新日期", "") or row.get(9, "")),
                "company_detail": str(row.get("公司详情", "") or row.get(10, "")),
                "source_url": str(row.get("岗位来源地址", "") or row.get(11, "")),
            }
            
            if not job["job_name"]:
                return None
            
            job["id"] = f"job_{idx}"
            job["category"] = self._infer_category(job["job_name"])
            
            return job
            
        except Exception as e:
            logger.warning(f"[Excel导入] 解析第 {idx} 行失败: {e}")
            return None
    
    def _infer_category(self, job_name: str) -> str:
        """
        根据岗位名称推断分类
        
        Args:
            job_name: 岗位名称
            
        Returns:
            分类名称
        """
        categories = {
            "开发": ["开发", "工程师", "程序员", "Java", "Python", "前端", "后端", "全栈", "软件"],
            "数据": ["数据", "分析", "大数据", "算法", "AI", "人工智能", "机器学习"],
            "测试": ["测试", "QA", "质量"],
            "运维": ["运维", "运维工程师", "DBA", "数据库"],
            "产品": ["产品", "产品经理", "PM"],
            "设计": ["设计", "UI", "UX", "视觉", "交互"],
            "运营": ["运营", "市场", "推广"],
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in job_name:
                    return category
        
        return "其他"
    
    def job_to_document(self, job: Dict) -> Dict:
        """
        将岗位数据转换为向量库文档
        
        Args:
            job: 岗位字典
            
        Returns:
            向量库文档
        """
        content_parts = []
        
        if job.get("job_name"):
            content_parts.append(f"岗位名称: {job['job_name']}")
        if job.get("category"):
            content_parts.append(f"岗位分类: {job['category']}")
        if job.get("salary_range"):
            content_parts.append(f"薪资范围: {job['salary_range']}")
        if job.get("address"):
            content_parts.append(f"工作地址: {job['address']}")
        if job.get("company_name"):
            content_parts.append(f"公司名称: {job['company_name']}")
        if job.get("industry"):
            content_parts.append(f"所属行业: {job['industry']}")
        if job.get("company_size"):
            content_parts.append(f"公司规模: {job['company_size']}")
        if job.get("job_detail"):
            content_parts.append(f"岗位详情: {job['job_detail']}")
        if job.get("company_detail"):
            content_parts.append(f"公司详情: {job['company_detail']}")
        
        content = "\n".join(content_parts)
        
        return {
            "id": job["id"],
            "content": content,
            "metadata": {
                "job_name": job.get("job_name", ""),
                "category": job.get("category", ""),
                "job_code": job.get("job_code", ""),
                "company_name": job.get("company_name", ""),
                "industry": job.get("industry", ""),
                "salary_range": job.get("salary_range", ""),
                "address": job.get("address", ""),
                "source_url": job.get("source_url", ""),
            }
        }
    
    def import_to_vector_db(self, file_path: str, clear: bool = False) -> bool:
        """
        导入 Excel 到向量库
        
        Args:
            file_path: Excel 文件路径
            clear: 是否先清空向量库
            
        Returns:
            是否成功
        """
        try:
            if USE_CHROMA and vector_db_manager.collection:
                db_manager = vector_db_manager
                logger.info("[Excel导入] 使用 ChromaDB")
            else:
                db_manager = simple_vector_db_manager
                logger.info("[Excel导入] 使用简单向量库")
            
            if clear:
                logger.info("[Excel导入] 清空向量库")
                db_manager.clear()
            
            jobs = self.read_excel(file_path)
            if not jobs:
                logger.warning("[Excel导入] 没有读取到岗位数据")
                return False
            
            documents = [self.job_to_document(job) for job in jobs]
            
            success = db_manager.add_documents(documents)
            
            if success:
                logger.info(f"[Excel导入] 成功导入 {len(documents)} 个岗位到向量库")
                self._save_to_json(jobs)
            else:
                logger.error("[Excel导入] 导入向量库失败")
            
            return success
            
        except Exception as e:
            logger.error(f"[Excel导入] 导入失败: {e}")
            return False
    
    def _save_to_json(self, jobs: List[Dict]):
        """
        保存岗位数据到 JSON（备用）
        
        Args:
            jobs: 岗位列表
        """
        try:
            json_path = get_abs_path("data/job_data/job_portraits_from_excel.json")
            data = {"job_portraits": jobs}
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[Excel导入] 已保存到 JSON: {json_path}")
            
        except Exception as e:
            logger.warning(f"[Excel导入] 保存 JSON 失败: {e}")


excel_importer = ExcelImporter()


def import_jobs_from_excel(file_path: str, clear: bool = False) -> bool:
    """
    从 Excel 导入岗位数据的便捷函数
    
    Args:
        file_path: Excel 文件路径
        clear: 是否先清空向量库
        
    Returns:
        是否成功
    """
    return excel_importer.import_to_vector_db(file_path, clear)


def search_jobs(query: str, top_k: int = 5) -> List[Dict]:
    """
    检索相关岗位
    
    Args:
        query: 查询文本
        top_k: 返回数量
        
    Returns:
        相关岗位列表
    """
    if USE_CHROMA and vector_db_manager.collection:
        return vector_db_manager.search(query, top_k)
    else:
        return simple_vector_db_manager.search(query, top_k)
