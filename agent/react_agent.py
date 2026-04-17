from langchain.agents import create_agent

from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (
    career_assessment,
    course_recommendation,
    job_guidance,
    get_all_job_portraits,
    get_job_portrait,
    get_job_relation_graph,
    parse_resume,
    job_matching_analysis,
    generate_career_report,
    export_career_report,
    get_student_profile
)
from agent.tools.middleware import monitor_tool, report_prompt_switch, log_before_model


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[
                career_assessment,
                course_recommendation,
                job_guidance,
                get_all_job_portraits,
                get_job_portrait,
                get_job_relation_graph,
                parse_resume,
                job_matching_analysis,
                generate_career_report,
                export_career_report,
                get_student_profile
            ],
            middleware=[monitor_tool, report_prompt_switch, log_before_model],
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            messages = chunk.get("messages", [])
            if messages:
                latest_message = messages[-1]
                if latest_message.content:
                    yield latest_message.content.strip() + "\n"

    def execute(self, query: str) -> str:
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        result = self.agent.invoke(input_dict, context={"report": False})
        messages = result.get("messages", [])
        if messages:
            latest_message = messages[-1]
            if latest_message.content:
                return latest_message.content
        return ""
