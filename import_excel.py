#!/usr/bin/env python3
"""
Excel 数据导入脚本

使用方法:
    python import_excel.py <excel_file_path> [--clear]

示例:
    python import_excel.py data/job_data/jobs.xlsx
    python import_excel.py data/job_data/jobs.xlsx --clear
"""
import sys
import argparse
from data.excel_importer import import_jobs_from_excel, search_jobs
from utils.logger_handler import logger


def main():
    parser = argparse.ArgumentParser(description="导入 Excel 岗位数据到向量库")
    parser.add_argument("file", help="Excel 文件路径")
    parser.add_argument("--clear", action="store_true", help="是否先清空向量库")
    parser.add_argument("--test", action="store_true", help="导入后进行检索测试")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("大学生职业规划智能体 - Excel 数据导入")
    print("=" * 60)
    
    success = import_jobs_from_excel(args.file, args.clear)
    
    if success:
        print("\n[OK] 导入成功！")
        
        if args.test:
            print("\n" + "=" * 60)
            print("测试检索功能...")
            print("=" * 60)
            
            test_queries = [
                "Java后端开发",
                "人工智能算法工程师",
                "数据分析师",
                "前端开发",
                "软件测试"
            ]
            
            for query in test_queries:
                print(f"\n[SEARCH] 查询: {query}")
                results = search_jobs(query, top_k=3)
                if results:
                    for i, doc in enumerate(results, 1):
                        print(f"  {i}. {doc['metadata'].get('job_name', '未知')}")
                        print(f"     公司: {doc['metadata'].get('company_name', '未知')}")
                        print(f"     薪资: {doc['metadata'].get('salary_range', '未知')}")
                        print(f"     相似度: {1 - doc.get('distance', 0):.2f}")
                else:
                    print("  未找到相关岗位")
    else:
        print("\n[ERROR] 导入失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
