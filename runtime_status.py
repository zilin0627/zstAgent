import streamlit as st


def render_runtime_status(status: dict | None):
    if not isinstance(status, dict):
        return

    summary = str(status.get("summary", "")).strip()
    if summary:
        st.info(summary)

    labels = []
    path = status.get("path")
    allow_web = bool(status.get("allow_web"))
    if path == "agent":
        labels.append(f"模式：{'Agent + 联网' if allow_web else 'Agent'}")
    elif path == "direct_rag":
        labels.append("模式：直连 RAG")

    labels.append(f"联网开关：{'开' if allow_web else '关'}")

    if path == "agent":
        if status.get("web_search_called"):
            labels.append(
                f"实际联网：已触发 web_search（{int(status.get('web_result_count', 0) or 0)} 条）"
            )
        else:
            labels.append("实际联网：未触发")
    else:
        labels.append("实际联网：未使用")

    if status.get("used_local_rag"):
        labels.append("本地知识库：已使用")

    retrieval_count = status.get("retrieval_count")
    if retrieval_count is not None:
        labels.append(f"检索片段：{retrieval_count}")

    confidence = status.get("confidence")
    if confidence:
        labels.append(f"置信度：{confidence}")

    st.caption("  ·  ".join(labels))

    thought_trace = status.get("thought_trace") or []
    if thought_trace:
        with st.expander("本轮调用过程", expanded=False):
            for step in thought_trace:
                st.markdown(f"- {step}")
