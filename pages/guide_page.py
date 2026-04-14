import json

import streamlit as st


GUIDE_SAMPLE_QUESTIONS = [
    "侗族织绣纹样通常有哪些构成元素？",
    "动物纹样具体有哪些？请尽量列举文献里常见的名称",
    "八菜一汤具体是什么纹样？它有什么寓意？",
    "几何纹样在侗族刺绣里常见吗？有什么含义？",
    "侗族织绣纹样在生活场景中一般怎么使用？",
]

MODE_MAP = {
    "导览讲解": "guide",
    "展签文案": "label",
    "深度研究": "research",
    "FAQ生成": "faq",
}

SIMPLE_FACT_MARKERS = [
    "是什么", "有哪些", "哪几类", "构成", "元素", "特点", "特征", "寓意", "含义", "象征", "来源", "区别",
]


def _should_prefer_direct_rag(prompt: str, mode: str, allow_web: bool) -> bool:
    if allow_web or mode != "guide":
        return False

    text = str(prompt or "").strip()
    if not text:
        return False

    if any(marker in text for marker in ["设计", "方案", "海报", "包装", "课程", "展签", "FAQ", "策划"]):
        return False

    return any(marker in text for marker in SIMPLE_FACT_MARKERS)


def _build_contextual_prompt(prompt: str) -> str:
    history = st.session_state.get("messages", [])
    if not history:
        return prompt

    recent_messages = history[-6:]
    history_lines = []
    for item in recent_messages:
        role = "用户" if item.get("role") == "user" else "助手"
        content = str(item.get("content", "")).strip()
        if content:
            history_lines.append(f"{role}：{content}")

    if not history_lines:
        return prompt

    return (
        "以下是本轮导览中最近的对话上下文，请在回答当前问题时适度继承：\n"
        + "\n".join(history_lines)
        + f"\n\n当前问题：{prompt}"
    )


def _delete_message_round(index: int):
    messages = st.session_state.get("messages", [])
    start = index
    end = index + 1
    if index > 0 and messages[index].get("role") == "assistant" and messages[index - 1].get("role") == "user":
        start = index - 1
    st.session_state["messages"] = messages[:start] + messages[end:]


def _render_citation_expander(citations_payload):
    citation_items = []
    if isinstance(citations_payload, dict):
        citation_items = citations_payload.get("citations", []) or []
    elif isinstance(citations_payload, list):
        citation_items = citations_payload

    if not citation_items:
        return

    with st.expander("参考资料与出处", expanded=False):
        for item in citation_items:
            if not isinstance(item, dict):
                continue
            source = item.get("source", "unknown")
            page = item.get("page", None)
            snippet = item.get("snippet", "")
            url = item.get("url", "")
            if url and not url.startswith(("http://", "https://")):
                url = ""
            header = f"{item.get('index', '')}. {source}"
            if page is not None:
                header += f" (page {page})"
            st.markdown(f"**{header}**")
            if snippet:
                st.write(snippet)
            if url:
                st.markdown(f"网页链接：[{url}]({url})")
        st.caption("以上为检索到的关键片段，已做截断展示。若启用了联网补充，网页链接也会在这里显示。")


def _render_message_history():
    messages = st.session_state.get("messages", [])
    if not messages:
        st.info("你可以先点击下方示例问题，也可以直接输入一个关于侗绣纹样的问题。")
        return

    latest_pair = messages[-2:] if len(messages) >= 2 else messages
    older_messages = messages[:-2] if len(messages) >= 2 else []

    st.markdown("### 当前导览结果")
    delete_index = None
    for idx, message in enumerate(latest_pair, start=max(len(messages) - len(latest_pair), 0)):
        with st.chat_message(message["role"]):
            notice = message.get("system_notice")
            if notice and isinstance(notice, dict):
                st.info(str(notice.get("message", "")).strip())
            top_cols = st.columns([0.88, 0.12], gap="small")
            with top_cols[0]:
                st.write(message.get("content", ""))
            with top_cols[1]:
                if message.get("role") == "assistant":
                    if st.button("删除这轮", key=f"guide-delete-round-{idx}", use_container_width=True):
                        delete_index = idx
            _render_citation_expander(message.get("citations"))

    if older_messages:
        with st.expander(f"历史导览记录（{len(older_messages)} 条）", expanded=False):
            for idx, message in enumerate(older_messages):
                with st.chat_message(message["role"]):
                    notice = message.get("system_notice")
                    if notice and isinstance(notice, dict):
                        st.info(str(notice.get("message", "")).strip())
                    top_cols = st.columns([0.88, 0.12], gap="small")
                    with top_cols[0]:
                        st.write(message.get("content", ""))
                    with top_cols[1]:
                        if message.get("role") == "assistant":
                            if st.button("删除这轮", key=f"guide-history-delete-{idx}", use_container_width=True):
                                delete_index = idx
                    _render_citation_expander(message.get("citations"))

    if delete_index is not None:
        _delete_message_round(delete_index)
        st.rerun()


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
        index=1,
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
    else:
        st.caption("当前为智能导览，但仍只使用本地资料，适合做稳妥讲解或展签草稿。")

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
        if st.button(question, key=f"guide-sidebar-sample-{question}", use_container_width=True):
            st.session_state["preset_prompt"] = question
            st.rerun()


