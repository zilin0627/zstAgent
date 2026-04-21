import json
import requests
import streamlit as st

from runtime_status import render_runtime_status


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


def _save_guide_settings(mode_label, strategy_label, allow_web, audience, citations_enabled):
    st.session_state["guide_mode"] = mode_label
    st.session_state["guide_strategy"] = strategy_label
    st.session_state["guide_allow_web"] = allow_web
    st.session_state["guide_audience"] = audience
    st.session_state["guide_citations"] = citations_enabled


def render_guide_sidebar(*, current_page, guide_page):
    if current_page != guide_page:
        st.caption("当前页面为模块入口展示区。切换到“智能导览”可继续使用原有问答能力。")
        return

    st.subheader("导览设置")
    mode_options = list(MODE_MAP.keys())
    strategy_options = ["快速导览（直连RAG）", "智能导览（Agent）"]
    audience_options = ["大众观众", "学生/入门", "专业观众"]

    mode_label = st.selectbox(
        "模式",
        options=mode_options,
        index=mode_options.index(st.session_state.get("guide_mode", "导览讲解"))
        if st.session_state.get("guide_mode", "导览讲解") in mode_options
        else 0,
        key="guide_mode_selector",
    )

    # 展签文案/深度研究/FAQ生成 必须走 Agent，不允许选直连RAG
    mode_forces_agent = mode_label != "导览讲解"

    if mode_forces_agent:
        st.session_state["guide_strategy_selector"] = "智能导览（Agent）"

    strategy_label = st.radio(
        "回答策略",
        options=strategy_options,
        index=1 if mode_forces_agent else (
            strategy_options.index(st.session_state.get("guide_strategy", "快速导览（直连RAG）"))
            if st.session_state.get("guide_strategy", "快速导览（直连RAG）") in strategy_options
            else 0
        ),
        disabled=mode_forces_agent,
        key="guide_strategy_selector",
    )
    if mode_forces_agent:
        st.caption(mode_label + " 模式固定走 Agent，策略选择不起效。")
        strategy_label = "智能导览（Agent）"

    current_use_direct_rag = strategy_label == "快速导览（直连RAG）"
    saved_allow_web = st.session_state.get("guide_allow_web", False)
    effective_allow_web = False if current_use_direct_rag else saved_allow_web
    if current_use_direct_rag and saved_allow_web:
        st.session_state["guide_allow_web"] = False

    allow_web = st.toggle(
        "允许联网补充",
        value=effective_allow_web,
        disabled=current_use_direct_rag,
        key="guide_allow_web_toggle",
    )

    # 受众只对导览讲解有效，其他模式格式固定
    audience_active = not mode_forces_agent
    audience = st.selectbox(
        "受众",
        options=audience_options,
        index=audience_options.index(st.session_state.get("guide_audience", "大众观众"))
        if st.session_state.get("guide_audience", "大众观众") in audience_options
        else 0,
        disabled=not audience_active,
        key="guide_audience_selector",
    )
    if not audience_active:
        st.caption(mode_label + " 模式输出格式固定，受众设置不起效。")

    citations_enabled = st.toggle(
        "展示参考资料与出处",
        value=st.session_state.get("guide_citations", True),
        key="guide_citations_toggle",
    )

    saved_settings = (
        st.session_state.get("guide_mode", "导览讲解"),
        st.session_state.get("guide_strategy", "快速导览（直连RAG）"),
        st.session_state.get("guide_allow_web", False),
        st.session_state.get("guide_audience", "大众观众"),
        st.session_state.get("guide_citations", True),
    )
    current_settings = (
        mode_label,
        strategy_label,
        False if current_use_direct_rag else allow_web,
        audience,
        citations_enabled,
    )
    if current_settings != saved_settings:
        _save_guide_settings(*current_settings)

    current_allow_web = False if current_use_direct_rag else allow_web

    if current_use_direct_rag:
        st.caption("当前为直连 RAG，联网补充已禁用。")
    elif current_allow_web:
        st.caption("当前为 Agent + 联网：优先本地检索，必要时联网补充。")
    else:
        st.caption("当前为 Agent 本地模式：仅使用本地资料。")

    st.divider()
    st.caption("示例问题")
    for q in GUIDE_SAMPLE_QUESTIONS:
        if st.button(q, key=f"sidebar_sample_{q}", use_container_width=True):
            st.session_state["preset_prompt"] = q
            st.rerun()


