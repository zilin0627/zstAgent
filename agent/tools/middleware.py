from typing import Callable
from langchain.agents import AgentState
from langchain.agents.middleware import (
    wrap_tool_call,
    before_model,
    dynamic_prompt,
    ModelRequest,
    Runtime,
    ToolCallRequest,
)
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompt, load_system_prompt

# 工具执行的监控
@wrap_tool_call
def mointor_tool(
        request: ToolCallRequest,  # 工具调用请求
        handler: Callable[[ToolCallRequest], ToolMessage | Command],  # 工具调用处理函数
    ) -> ToolMessage | Command:
    logger.info(f"[mointor_tool]开始监控工具调用: {request.tool_call['name']}")
    logger.info(f"[mointor_tool]工具调用参数: {request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[mointor_tool]工具{request.tool_call['name']}调用成功")

        if request.tool_call['name'] == 'fill_context_for_report':
            logger.info(f"[mointor_tool]fill_context_for_report工具被调用, 注入上下文 report=True")
            request.runtime.context["report"] = True
        return result
    except Exception as e:
        logger.error(f"[mointor_tool]工具{request.tool_call['name']}调用失败: {e}")
        raise e  

 # 在模型调用前记录日志
@before_model
def log_before_model(
    state: AgentState,     # 整个agent的状态记录
    runtime: Runtime,      # 记录执行过程的上下文信息
):
    logger.info(f"[log_before_model]: 即将调用模型，带有{len(state['messages'])}条消息，消息如下：")
    logger.info(f"[log_before_model][{type(state['messages'][-1]).__name__}]: {state['messages'][-1].content.strip()}")
    
    return None

# 动态切换提示词
@dynamic_prompt      # 每一次生成提示词之前， 调用此函数
def report_prompt_switch(request: ModelRequest):
    is_report = request.runtime.context.get("report", False)
    if is_report:  # 如果上下文包含 report=True 标志， 则加载报告提示词
        return load_report_prompt()   # 加载报告提示词

    return load_system_prompt()  # 加载系统提示词
