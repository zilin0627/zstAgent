import json

import requests
import streamlit as st


GUIDE_SAMPLE_QUESTIONS = [
    "侗绣里常见的典型纹样有哪些？各自最容易辨认的特点是什么？",
    "如果只看图案构成，怎样快速分辨侗绣里的龙纹、鸟纹和花纹？",
    "侗绣纹样常见在哪些服饰或绣片位置？这些位置会影响图案组织吗？",
    "请写一段面向观众的侗绣纹样展签，重点介绍构图与工艺特点（100-150字）",
    "请围绕侗绣纹样生成一组观众常见问题 FAQ",
]

MODE_MAP = {
    "导览讲解": "guide",
    "展签文案": "label",
    "深度研究": "research",
    "FAQ生成": "faq",
}


def _save_guide_settings(mode_label: str, strategy_label: str, allow_web: bool, audience: str, citations_enabled: bool):
    st.session_state["guide_mode"] = mode_label
    st.session_state["guide_strategy"] = strategy_label
    st.session_state["guide_allow_web"] = allow_web
    st.session_state["guide_audience"] = audience
    st.session_state["guide_citations"] = citations_enabled


def render_guide_sidebar(*, current_page: str, guide_page: str):
    if current_page != guide_page:
        st.caption("当前页面为模块入口展示区。切换到“智能导览”可继续使用原有问答能力。")
        return

    st.subheader("导览设置")
    mode_options = list(MODE_MAP.keys())
    strategy_options = ["快速导览（直连RAG）", "智能导览（Agent）"]
    audience_options = ["大众观众", "学生/入门", "专业观众"]

    default_mode = st.session_state.get("guide_mode", "导览讲解")
    default_strategy = st.session_state.get("guide_strategy", "快速导览（直连RAG）")
    default_allow_web = st.session_state.get("guide_allow_web", False)
    default_audience = st.session_state.get("guide_audience", "大众观众")
    default_citations = st.session_state.get("guide_citations", True)

    with st.form("guide_settings_form", clear_on_submit=False):
        mode_label = st.selectbox(
            "模式",
            options=mode_options,
            index=mode_options.index(default_mode) if default_mode in mode_options else 0,
        )
        strategy_label = st.radio(
            "回答策略",
            options=strategy_options,
            index=strategy_options.index(default_strategy) if default_strategy in strategy_options else 0,
        )
        use_direct_rag = strategy_label == "快速导览（直连RAG）"
        allow_web = st.toggle("允许联网补充", value=default_allow_web)
        audience = st.selectbox(
            "受众",
            options=audience_options,
            index=audience_options.index(default_audience) if default_audience in audience_options else 0,
        )
        citations_enabled = st.toggle("展示参考资料与出处", value=default_citations)
        submitted = st.form_submit_button("应用导览设置", use_container_width=True)

    if submitted:
        _save_guide_settings(mode_label, strategy_label, allow_web, audience, citations_enabled)
        st.rerun()

    current_mode = st.session_state.get("guide_mode", default_mode)
    current_strategy = st.session_state.get("guide_strategy", default_strategy)
    current_use_direct_rag = current_strategy == "快速导览（直连RAG）"
    current_allow_web = st.session_state.get("guide_allow_web", default_allow_web)

    if current_use_direct_rag:
        st.caption("快速导览模式下仅使用本地知识库，响应更快；即使开启‘允许联网补充’，该设置在此模式下也不会生效。")
        if MODE_MAP[current_mode] != "guide":
            st.caption("当前仅“导览讲解”模式支持直连RAG，其它模式会自动切换为 Agent。")
    elif current_allow_web:
        st.caption("智能导览将优先本地检索，必要时再联网补充。")
    else:
        st.caption("当前为智能导览，但仍只使用本地资料；如需联网补充，可打开上方开关后应用设置。")

    st.divider()
    st.caption("示例问题")
    for question in GUIDE_SAMPLE_QUESTIONS:
        if st.button(question, key=f"guide-sidebar-sample-{question}", use_container_width=True):
            st.session_state["preset_prompt"] = question
            st.rerun()


def _render_message_block(message: dict, *, highlight_latest: bool):
    role = message.get("role", "assistant")
    content = message.get("content", "")
    citations_payload = message.get("citations")
    citation_items = []
    if isinstance(citations_payload, dict):
        citation_items = citations_payload.get("citations", []) or []
    elif isinstance(citations_payload, list):
        citation_items = citations_payload

    if highlight_latest and role == "assistant":
        st.markdown("#### 最新导览结果")
        st.write(content)
    else:
        with st.chat_message(role):
            st.write(content)

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
            st.caption("以上为检索到的关键片段。")



def render_guide_page(*, run_agent_request, run_direct_rag_request):
    st.title("文化导览")
    st.caption("围绕侗绣纹样做讲解、展签转译与工艺解释，尽量让回答更聚焦纹样本身。")
    st.divider()

    preset_top = st.columns(3, gap="large")
    for idx, question in enumerate(GUIDE_SAMPLE_QUESTIONS[:3]):
        with preset_top[idx % 3]:
            if st.button(question, key=f"guide-preset-{idx}", use_container_width=True):
                st.session_state["preset_prompt"] = question
                st.rerun()

    preset_bottom = st.columns(2, gap="large")
    for idx, question in enumerate(GUIDE_SAMPLE_QUESTIONS[3:]):
        with preset_bottom[idx % 2]:
            if st.button(question, key=f"guide-preset-extra-{idx}", use_container_width=True):
                st.session_state["preset_prompt"] = question
                st.rerun()

    st.divider()

    history_col, helper_col = st.columns([1.25, 0.75], gap="large")
    messages = st.session_state["messages"]
    latest_pair = messages[-2:] if len(messages) >= 2 else messages
    older_messages = messages[:-2] if len(messages) >= 2 else []

    with history_col:
        if latest_pair:
            for message in latest_pair:
                _render_message_block(message, highlight_latest=(message is latest_pair[-1]))
        else:
            st.info("你可以先点击上方示例问题，或直接输入一个关于侗绣纹样的问题。")

        if older_messages:
            with st.expander(f"历史问答（{len(older_messages)} 条）", expanded=False):
                for message in older_messages:
                    _render_message_block(message, highlight_latest=False)

    with helper_col:
        st.markdown("### 当前导览状态")
        st.markdown(f"- 模式：{st.session_state.get('guide_mode', '导览讲解')}")
        st.markdown(f"- 策略：{st.session_state.get('guide_strategy', '快速导览（直连RAG）')}")
        st.markdown(f"- 受众：{st.session_state.get('guide_audience', '大众观众')}")
        st.markdown(f"- 参考资料：{'开启' if st.session_state.get('guide_citations', True) else '关闭'}")
        st.caption("如需调整，请在侧边栏统一修改设置，再提交问题。")
        if st.button("清空当前对话", key="guide-clear-history", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

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
        try:
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
                answer, citations = run_direct_rag_request(
                    prompt,
                    {
                        "mode": mode,
                        "audience": audience,
                        "citations_enabled": citations_enabled,
                    },
                )
                if isinstance(citations, str):
                    citations = json.loads(citations)
        except requests.exceptions.RequestException:
            answer, citations = "当前连接不稳定，请稍后重试。", None

        if not citations_enabled:
            citations = None
        st.session_state["messages"].append({"role": "assistant", "content": answer, "citations": citations})
        st.rerun()
