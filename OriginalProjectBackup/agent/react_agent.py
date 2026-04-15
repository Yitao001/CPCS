from langchain.agents import create_agent
from oauthlib.uri_validate import query

from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize,get_weather,get_user_id,get_current_month,get_user_location,
                                     fetch_external_data,fill_context_for_report,generate_persona,get_chat_history,generate_persona_from_db)
from agent.tools.middleware import monitor_tool,report_prompt_switch,log_before_model

class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            system_prompt = load_system_prompts(),
            tools = [rag_summarize,get_weather,get_user_id,get_current_month,
                   get_user_location,fetch_external_data,fill_context_for_report,generate_persona,get_chat_history,generate_persona_from_db],
            middleware = [monitor_tool,report_prompt_switch,log_before_model],
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages":[
                {"role": "user", "content": query},
            ]
        }

        # 第三个参数context就是上线文runtime中的信息，就是我们做提示词切换的标记
        for chunk in self.agent.stream(input_dict,stream_mode="values",context={"report":False}):
            messages = chunk.get("messages", [])
            if messages:
                latest_message = messages[-1]
                if latest_message.content:
                    yield latest_message.content.strip() + "\n"
