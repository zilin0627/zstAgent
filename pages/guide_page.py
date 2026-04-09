import json

import streamlit as st


GUIDE_SAMPLE_QUESTIONS = [
    "侗族织绣纹样通常有哪些构成元素？",
    "几何纹样在侗族刺绣里常见吗？有什么含义？",
    "侗族织绣纹样在生活场景中一般怎么使用？",
    "想写一段展签：介绍某个典型纹样的要点（100-150字）",
    "请生成一组观众常见问题FAQ",
]

MODE_MAP = {
    "导览讲解": "guide",
    "展签文案": "label",
    "深度研究": "research",
    "FAQ生成": "faq",
}


def render_guide_sidebar(*, current_page: str, guide_page: str):
    if current_page != guide_page:
        st.caption("当前页面为模块入口展示区。切换到“智能导览”可继续使用原有问答能力。")
        return

    st.subheader("导览设置")
    mode_label = st.selectbox(
        "模式",
        options=list(MODE_MAP.keys()),
        index=0,
        key="guide_mode",
    )
    mode = MODE_MAP[mode_label]

    strategy_label = st.radio(
        "回答策略",
        options=["快速导览（直连RAG）", "智能导览（Agent）"],
        index=0,
        key="guide_strategy",
    )
    use_direct_rag = strategy_label == "快速导览（直连RAG）"
    allow_web = st.toggle("允许联网补充", value=False, disabled=use_direct_rag, key="guide_allow_web")
    if use_direct_rag:
        st.caption("快速导览模式下仅使用本地知识库，响应更快。")
        if mode != "guide":
            st.caption("当前仅“导览讲解”模式支持直连RAG，其它模式会自动切换为 Agent。")
    elif allow_web:
        st.caption("智能导览将优先本地检索，必要时再联网补充。")

    st.selectbox(
        "受众",
        options=["大众观众", "学生/入门", "专业观众"],
        index=0,
        key="guide_audience",
    )
    st.toggle("展示参考资料与出处", value=True, key="guide_citations")

    st.divider()
    st.caption("示例问题")
    for question in GUIDE_SAMPLE_QUESTIONS:
        if st.button(question, width="stretch"):
            st.session_state["preset_prompt"] = question


def render_guide_page(*, run_agent_request, run_direct_rag_request):
    st.title("文化导览")
    st.caption("优先使用预设问题和结果展示，让它更像导览机与展签助手，而不是聊天页面。")
    st.divider()

    preset_cols = st.columns(3, gap="large")
    for idx, question in enumerate(GUIDE_SAMPLE_QUESTIONS[:3]):
        with preset_cols[idx % 3]:
            if st.button(question, key=f"guide-preset-{idx}", width="stretch"):
                st.session_state["preset_prompt"] = question
                st.rerun()

    extra_cols = st.columns(2, gap="large")
    for idx, question in enumerate(GUIDE_SAMPLE_QUESTIONS[3:]):
        with extra_cols[idx % 2]:
            if st.button(question, key=f"guide-preset-extra-{idx}", width="stretch"):
                st.session_state["preset_prompt"] = question
                st.rerun()

    st.divider()

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

    prompt = st.chat_input("也可以直接输入你的问题")
    if not prompt:
        prompt = st.session_state.pop("preset_prompt", "")

    if not prompt:
        return

    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    mode_label = st.session_state.get("guide_mode", "导览讲解")
    mode = MODE_MAP[mode_label]
    strategy_label = st.session_state.get("guide_strategy", "快速导览（直连RAG）")
    use_direct_rag = strategy_label == "快速导览（直连RAG）"
    allow_web = st.session_state.get("guide_allow_web", False)
    audience = st.session_state.get("guide_audience", "大众观众")
    citations_enabled = st.session_state.get("guide_citations", True)
    use_agent = not use_direct_rag or mode != "guide"

    with st.spinner("思考中..."):
        if use_agent:
            answer, citations = run_agent_request(
                prompt,
                {
                    "mode": mode,
                    "audience": audience,
                    "citations_enabled": citations_enabled,
                    "allow_web": allow_web,
                },
            )
        else:
            answer, citations = run_direct_rag_request(prompt)
            if isinstance(citations, str):
                citations = json.loads(citations)

        if not citations_enabled:
            citations = None
        st.session_state["messages"].append(
            {"role": "assistant", "content": answer, "citations": citations}
        )
        st.rerun()
