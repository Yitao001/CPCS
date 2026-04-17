"""
增强版工具函数 - 突出核心功能
"""
from langchain_core.tools import tool
from typing import Dict, List, Optional
import json
import re
from utils.logger_handler import logger


def calculate_skill_matching(student_skills: List[str], job_skills: List[str]) -> Dict:
    """
    计算技能匹配度
    """
    if not job_skills:
        return {"score": 0, "matched": [], "missing": [], "match_count": 0, "total_count": 0}
    
    matched = []
    missing = []
    
    student_skills_lower = [s.lower() for s in student_skills]
    
    for skill in job_skills:
        if any(s in skill.lower() for s in student_skills_lower):
            matched.append(skill)
        else:
            missing.append(skill)
    
    score = int((len(matched) / len(job_skills)) * 100) if job_skills else 0
    
    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "match_count": len(matched),
        "total_count": len(job_skills)
    }


def calculate_competency_matching(student_profile: Dict, job_requirements: Dict) -> List[Dict]:
    """
    计算能力素质匹配度
    """
    competencies = [
        "innovation_ability",
        "learning_ability",
        "stress_resistance",
        "communication_ability",
        "internship_ability"
    ]
    
    results = []
    
    for competency in competencies:
        student_score = student_profile.get(competency, 0)
        required_score = job_requirements.get(competency, 5)
        
        gap = student_score - required_score
        
        if gap >= 0:
            level = "超出要求"
        elif gap >= -1:
            level = "基本达标"
        elif gap >= -3:
            level = "需提升"
        else:
            level = "差距较大"
        
        competency_name = {
            "innovation_ability": "创新能力",
            "learning_ability": "学习能力",
            "stress_resistance": "抗压能力",
            "communication_ability": "沟通能力",
            "internship_ability": "实习能力"
        }.get(competency, competency)
        
        results.append({
            "competency": competency_name,
            "required": required_score,
            "actual": student_score,
            "gap": gap,
            "level": level
        })
    
    return results


@tool(description="智能人岗匹配分析，输入学生能力画像和岗位名称，返回详细的匹配分析报告")
def enhanced_job_matching(student_profile_json: str, job_name: str) -> str:
    """
    增强版人岗匹配分析
    """
    try:
        from data.data_manager import job_portrait_manager
        
        student_profile = json.loads(student_profile_json)
        
        job = job_portrait_manager.get_job_by_name(job_name)
        if not job:
            job = job_portrait_manager.get_job_by_code(job_name)
        
        if not job:
            return f"未找到岗位: {job_name}"
        
        student_skills = student_profile.get("professional_skills", [])
        job_skills = job.get("professional_skills", [])
        
        skill_match = calculate_skill_matching(student_skills, job_skills)
        
        competency_match = calculate_competency_matching(student_profile, job)
        
        skill_score = skill_match["score"]
        competency_score = sum(
            max(0, min(100, (c["actual"] / c["required"]) * 100))
            for c in competency_match if c["required"] > 0
        ) / len(competency_match) if competency_match else 0
        
        experience_bonus = 0
        if student_profile.get("internship_experience"):
            experience_bonus += 10
        if student_profile.get("project_experience"):
            experience_bonus += 5
        
        overall_score = int(skill_score * 0.5 + competency_score * 0.3 + experience_bonus * 0.2)
        overall_score = min(100, max(0, overall_score))
        
        if overall_score >= 80:
            matching_level = "高度匹配"
        elif overall_score >= 60:
            matching_level = "基本匹配"
        elif overall_score >= 40:
            matching_level = "部分匹配"
        else:
            matching_level = "不太匹配"
        
        critical_gaps = []
        minor_gaps = []
        
        if skill_match["missing"]:
            critical_gaps.extend(skill_match["missing"][:3])
        
        for c in competency_match:
            if c["level"] == "差距较大":
                critical_gaps.append(f"{c['competency']}需要提升")
            elif c["level"] == "需提升":
                minor_gaps.append(f"{c['competency']}可以加强")
        
        recommendations = []
        if critical_gaps:
            recommendations.append(f"优先学习: {', '.join(critical_gaps[:2])}")
        if minor_gaps:
            recommendations.append(f"持续提升: {', '.join(minor_gaps[:2])}")
        if not student_profile.get("internship_experience"):
            recommendations.append("建议寻找相关实习机会")
        if len(student_profile.get("project_experience", [])) < 2:
            recommendations.append("建议多参与项目实践")
        
        result = {
            "job_name": job.get("job_name"),
            "overall_score": overall_score,
            "matching_level": matching_level,
            "skill_matching": skill_match,
            "competency_matching": competency_match,
            "gap_analysis": {
                "critical_gaps": critical_gaps,
                "minor_gaps": minor_gaps
            },
            "recommendations": recommendations
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"增强版人岗匹配失败: {e}")
        return f"匹配分析失败: {str(e)}"