def _render_message_block(message, highlight_latest=False):
    role = message.get("role", "assistant")
    content = message.get("content", "")
    citations_payload = message.get("citations")
    runtime_status = message.get("runtime_status") if role == "assistant" else None
    citation_items = []
    if isinstance(citations_payload, dict):
        citation_items = citations_payload.get("citations", []) or []
    elif isinstance(citations_payload, list):
        citation_items = citations_payload

    if role == "user":
        st.markdown(f'<div class="user-bubble">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-bubble">{content}</div>', unsafe_allow_html=True)
        render_runtime_status(runtime_status)

    if citation_items:
        with st.expander("参考资料", expanded=False):
            for item in citation_items:
                if not isinstance(item, dict):
                    continue
                source = item.get("source", "unknown")
                page = item.get("page")
                snippet = item.get("snippet", "")
                url = item.get("url")
                header = f"{item.get('index', '')}. {source}"
                if page is not None:
                    header += f" (p.{page})"
                if url:
                    st.markdown(f"**{header}** [链接]({url})")
                else:
                    st.markdown(f"**{header}**")
                st.write(snippet)
            st.caption("以上为检索到的关键片段。")


def render_guide_page(*, run_agent_request_streaming, run_direct_rag_request):
    st.title("文化导览")
    st.caption("围绕侗绣纹样做讲解、展签转译与工艺解释")

    # 当前设置摘要
    mode_label = st.session_state.get("guide_mode", "导览讲解")
    strategy_label = st.session_state.get("guide_strategy", "快速导览（直连RAG）")
    audience = st.session_state.get("guide_audience", "大众观众")
    citations_on = st.session_state.get("guide_citations", True)
    web_on = st.session_state.get("guide_allow_web", False)

    status_text = f"模式：{mode_label}  ·  策略：{strategy_label}  ·  受众：{audience}"
    if citations_on:
        status_text += "  ·  显示引用"
    if web_on:
        status_text += "  ·  可联网"
    st.caption(status_text)
    st.divider()

    # 示例问题
    row1 = st.columns(3)
    for i, q in enumerate(GUIDE_SAMPLE_QUESTIONS[:3]):
        with row1[i]:
            if st.button(q, key=f"preset_{i}", use_container_width=True):
                st.session_state["preset_prompt"] = q
                st.rerun()
    row2 = st.columns(2)
    for i, q in enumerate(GUIDE_SAMPLE_QUESTIONS[3:]):
        with row2[i]:
            if st.button(q, key=f"preset_extra_{i}", use_container_width=True):
                st.session_state["preset_prompt"] = q
                st.rerun()

    st.divider()

    left, right = st.columns([3, 1])

    with left:
        messages = st.session_state.get("messages", [])
        if not messages:
            st.info("点击上方问题或直接输入开始对话")
        else:
            show_count = min(6, len(messages))
            for msg in messages[-show_count:]:
                _render_message_block(msg)
            if len(messages) > show_count:
                with st.expander(f"更早的对话（{len(messages) - show_count} 条）"):
                    for msg in messages[:-show_count]:
                        _render_message_block(msg)

    with right:
        if st.button("清空对话", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()
        st.caption("设置请去左侧边栏")

    prompt = st.chat_input("输入问题")
    if not prompt:
        prompt = st.session_state.pop("preset_prompt", "")

    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state["messages"].append({"role": "user", "content": prompt})

        mode = MODE_MAP[mode_label]
        use_direct = strategy_label == "快速导览（直连RAG）"
        use_agent = not use_direct or mode != "guide"

        with st.spinner("稍等..."):
            placeholder = st.empty()
            thought_placeholder = st.empty()

            try:
                if use_agent:
                    answer, citations, _ = run_agent_request_streaming(
                        prompt,
                        {
                            "mode": mode,
                            "audience": audience,
                            "citations_enabled": citations_on,
                            "allow_web": web_on,
                        },
                        placeholder,
                        thought_placeholder,
                    )
                else:
                    answer, citations, _, _, _ = run_direct_rag_request(prompt)
                    placeholder.markdown(answer)
                    thought_placeholder.empty()
            except Exception:
                answer, citations = "服务暂时不可用，请稍后重试。", None
                placeholder.markdown(answer)

            runtime_status = st.session_state.get("_last_runtime_status")
            if not citations_on:
                citations = None
            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                    "runtime_status": runtime_status,
                }
            )
            st.rerun()