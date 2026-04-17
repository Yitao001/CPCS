from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


def load_system_prompts():
    try:
        system_prompts_path = get_abs_path(prompts_conf['main_prompt_path'])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有main_prompt_path配置项")
        raise e

    try:
        return open(system_prompts_path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts]解析系统提示词出错，{str(e)}")
        raise e


def load_career_assessment_prompts():
    try:
        path = get_abs_path(prompts_conf['career_assessment_prompt_path'])
    except KeyError as e:
        logger.error(f"[load_career_assessment_prompts]在yaml配置项中没有career_assessment_prompt_path配置项")
        raise e

    try:
        return open(path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_career_assessment_prompts]解析职业测评提示词出错，{str(e)}")
        raise e


def load_course_recommendation_prompts():
    try:
        path = get_abs_path(prompts_conf['course_recommendation_prompt_path'])
    except KeyError as e:
        logger.error(f"[load_course_recommendation_prompts]在yaml配置项中没有course_recommendation_prompt_path配置项")
        raise e

    try:
        return open(path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_course_recommendation_prompts]解析课程推荐提示词出错，{str(e)}")
        raise e


def load_job_guidance_prompts():
    try:
        path = get_abs_path(prompts_conf['job_guidance_prompt_path'])
    except KeyError as e:
        logger.error(f"[load_job_guidance_prompts]在yaml配置项中没有job_guidance_prompt_path配置项")
        raise e

    try:
        return open(path,"r",encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_job_guidance_prompts]解析就业指导提示词出错，{str(e)}")
        raise e


if __name__ == '__main__':
    print(load_system_prompts())
