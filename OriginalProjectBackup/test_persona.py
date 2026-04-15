#!/usr/bin/env python3
"""
测试人物画像分析功能
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.tools.agent_tools import get_chat_history_from_db, generate_persona_simple_from_db

def test_chat_history():
    """测试获取对话历史"""
    print("=" * 60)
    print("测试 1: 获取对话历史（带时间排序和时间间隔）")
    print("=" * 60)
    
    try:
        result = get_chat_history_from_db("S2023003")
        print("\n对话历史内容:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_simple_persona():
    """测试简化版人物画像"""
    print("\n" + "=" * 60)
    print("测试 2: 简化版人物画像")
    print("=" * 60)
    
    try:
        result = generate_persona_simple_from_db("S2023003")
        print("\n人物画像内容:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        return True
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 开始测试人物画像分析功能\n")
    
    success_count = 0
    total_count = 2
    
    if test_chat_history():
        success_count += 1
    
    if test_simple_persona():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"测试完成: {success_count}/{total_count} 成功")
    print("=" * 60)
