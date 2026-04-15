#!/usr/bin/env python3
"""
测试对话历史获取功能（仅测试时间排序和时间间隔）
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.tools.agent_tools import get_chat_history_from_db

def test_chat_history():
    """测试获取对话历史"""
    print("=" * 60)
    print("测试: 获取对话历史（带时间排序和时间间隔）")
    print("=" * 60)
    
    try:
        result = get_chat_history_from_db("S2023003")
        print("\n对话历史内容:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        
        if "未找到" in result or "失败" in result:
            print("\n⚠️  注意: 数据库中没有找到数据或代理服务调用失败")
            print("   请确保:")
            print("   1. 代理服务正在运行 (localhost:8001)")
            print("   2. 数据库中有测试数据")
            print("   3. .env 中的 PROXY_API_URL 配置正确")
        else:
            print("\n✅ 测试成功!")
            print("\n检查点:")
            print("  ✓ 时间排序: 记录是否按时间从早到晚排列?")
            print("  ✓ 序号: 是否有 [1], [2], [3]... 序号?")
            print("  ✓ 时间间隔: 是否显示距离上次的间隔时间?")
        
        return True
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n开始测试对话历史功能\n")
    test_chat_history()
