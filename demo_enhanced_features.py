#!/usr/bin/env python3
"""
增强功能演示脚本 - 展示智能体的核心功能
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger_handler import logger

print("=" * 80)
print("大学生职业规划智能体 - 增强功能演示")
print("=" * 80)

try:
    from agent.tools.enhanced_tools import (
        enhanced_job_matching,
        generate_detailed_action_plan,
        enhanced_report_export
    )
    from data.data_manager import job_portrait_manager, student_profile_manager, report_manager
    
    print("\n" + "=" * 80)
    print("1. 加载测试数据")
    print("=" * 80)
    
    test_student_profile = {
        "professional_skills": ["Java", "Python", "MySQL", "Git", "Linux"],
        "certificates": ["计算机二级", "英语四级"],
        "innovation_ability": 6,
        "learning_ability": 7,
        "stress_resistance": 7,
        "communication_ability": 6,
        "internship_ability": 5,
        "internship_experience": ["某科技公司 - Java开发实习生（3个月）"],
        "project_experience": ["在线商城系统 - 后端开发", "课程设计项目"],
        "completeness_score": 78,
        "competitiveness_score": 65
    }
    
    print("[OK] 测试学生数据准备完成")
    print(f"   - 专业技能: {len(test_student_profile['professional_skills'])} 项")
    print(f"   - 完整度评分: {test_student_profile['completeness_score']} 分")
    print(f"   - 竞争力评分: {test_student_profile['competitiveness_score']} 分")
    
    print("\n" + "=" * 80)
    print("2. 展示岗位画像（增强版）")
    print("=" * 80)
    
    java_job = job_portrait_manager.get_job_by_code("DEV001")
    if java_job:
        print(f"[OK] 岗位: {java_job.get('job_name')}")
        print(f"   - 类别: {java_job.get('category')}")
        print(f"   - 专业技能: {len(java_job.get('professional_skills', []))} 项")
        print(f"   - 证书要求: {len(java_job.get('certificate_requirements', []))} 项")
        print(f"   - 垂直发展路径: {len(java_job.get('vertical_path', []))} 阶")
        print(f"   - 换岗路径: {len(java_job.get('job_change_paths', []))} 条")
        
        print(f"\n   专业技能示例:")
        for skill in java_job.get('professional_skills', [])[:3]:
            print(f"   - {skill}")
        
        print(f"\n   垂直发展路径:")
        for i, path in enumerate(java_job.get('vertical_path', []), 1):
            print(f"   {i}. {path}")
    
    print("\n" + "=" * 80)
    print("3. 智能人岗匹配分析（核心功能）")
    print("=" * 80)
    
    matching_result = enhanced_job_matching.invoke({
        "student_profile_json": json.dumps(test_student_profile, ensure_ascii=False),
        "job_name": "Java后端开发工程师"
    })
    
    matching_data = json.loads(matching_result)
    
    print(f"[OK] 人岗匹配分析完成")
    print(f"\n   目标岗位: {matching_data.get('job_name')}")
    print(f"   整体匹配度: {matching_data.get('overall_score')} 分")
    print(f"   匹配等级: {matching_data.get('matching_level')}")
    
    skill_match = matching_data.get('skill_matching', {})
    print(f"\n   专业技能匹配:")
    print(f"   - 得分: {skill_match.get('score')} 分")
    print(f"   - 已掌握: {len(skill_match.get('matched', []))} 项")
    print(f"   - 待提升: {len(skill_match.get('missing', []))} 项")
    
    if skill_match.get('matched'):
        print(f"   - 已掌握技能: {', '.join(skill_match['matched'][:3])}")
    if skill_match.get('missing'):
        print(f"   - 待提升技能: {', '.join(skill_match['missing'][:3])}")
    
    competency_match = matching_data.get('competency_matching', [])
    print(f"\n   能力素质匹配:")
    for comp in competency_match[:3]:
        print(f"   - {comp['competency']}: 要求{comp['required']}分, 实际{comp['actual']}分 ({comp['level']})")
    
    gaps = matching_data.get('gap_analysis', {})
    print(f"\n   差距分析:")
    if gaps.get('critical_gaps'):
        print(f"   - 关键差距: {', '.join(gaps['critical_gaps'][:2])}")
    if gaps.get('minor_gaps'):
        print(f"   - 次要差距: {', '.join(gaps['minor_gaps'][:2])}")
    
    recommendations = matching_data.get('recommendations', [])
    print(f"\n   改进建议:")
    for rec in recommendations[:3]:
        print(f"   - {rec}")
    
    print("\n" + "=" * 80)
    print("4. 生成详细职业发展计划（核心功能）")
    print("=" * 80)
    
    action_plan = generate_detailed_action_plan.invoke({
        "student_info": "大三，计算机科学与技术专业，Java方向",
        "target_job": "Java后端开发工程师",
        "matching_result": matching_result
    })
    
    plan_data = json.loads(action_plan)
    
    print(f"[OK] 职业发展计划生成完成")
    print(f"\n   目标岗位: {plan_data.get('target_job')}")
    
    short_term = plan_data.get('short_term', {})
    print(f"\n   短期计划 ({short_term.get('duration')}):")
    for action in short_term.get('actions', [])[:3]:
        print(f"   - {action}")
    
    mid_term = plan_data.get('mid_term', {})
    print(f"\n   中期计划 ({mid_term.get('duration')}):")
    for action in mid_term.get('actions', [])[:3]:
        print(f"   - {action}")
    
    long_term = plan_data.get('long_term', {})
    print(f"\n   长期计划 ({long_term.get('duration')}):")
    for action in long_term.get('actions', [])[:3]:
        print(f"   - {action}")
    
    evaluation = plan_data.get('evaluation', {})
    print(f"\n   评估指标:")
    if evaluation.get('monthly'):
        print(f"   - 月度: {', '.join(evaluation['monthly'])}")
    if evaluation.get('quarterly'):
        print(f"   - 季度: {', '.join(evaluation['quarterly'])}")
    
    resources = plan_data.get('resources', [])
    print(f"\n   学习资源:")
    for resource in resources[:3]:
        print(f"   - {resource}")
    
    print("\n" + "=" * 80)
    print("5. 生成增强版职业发展报告（核心功能）")
    print("=" * 80)
    
    full_report = {
        "title": "张三的职业发展报告",
        "created_time": "2026-04-15",
        "student_info": {
            "name": "张三",
            "major": "计算机科学与技术",
            "grade": "大三",
            "school": "某某大学"
        },
        "student_profile": test_student_profile,
        "job_matching": matching_data,
        "career_path": {
            "vertical_path": java_job.get('vertical_path', []),
            "job_change_paths": java_job.get('job_change_paths', [])
        },
        "action_plan": plan_data
    }
    
    markdown_report = enhanced_report_export.invoke({
        "student_id": "demo_001",
        "report_data": json.dumps(full_report, ensure_ascii=False),
        "format": "markdown"
    })
    
    print(f"[OK] Markdown格式报告生成完成")
    print(f"   报告长度: {len(markdown_report)} 字符")
    
    report_file = os.path.join(os.path.dirname(__file__), "demo_career_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(markdown_report)
    
    print(f"   报告已保存至: {report_file}")
    
    html_report = enhanced_report_export.invoke({
        "student_id": "demo_001",
        "report_data": json.dumps(full_report, ensure_ascii=False),
        "format": "html"
    })
    
    print(f"\n[OK] HTML格式报告生成完成")
    print(f"   报告长度: {len(html_report)} 字符")
    
    html_file = os.path.join(os.path.dirname(__file__), "demo_career_report.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_report)
    
    print(f"   报告已保存至: {html_file}")
    
    print("\n" + "=" * 80)
    print("增强功能演示完成！")
    print("=" * 80)
    print("\n核心功能亮点：")
    print("1. [OK] 智能人岗匹配 - 多维度分析，精准评分")
    print("2. [OK] 详细行动计划 - 短中长期，可落地执行")
    print("3. [OK] 精美报告导出 - Markdown和HTML双格式")
    print("4. [OK] 差距分析 - 明确指出改进方向")
    print("5. [OK] 个性化建议 - 根据学生情况定制")
    print("\n生成的文件：")
    print(f"- {report_file}")
    print(f"- {html_file}")
    print("\n您可以在浏览器中打开HTML文件查看精美报告！")
    print("=" * 80)
    
except Exception as e:
    logger.error(f"演示失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
