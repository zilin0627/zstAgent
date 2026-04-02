from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from agent.tools.agent_tools import (get_user_location, get_user_id, get_current_month, rag_summarize,
                                      fetch_external_data, fill_context_for_report, get_weather)
from agent.tools.middleware import report_prompt_switch, mointor_tool, log_before_model

class ReactAgent:
    def __init__(self):
       self.agent = create_agent(
           model=chat_model,
           system_prompt=load_system_prompt(),
           tools=[rag_summarize, fetch_external_data, fill_context_for_report,
                   get_user_location, get_user_id, get_current_month, get_weather],
           middleware=[report_prompt_switch, mointor_tool, log_before_model],
       )
    
    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        # context={"report": False}   设置上下文 默认不开启报告模式
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"


if __name__ == "__main__":
    agent = ReactAgent()
    for chunk in agent.execute_stream("给我生成使用报告"):
        print(chunk, end="", flush=True)

       
