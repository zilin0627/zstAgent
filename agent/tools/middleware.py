from typing import Any, Callable
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
from utils.prompt_loader import (
    load_guide_prompt,
    load_label_prompt,
    load_research_prompt,
    load_faq_prompt,
    load_system_prompt,
)


def _runtime_context_dict(raw_context: Any) -> dict:
    if isinstance(raw_context, dict):
        return raw_context
    return {}


# 工具执行的监控
@wrap_tool_call
def mointor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    tool_name = request.tool_call["name"]
    logger.info(f"[mointor_tool]开始监控工具调用: {tool_name}")
    logger.info(f"[mointor_tool]工具调用参数: {request.tool_call['args']}")

    context = _runtime_context_dict(request.runtime.context)
    trace = context.get("progress_trace")
    if isinstance(trace, list):
        trace.append({"type": "tool_start", "tool": tool_name, "args": request.tool_call["args"]})

    try:
        result = handler(request)
        logger.info(f"[mointor_tool]工具{tool_name}调用成功")

        if isinstance(trace, list):
            trace.append({"type": "tool_end", "tool": tool_name, "content": str(getattr(result, 'content', '') or '')[:1600]})

        if tool_name == "fill_context_for_report":
            logger.info("[mointor_tool]fill_context_for_report工具被调用, 注入上下文 report=True")
            context["report"] = True
            request.runtime.context = context
        return result
    except Exception as e:
        logger.error(f"[mointor_tool]工具{tool_name}调用失败: {e}")
        if isinstance(trace, list):
            trace.append({"type": "tool_error", "tool": tool_name, "content": str(e)})
        raise e


# 在模型调用前记录日志
@before_model
def log_before_model(
    state: AgentState,
    runtime: Runtime,
):
    logger.info(f"[log_before_model]: 即将调用模型，带有{len(state['messages'])}条消息，消息如下：")
    logger.info(f"[log_before_model][{type(state['messages'][-1]).__name__}]: {state['messages'][-1].content.strip()}")
    return None


# 动态切换提示词（按模式）
@dynamic_prompt
def mode_prompt_switch(request: ModelRequest):
    context = _runtime_context_dict(request.runtime.context)
    mode = context.get("mode", "guide")

    if mode == "guide":
        return load_guide_prompt()
    if mode == "label":
        return load_label_prompt()
    if mode == "research":
        return load_research_prompt()
    if mode == "faq":
        return load_faq_prompt()

    return load_system_prompt()
