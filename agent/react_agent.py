from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from agent.tools.agent_tools import rag_summarize, fetch_exhibit, web_search
from agent.tools.middleware import mode_prompt_switch, mointor_tool, log_before_model

class ReactAgent:
    def __init__(self):
       shared_kwargs = {
           "model": chat_model,
           "system_prompt": load_system_prompt(),
           "middleware": [mode_prompt_switch, mointor_tool, log_before_model],
       }
       self.agent = create_agent(
           tools=[rag_summarize, fetch_exhibit, web_search],
           **shared_kwargs,
       )
       self.local_agent = create_agent(
           tools=[rag_summarize, fetch_exhibit],
           **shared_kwargs,
       )
    
    def execute_stream(self, query: str, context: dict | None = None):
        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        runtime_context = context or {"mode": "guide"}
        emitted_contents: set[str] = set()
        allow_web = bool(runtime_context.get("allow_web", True)) if isinstance(runtime_context, dict) else True
        runner = self.agent if allow_web else self.local_agent

        for chunk in runner.stream(input_dict, stream_mode="values", context=runtime_context):
            latest_message = chunk["messages"][-1]
            if not isinstance(latest_message, AIMessage):
                continue

            content = latest_message.content
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            else:
                content = str(content or "")

            content = content.strip()
            if not content or content in emitted_contents:
                continue

            emitted_contents.add(content)
            yield content + "\n"


if __name__ == "__main__":
    agent = ReactAgent()
    for chunk in agent.execute_stream("给我生成使用报告"):
        print(chunk, end="", flush=True)

       