@tool(description="生成详细的职业发展计划，包含短期、中期、长期目标和具体行动项")
def generate_detailed_action_plan(student_info: str, target_job: str, matching_result: str) -> str:
    """
    生成详细的职业发展行动计划
    """
    try:
        matching_data = json.loads(matching_result) if matching_result else {}
        
        job_name = matching_data.get("job_name", target_job)
        gaps = matching_data.get("gap_analysis", {})
        recommendations = matching_data.get("recommendations", [])
        
        short_term = []
        mid_term = []
        long_term = []
        
        critical_gaps = gaps.get("critical_gaps", [])
        minor_gaps = gaps.get("minor_gaps", [])
        
        for gap in critical_gaps[:2]:
            short_term.append(f"学习{gap}，每周投入8小时")
        
        for gap in minor_gaps[:2]:
            short_term.append(f"提升{gap}，每周投入4小时")
        
        short_term.append("完成1个相关实战项目")
        short_term.append("准备3份面试作品")
        
        mid_term.append("争取3-6个月的相关实习")
        mid_term.append("深入学习高级技能")
        mid_term.append("参与1-2个开源项目")
        mid_term.append("考取1个相关证书")
        
        long_term.append("成为中级工程师")
        long_term.append("积累3-5年工作经验")
        long_term.append("向高级/专家方向发展")
        long_term.append("建立个人技术影响力")
        
        evaluation_metrics = {
            "monthly": [
                "技能学习进度",
                "项目完成情况",
                "技术文章阅读量"
            ],
            "quarterly": [
                "项目作品集质量",
                "技术能力评估",
                "实习/工作反馈"
            ],
            "yearly": [
                "职业目标达成度",
                "薪资增长情况",
                "技能等级提升"
            ]
        }
        
        plan = {
            "target_job": job_name,
            "short_term": {
                "duration": "3-6个月",
                "actions": short_term
            },
            "mid_term": {
                "duration": "6-18个月",
                "actions": mid_term
            },
            "long_term": {
                "duration": "1-3年",
                "actions": long_term
            },
            "evaluation": evaluation_metrics,
            "resources": [
                "在线课程平台（Coursera、慕课网、极客时间）",
                "技术社区（GitHub、Stack Overflow、掘金）",
                "实习招聘平台（实习僧、BOSS直聘、猎聘）"
            ]
        }
        
        return json.dumps(plan, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"生成行动计划失败: {e}")
        return f"生成行动计划失败: {str(e)}"


@tool(description="增强版报告导出，支持生成更详细、更美观的报告")
def enhanced_report_export(student_id: str, report_data: str, format: str = "markdown") -> str:
    """
    增强版报告导出
    """
    try:
        report = json.loads(report_data)
        
        if format == "markdown":
            return _generate_enhanced_markdown(report)
        elif format == "html":
            return _generate_enhanced_html(report)
        else:
            return json.dumps(report, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"增强版报告导出失败: {e}")
        return f"报告导出失败: {str(e)}"


