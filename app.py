import json
import re
from json import JSONDecoder
import streamlit as st
from agent.react_agent import ReactAgent
from rag.rag_service import RagSummarizeService

def _extract_citations(text: str):
    """
    从模型输出中抽取引用区块：
    [[CITATIONS]]
    {...json...}
    [[/CITATIONS]]
    """
    if not text:
        return text, None

    start_tag = "[[CITATIONS]]"
    end_tag = "[[/CITATIONS]]"
    start = text.rfind(start_tag)
    end = text.rfind(end_tag)
    if start != -1 and end != -1 and end > start:
        json_part = text[start + len(start_tag) : end].strip()
        answer = (text[:start] + text[end + len(end_tag) :]).strip()
        try:
            data = json.loads(json_part)
            # 兼容：若 answer 为空，则优先取 JSON 中的 answer 字段
            if isinstance(data, dict) and not answer:
                answer = str(data.get("answer", "")).strip()
            return answer, data
        except Exception:
            # 解析失败则继续尝试“裸 JSON”回退解析
            pass

    # 回退兼容：扫描正文中任意 JSON 对象，提取包含 answer/citations 的 payload
    decoder = JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, end = decoder.raw_decode(text[i:])
            if isinstance(obj, dict) and "answer" in obj and "citations" in obj:
                prefix = text[:i].strip()
                answer = prefix if prefix else str(obj.get("answer", "")).strip()
                return answer, obj
        except Exception:
            continue

    # 默认：不包含可解析引用结构
    try:
        return text, None
    except Exception:
        # 解析失败则直接不展示引用，避免影响主回答
        return text, None

def _clean_answer_text(answer: str) -> str:
    """
    清洗模型正文中的工具回显噪音（例如 web_search 的 {"query":...,"results":[...]}）。
    """
    if not answer:
        return answer

    cleaned = answer

    # 去掉常见的 web_search 原始 JSON 回显
    cleaned = re.sub(
        r'\s*\{"query"\s*:\s*".*?"\s*,\s*"results"\s*:\s*\[.*?\]\}\s*',
        " ",
        cleaned,
        flags=re.S,
    )

    # 去掉 markdown 标题符号，保留更干净的小节标题
    cleaned = re.sub(r"(?m)^\s*#{1,6}\s*网络补充来源\s*$", "网络补充来源", cleaned)
    cleaned = cleaned.replace("###### 网络补充来源", "网络补充来源")
    cleaned = cleaned.replace("### 网络补充来源", "网络补充来源")
    cleaned = cleaned.replace("## 网络补充来源", "网络补充来源")

    # 删除常见的占位备注文案
    cleaned = re.sub(r"（?注：此为示意链接，实际搜索未返回具体结果）?", "", cleaned)

    # 去掉回答中重复回显的提问句（常见于“问题 + 答案”拼接）
    lines = [line.rstrip() for line in cleaned.splitlines()]
    normalized_lines = []
    last_meaningful = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            normalized_lines.append("")
            continue

        # 连续重复的整行内容只保留一次
        if stripped == last_meaningful:
            continue

        # 过滤“问句原样重复一遍”的回显
        if stripped.endswith("？") and last_meaningful == "":
            continue

        normalized_lines.append(stripped)
        last_meaningful = stripped

    cleaned = "\n".join(normalized_lines)

    # 压缩多余空白
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned

# 标题
st.title("侗族织绣纹样 · 非遗数字导览员")
st.divider()

if "rag_service" not in st.session_state:
    st.session_state.rag_service = RagSummarizeService()

with st.sidebar:
    st.subheader("导览设置")
    mode_label = st.selectbox(
        "模式",
        options=["导览讲解", "展签文案", "深度研究", "FAQ生成"],
        index=0,
    )
    mode_map = {"导览讲解": "guide", "展签文案": "label", "深度研究": "research", "FAQ生成": "faq"}
    mode = mode_map[mode_label]

    strategy_label = st.radio(
        "回答策略",
        options=["快速导览（直连RAG）", "智能导览（Agent）"],
        index=0,
    )
    use_direct_rag = strategy_label == "快速导览（直连RAG）"
    allow_web = st.toggle("允许联网补充", value=False, disabled=use_direct_rag)
    if use_direct_rag:
        st.caption("快速导览模式下仅使用本地知识库，响应更快。")
        if mode != "guide":
            st.caption("当前仅“导览讲解”模式支持直连RAG，其它模式会自动切换为 Agent。")
    elif allow_web:
        st.caption("智能导览将优先本地检索，必要时再联网补充。")

    audience = st.selectbox("受众", options=["大众观众", "学生/入门", "专业观众"], index=0)
    citations_enabled = st.toggle("展示参考资料与出处", value=True)

    st.divider()
    st.caption("示例问题")
    sample_questions = [
        "侗族织绣纹样通常有哪些构成元素？",
        "几何纹样在侗族刺绣里常见吗？有什么含义？",
        "侗族织绣纹样在生活场景中一般怎么使用？",
        "想写一段展签：介绍某个典型纹样的要点（100-150字）",
        "请生成一组观众常见问题FAQ",
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state["preset_prompt"] = q

if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message.get("content", ""))
        citations_payload = message.get("citations")
        citation_items = []
        if isinstance(citations_payload, dict):
            citation_items = citations_payload.get("citations", []) or []
        elif isinstance(citations_payload, list):
            citation_items = citations_payload
        if citation_items:
            with st.expander("参考资料与出处", expanded=False):
                for item in citation_items:
                    if not isinstance(item, dict):
                        continue
                    source = item.get("source", "unknown")
                    page = item.get("page", None)
                    snippet = item.get("snippet", "")
                    header = f"{item.get('index', '')}. {source}"
                    if page is not None:
                        header += f" (page {page})"
                    st.markdown(f"**{header}**")
                    st.write(snippet)
                st.caption("以上为检索到的关键片段，已做截断展示。")

# 用户提示词（兼容低版本 Streamlit：chat_input 不支持 value 参数）
prompt = st.chat_input()
if not prompt:
    prompt = st.session_state.pop("preset_prompt", "")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    use_agent = not use_direct_rag or mode != "guide"

    with st.spinner("思考中..."):
        if use_agent:
            response_message = []
            response_stream = st.session_state.agent.execute_stream(
                prompt,
                context={
                    "mode": mode,
                    "audience": audience,
                    "citations_enabled": citations_enabled,
                    "allow_web": allow_web,
                },
            )

            for chunk in response_stream:
                response_message.append(chunk)

            full_text = "".join(response_message).strip()
            answer, citations = _extract_citations(full_text)
        else:
            rag_payload_text = st.session_state.rag_service.rag_summarize_with_citations(prompt)
            citations = json.loads(rag_payload_text)
            answer = citations.get("answer", "") if isinstance(citations, dict) else ""

        answer = _clean_answer_text(answer.strip())
        if not answer:
            answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
        if not citations_enabled:
            citations = None
        st.session_state["messages"].append(
            {"role": "assistant", "content": answer, "citations": citations}
        )
        st.rerun()
            
           