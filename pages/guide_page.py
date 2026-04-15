import json
import requests
import streamlit as st

from pages.runtime_status import render_runtime_status


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
        submitted = st.form_submit_button("应用设置", use_container_width=True)

    if submitted:
        _save_guide_settings(mode_label, strategy_label, allow_web, audience, citations_enabled)
        st.rerun()

    current_mode = st.session_state.get("guide_mode", default_mode)
    current_strategy = st.session_state.get("guide_strategy", default_strategy)
    current_use_direct_rag = current_strategy == "快速导览（直连RAG）"
    current_allow_web = st.session_state.get("guide_allow_web", default_allow_web)

    if current_use_direct_rag:
        st.caption("快速模式仅用本地知识库，联网开关不生效。")
        if MODE_MAP[current_mode] != "guide":
            st.caption("当前模式需走 Agent。")
    elif current_allow_web:
        st.caption("优先本地检索，必要时联网。")
    else:
        st.caption("仅用本地资料。")

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