def _generate_enhanced_markdown(report: Dict) -> str:
    """
    生成增强版Markdown报告
    """
    md = []
    
    title = report.get("title", "大学生职业发展报告")
    student_name = report.get("student_info", {}).get("name", "同学")
    
    md.append(f"# {title}")
    md.append(f"\n**学生姓名**: {student_name}")
    md.append(f"\n**生成时间**: {report.get('created_time', '')}")
    md.append("\n---")
    
    md.append("\n## 一、执行摘要")
    
    job_matching = report.get("job_matching", {})
    overall_score = job_matching.get("total_score", 0)
    target_job = job_matching.get("target_job", "未指定")
    
    if overall_score >= 80:
        summary = "您与目标岗位高度匹配，建议积极投递简历，争取面试机会！"
    elif overall_score >= 60:
        summary = "您与目标岗位基本匹配，建议补充关键技能后再投递。"
    else:
        summary = "您与目标岗位还有一定差距，建议先提升核心技能。"
    
    md.append(f"\n{summary}")
    md.append(f"\n- **目标岗位**: {target_job}")
    md.append(f"\n- **整体匹配度**: {overall_score}分")
    
    career_path = report.get("career_path", {})
    if career_path.get("vertical_path"):
        md.append(f"\n- **推荐发展路径**: {' → '.join(career_path['vertical_path'])}")
    
    md.append("\n---")
    
    md.append("\n## 二、学生能力画像")
    
    student_info = report.get("student_info", {})
    if student_info:
        md.append("\n### 2.1 基本信息")
        for key, value in student_info.items():
            md.append(f"\n- **{key}**: {value}")
    
    if "student_profile" in report:
        profile = report["student_profile"]
        md.append("\n### 2.2 能力评分")
        md.append(f"\n- **完整度**: {profile.get('completeness_score', 0)}分")
        md.append(f"\n- **竞争力**: {profile.get('competitiveness_score', 0)}分")
        
        skills = profile.get("professional_skills", [])
        if skills:
            md.append("\n### 2.3 专业技能")
            for skill in skills:
                md.append(f"\n- {skill}")
    
    md.append("\n---")
    
    md.append("\n## 三、人岗匹配分析")
    
    if job_matching:
        md.append(f"\n### 3.1 整体匹配度: {overall_score}分")
        
        if "skill_matching" in job_matching:
            md.append("\n### 3.2 专业技能匹配")
            skill_match = job_matching["skill_matching"]
            md.append(f"\n- 匹配得分: {skill_match.get('score', 0)}分")
            md.append(f"\n- 已掌握: {', '.join(skill_match.get('matched', []))}")
            md.append(f"\n- 待提升: {', '.join(skill_match.get('missing', []))}")
        
        if "competency_matching" in job_matching:
            md.append("\n### 3.3 能力素质匹配")
            for comp in job_matching["competency_matching"]:
                md.append(f"\n- {comp.get('competency', '')}: 要求{comp.get('required', 0)}分, 实际{comp.get('actual', 0)}分 ({comp.get('level', '')})")
        
        if "gap_analysis" in job_matching:
            md.append("\n### 3.4 差距分析")
            gaps = job_matching["gap_analysis"]
            if gaps.get("critical_gaps"):
                md.append(f"\n- **关键差距**: {', '.join(gaps['critical_gaps'])}")
            if gaps.get("minor_gaps"):
                md.append(f"\n- **次要差距**: {', '.join(gaps['minor_gaps'])}")
        
        if "recommendations" in job_matching:
            md.append("\n### 3.5 改进建议")
            for rec in job_matching["recommendations"]:
                md.append(f"\n- {rec}")
    
    md.append("\n---")
    
    md.append("\n## 四、职业路径规划")
    
    if career_path:
        if career_path.get("vertical_path"):
            md.append("\n### 4.1 垂直发展路径")
            for i, job in enumerate(career_path["vertical_path"], 1):
                md.append(f"\n{i}. {job}")
        
        if career_path.get("job_change_paths"):
            md.append("\n### 4.2 换岗路径")
            for i, path in enumerate(career_path["job_change_paths"], 1):
                md.append(f"\n{i}. {path}")
    
    md.append("\n---")
    
    md.append("\n## 五、行动计划")
    
    action_plan = report.get("action_plan", {})
    if action_plan:
        if action_plan.get("short_term"):
            md.append("\n### 5.1 短期计划（3-6个月）")
            for action in action_plan["short_term"]:
                md.append(f"\n- [ ] {action}")
        
        if action_plan.get("mid_term"):
            md.append("\n### 5.2 中期计划（6-18个月）")
            for action in action_plan["mid_term"]:
                md.append(f"\n- [ ] {action}")
        
        if action_plan.get("long_term"):
            md.append("\n### 5.3 长期计划（1-3年）")
            for action in action_plan["long_term"]:
                md.append(f"\n- [ ] {action}")
        
        if action_plan.get("evaluation"):
            md.append("\n### 5.4 评估指标")
            eval_metrics = action_plan["evaluation"]
            if eval_metrics.get("monthly"):
                md.append("\n**月度评估**:")
                for metric in eval_metrics["monthly"]:
                    md.append(f"\n- {metric}")
            if eval_metrics.get("quarterly"):
                md.append("\n**季度评估**:")
                for metric in eval_metrics["quarterly"]:
                    md.append(f"\n- {metric}")
            if eval_metrics.get("yearly"):
                md.append("\n**年度评估**:")
                for metric in eval_metrics["yearly"]:
                    md.append(f"\n- {metric}")
    
    md.append("\n---")
    
    md.append("\n## 六、附录")
    md.append("\n### 6.1 学习资源推荐")
    md.append("\n- 在线课程: Coursera、慕课网、极客时间")
    md.append("\n- 技术社区: GitHub、掘金、知乎")
    md.append("\n- 招聘平台: BOSS直聘、猎聘、实习僧")
    
    md.append("\n---")
    md.append("\n*本报告由AI智能生成，仅供参考。请结合自身实际情况制定职业规划。*")
    
    return "\n".join(md)


def _generate_enhanced_html(report: Dict) -> str:
    """
    生成增强版HTML报告
    """
    markdown_content = _generate_enhanced_markdown(report)
    
    try:
        import markdown
        html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
    except ImportError:
        html_content = f"<pre>{markdown_content}</pre>"
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report.get('title', '职业发展报告')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 50px;
        }}
        h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        h2 {{
            color: #34495e;
            font-size: 1.6em;
            margin-top: 35px;
            margin-bottom: 15px;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}
        h3 {{
            color: #555;
            font-size: 1.2em;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        p {{
            margin-bottom: 15px;
        }}
        ul {{
            margin-left: 25px;
            margin-bottom: 15px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, #667eea, #764ba2);
            margin: 30px 0;
        }}
        .score-high {{
            color: #27ae60;
            font-weight: bold;
        }}
        .score-medium {{
            color: #f39c12;
            font-weight: bold;
        }}
        .score-low {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .summary-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0;
        }}
        .summary-box h3 {{
            color: white;
            margin-top: 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #888;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 20px 10px;
            }}
            .container {{
                padding: 30px 20px;
            }}
            h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
    <div class="footer">
        本报告由AI智能生成，仅供参考。请结合自身实际情况制定职业规划。
    </div>
</body>
</html>
"""
    return html
