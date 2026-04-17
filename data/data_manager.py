"""
数据管理模块 - 学生能力画像、报告管理（岗位画像已改用向量库）
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


class StudentProfileManager:
    """学生就业能力画像管理器"""
    
    def __init__(self):
        self.data_dir = get_abs_path("data/student_data")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_student_profile(self, student_id: str, profile: Dict) -> bool:
        """保存学生就业能力画像"""
        try:
            file_path = os.path.join(self.data_dir, f"{student_id}_profile.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            logger.info(f"[学生画像] 已保存学生画像: {student_id}")
            return True
        except Exception as e:
            logger.error(f"[学生画像] 保存失败: {e}")
            return False
    
    def load_student_profile(self, student_id: str) -> Optional[Dict]:
        """加载学生就业能力画像"""
        try:
            file_path = os.path.join(self.data_dir, f"{student_id}_profile.json")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                logger.info(f"[学生画像] 已加载学生画像: {student_id}")
                return profile
            return None
        except Exception as e:
            logger.error(f"[学生画像] 加载失败: {e}")
            return None


class ReportManager:
    """职业发展报告管理器"""
    
    def __init__(self):
        self.data_dir = get_abs_path("data/reports")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_report(self, student_id: str, report: Dict, report_type: str = "career_development") -> bool:
        """保存职业发展报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.data_dir, f"{student_id}_{report_type}_{timestamp}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"[报告管理] 已保存报告: {student_id}")
            return True
        except Exception as e:
            logger.error(f"[报告管理] 保存失败: {e}")
            return False
    
    def export_report(self, student_id: str, report: Dict, format: str = "markdown") -> str:
        """导出报告为指定格式"""
        if format == "markdown":
            return self._export_to_markdown(report)
        elif format == "html":
            return self._export_to_html(report)
        else:
            return json.dumps(report, ensure_ascii=False, indent=2)
    
    def _export_to_markdown(self, report: Dict) -> str:
        """导出为Markdown格式"""
        md_content = []
        md_content.append(f"# {report.get('title', '大学生职业发展报告')}\n")
        md_content.append(f"\n**生成时间**: {report.get('created_time', '')}\n")
        
        if "student_info" in report:
            md_content.append("\n## 一、学生基本信息\n")
            for key, value in report["student_info"].items():
                md_content.append(f"- **{key}**: {value}\n")
        
        if "job_matching" in report:
            md_content.append("\n## 二、职业探索与岗位匹配\n")
            matching = report["job_matching"]
            md_content.append(f"\n### 目标岗位: {matching.get('target_job', '')}\n")
            md_content.append(f"\n**整体匹配度**: {matching.get('total_score', 0)}分\n")
            
            if "skill_matching" in matching:
                md_content.append("\n#### 专业技能匹配\n")
                for skill in matching["skill_matching"]:
                    md_content.append(f"- {skill.get('name', '')}: {skill.get('score', 0)}分\n")
            
            if "quality_matching" in matching:
                md_content.append("\n#### 通用素质匹配\n")
                for quality in matching["quality_matching"]:
                    md_content.append(f"- {quality.get('name', '')}: {quality.get('score', 0)}分\n")
        
        if "career_path" in report:
            md_content.append("\n## 三、职业目标设定与职业路径规划\n")
            path = report["career_path"]
            
            if "vertical_path" in path:
                md_content.append("\n### 垂直发展路径\n")
                for i, job in enumerate(path["vertical_path"], 1):
                    md_content.append(f"{i}. {job}\n")
            
            if "industry_trend" in path:
                md_content.append(f"\n### 行业发展趋势\n{path['industry_trend']}\n")
        
        if "action_plan" in report:
            md_content.append("\n## 四、行动计划与成果展示\n")
            plan = report["action_plan"]
            
            if "short_term" in plan:
                md_content.append("\n### 短期计划（1年内）\n")
                for item in plan["short_term"]:
                    md_content.append(f"- {item}\n")
            
            if "mid_term" in plan:
                md_content.append("\n### 中期计划（1-3年）\n")
                for item in plan["mid_term"]:
                    md_content.append(f"- {item}\n")
            
            if "evaluation" in plan:
                md_content.append("\n### 评估周期与指标\n")
                md_content.append(f"{plan['evaluation']}\n")
        
        return "\n".join(md_content)
    
    def _export_to_html(self, report: Dict) -> str:
        """导出为HTML格式"""
        md_content = self._export_to_markdown(report)
        try:
            import markdown
            html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report.get('title', '职业发展报告')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #555; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
        except ImportError:
            return "<html><body><pre>" + md_content + "</pre></body></html>"


student_profile_manager = StudentProfileManager()
report_manager = ReportManager()
