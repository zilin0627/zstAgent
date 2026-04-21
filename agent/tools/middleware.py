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


def _build_runtime_instruction(context: dict) -> str:
    mode = str(context.get("mode", "guide") or "guide")
    allow_web = bool(context.get("allow_web", False))
    citations_enabled = bool(context.get("citations_enabled", True))
    audience = str(context.get("audience", "") or "").strip()

    instruction_lines = [
        "\n\n### 本轮运行时约束（强制）",
        f"- 当前模式：{mode}",
        f"- 当前受众：{audience or '未指定'}",
        f"- 引用展示：{'开启' if citations_enabled else '关闭'}",
    ]

    if allow_web:
        instruction_lines.extend(
            [
                "- 本轮已开启联网补充能力，必须使用 Agent 路径，不要退化成只做纯本地直答。",
                "- 回答前应优先调用 rag_summarize 获取本地资料；若用户明确要求外部信息、最新信息、链接/官网，或本地资料不足以支撑回答，应继续调用 web_search 补充。",
                "- 当问题属于研究、设计转化、方案提案、外部背景补充等较复杂场景时，不要忽略联网开关；在确有必要时主动调用 web_search。",
                "- 联网资料只能作为补充，不能替代本地资料证据。",
            ]
        )
    else:
        instruction_lines.extend(
            [
                "- 本轮未开启联网补充，只能使用本地资料与本地工具。",
                "- 若需要知识依据，应优先调用 rag_summarize；不要调用 web_search。",
            ]
        )

    return "\n".join(instruction_lines)


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


@before_model
def log_before_model(
    state: AgentState,
    runtime: Runtime,
):
    logger.info(f"[log_before_model]: 即将调用模型，带有{len(state['messages'])}条消息，消息如下：")
    logger.info(f"[log_before_model][{type(state['messages'][-1]).__name__}]: {state['messages'][-1].content.strip()}")
    return None


@dynamic_prompt
def mode_prompt_switch(request: ModelRequest):
    context = _runtime_context_dict(request.runtime.context)
    mode = context.get("mode", "guide")

    if mode == "guide":
        base_prompt = load_guide_prompt()
    elif mode == "label":
        base_prompt = load_label_prompt()
    elif mode == "research":
        base_prompt = load_research_prompt()
    elif mode == "faq":
        base_prompt = load_faq_prompt()
    else:
        base_prompt = load_system_prompt()

    return base_prompt + _build_runtime_instruction(context)