def render_guide_page(*, run_agent_request_streaming, run_direct_rag_request):
    st.title("文化导览")
    st.caption("把侗绣纹样问题组织成导览讲解、展签文案、深度研究和 FAQ 生成，更像导览台而不是通用聊天框。")
    st.divider()

    intro_left, intro_right = st.columns([1.05, 0.95], gap="large")
    with intro_left:
        st.markdown("### 这页适合做什么")
        st.markdown("- 快速理解某类纹样的构成特点、寓意和使用场景")
        st.markdown("- 把知识问答转成展签文案、FAQ 或研究型说明")
        st.markdown("- 结合本地知识库做更可追溯的讲解，而不是只给一段泛泛回答")
    with intro_right:
        st.info("推荐优先点击示例问题进入，再根据结果继续追问；这样更像真实导览流程。")
        action_cols = st.columns(2, gap="medium")
        with action_cols[0]:
            st.metric("当前入口", "智能导览台")
        with action_cols[1]:
            if st.button("清空全部对话", key="guide-clear-all", use_container_width=True):
                st.session_state["messages"] = []
                st.rerun()

    st.divider()
    st.markdown("### 常用导览入口")
    preset_cols = st.columns(3, gap="large")
    for idx, question in enumerate(GUIDE_SAMPLE_QUESTIONS[:3]):
        with preset_cols[idx % 3]:
            if st.button(question, key=f"guide-preset-{idx}", use_container_width=True):
                st.session_state["preset_prompt"] = question
                st.rerun()

    extra_cols = st.columns(2, gap="large")
    for idx, question in enumerate(GUIDE_SAMPLE_QUESTIONS[3:]):
        with extra_cols[idx % 2]:
            if st.button(question, key=f"guide-preset-extra-{idx}", use_container_width=True):
                st.session_state["preset_prompt"] = question
                st.rerun()

    st.divider()
    content_left, content_right = st.columns([1.2, 0.8], gap="large")

    with content_left:
        _render_message_history()

    with content_right:
        st.markdown("### 当前导览状态")
        st.markdown(f"- 模式：{st.session_state.get('guide_mode', '导览讲解')}")
        st.markdown(f"- 策略：{st.session_state.get('guide_strategy', '智能导览（Agent）')}")
        st.markdown(f"- 受众：{st.session_state.get('guide_audience', '大众观众')}")
        st.markdown(f"- 参考资料：{'开启' if st.session_state.get('guide_citations', True) else '关闭'}")
        st.markdown(f"- 联网补充：{'开启' if st.session_state.get('guide_allow_web', False) else '关闭'}")
        st.caption("如需调整模式和回答策略，请在侧边栏统一修改。")

        st.markdown("### 推荐提问方式")
        st.markdown("- 不知道专业名称也没关系，可以直接问‘常见动物有哪些’‘这种纹样一般什么意思’。")
        st.markdown("- 如果想要列举，请直接说‘请列举具体名称’或‘请尽量用文献里的原词回答’。")
        st.markdown("- 如果你只知道模糊印象，也可以问‘有一个像八菜一汤的纹样，它具体是什么’。")
        st.markdown("- 如果要展签文案，直接说明字数或使用场景。")
        st.markdown("- 如果要研究说明，可以明确说‘请从来源、构成、寓意来讲’。")

    prompt = st.chat_input("也可以直接输入你的问题")
    if not prompt:
        prompt = st.session_state.pop("preset_prompt", "")

    if not prompt:
        return

    st.session_state["messages"].append({"role": "user", "content": prompt})

    mode_label = st.session_state.get("guide_mode", "导览讲解")
    mode = MODE_MAP[mode_label]
    strategy_label = st.session_state.get("guide_strategy", "快速导览（直连RAG）")
    use_direct_rag = strategy_label == "快速导览（直连RAG）"
    allow_web = st.session_state.get("guide_allow_web", False)
    audience = st.session_state.get("guide_audience", "大众观众")
    citations_enabled = st.session_state.get("guide_citations", True)
    if not use_direct_rag and _should_prefer_direct_rag(prompt, mode, allow_web):
        use_direct_rag = True
    use_agent = not use_direct_rag or mode != "guide"
    contextual_prompt = _build_contextual_prompt(prompt)

    with content_left:
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            thought_placeholder = st.empty()
            answer_placeholder = st.empty()
            system_notice = None

            if use_agent:
                if allow_web:
                    thought_placeholder.info("正在结合上下文分析问题，先检索本地资料；若不足，再补充联网公开信息…")
                else:
                    thought_placeholder.info("正在结合上下文分析问题并检索本地资料，请稍候…")
                answer, citations, system_notice = run_agent_request_streaming(
                    contextual_prompt,
                    {
                        "mode": mode,
                        "audience": audience,
                        "citations_enabled": citations_enabled,
                        "allow_web": allow_web,
                    },
                    answer_placeholder,
                    thought_placeholder,
                )
                if system_notice and isinstance(system_notice, dict):
                    st.info(str(system_notice.get("message", "")).strip())
            else:
                thought_placeholder.info("正在优先使用直连知识库回答，以减少等待时间…")
                with st.spinner("思考中..."):
                    answer, citations, _, _, system_notice = run_direct_rag_request(prompt)
                    if isinstance(citations, str):
                        citations = json.loads(citations)
                thought_placeholder.success("已完成检索与生成")
                if system_notice and isinstance(system_notice, dict):
                    st.info(str(system_notice.get("message", "")).strip())
                answer_placeholder.markdown(answer)

            if not citations_enabled:
                citations = None

        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": answer,
                "citations": citations,
                "system_notice": system_notice,
            }
        )
        st.rerun()
