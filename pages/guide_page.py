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
    "FAQ生成":  "faq",
}

_MODE_COLOR = {
    "导览讲解": "#1e3a5f",
    "展签文案": "#1a5c4f",
    "深度研究": "#3d2a5c",
    "FAQ生成":  "#7c4a0a",
}


def _inject_css():
    st.markdown(
        """
        <style>
        /* 对话泡泡 */
        .user-bubble {
            background: #eef2fb;
            border-left: 3px solid #1e3a5f;
            border-radius: 4px 12px 12px 12px;
            padding: 10px 16px;
            margin: 8px 0;
            color: #1a2540;
            font-size: 14px;
            line-height: 1.65;
        }
        .assistant-bubble {
            background: #fdfcf9;
            border: 1px solid #e5ddd0;
            border-left: 3px solid #b8960f;
            border-radius: 12px 4px 12px 12px;
            padding: 10px 16px;
            margin: 8px 0;
            color: #1a1a1a;
            font-size: 14px;
            line-height: 1.75;
        }
        /* 模式状态徽章 */
        .status-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
            padding: 6px 0 2px;
        }
        .s-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            background: rgba(0,0,0,0.05);
            color: #3a3a3a;
            border: 1px solid rgba(0,0,0,0.08);
        }
        .s-badge-primary {
            background: rgba(30,58,95,0.1);
            color: #1e3a5f;
            border-color: rgba(30,58,95,0.18);
            font-weight: 600;
        }
        /* 示例问题按钮 */
        div[data-testid="stHorizontalBlock"]
            div[data-testid="stButton"] button {
            background: #f8f4ee;
            border: 1px solid #d8cbb8;
            color: #3a2e20;
            border-radius: 6px;
            font-size: 12px;
            padding: 8px 10px;
            white-space: normal;
            text-align: left;
            line-height: 1.45;
            min-height: 56px;
            transition: background 0.12s, border-color 0.12s, color 0.12s;
        }
        div[data-testid="stHorizontalBlock"]
            div[data-testid="stButton"] button:hover {
            background: #1e3a5f;
            border-color: #1e3a5f;
            color: #fff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_status_bar(mode_label, strategy_label, audience, citations_on, web_on):
    color = _MODE_COLOR.get(mode_label, "#444")
    parts = [
        f'<span class="s-badge s-badge-primary" style="background:{color}18;color:{color};border-color:{color}30;">{mode_label}</span>',
        f'<span class="s-badge">{strategy_label}</span>',
        f'<span class="s-badge">{audience}</span>',
    ]
    if citations_on:
        parts.append('<span class="s-badge">引用开启</span>')
    if web_on:
        parts.append('<span class="s-badge">联网补充</span>')
    st.markdown(
        f'<div class="status-bar">{"".join(parts)}</div>',
        unsafe_allow_html=True,
    )


def _save_guide_settings(mode_label, strategy_label, allow_web, audience, citations_enabled):
    st.session_state["guide_mode"]      = mode_label
    st.session_state["guide_strategy"]  = strategy_label
    st.session_state["guide_allow_web"] = allow_web
    st.session_state["guide_audience"]  = audience
    st.session_state["guide_citations"] = citations_enabled


def render_guide_sidebar(*, current_page, guide_page):
    if current_page != guide_page:
        st.caption('当前页面为模块入口展示区。切换到「智能导览」可继续使用原有问答能力。')
        return

    st.subheader("导览设置")
    mode_options     = list(MODE_MAP.keys())
    strategy_options = ["快速导览（直连RAG）", "智能导览（Agent）"]
    audience_options = ["大众观众", "学生/入门", "专业观众"]

    mode_label = st.selectbox(
        "模式",
        options=mode_options,
        index=mode_options.index(st.session_state.get("guide_mode", "导览讲解"))
        if st.session_state.get("guide_mode", "导览讲解") in mode_options else 0,
        key="guide_mode_selector",
    )

    mode_forces_agent = mode_label != "导览讲解"
    if mode_forces_agent:
        st.session_state["guide_strategy_selector"] = "智能导览（Agent）"

    strategy_label = st.radio(
        "回答策略",
        options=strategy_options,
        index=1 if mode_forces_agent else (
            strategy_options.index(st.session_state.get("guide_strategy", "快速导览（直连RAG）"))
            if st.session_state.get("guide_strategy", "快速导览（直连RAG）") in strategy_options else 0
        ),
        disabled=mode_forces_agent,
        key="guide_strategy_selector",
    )
    if mode_forces_agent:
        st.caption(mode_label + " 模式固定走 Agent，策略选择不起效。")
        strategy_label = "智能导览（Agent）"

    current_use_direct_rag = strategy_label == "快速导览（直连RAG）"
    saved_allow_web        = st.session_state.get("guide_allow_web", False)
    effective_allow_web    = False if current_use_direct_rag else saved_allow_web
    if current_use_direct_rag and saved_allow_web:
        st.session_state["guide_allow_web"] = False

    allow_web = st.toggle(
        "允许联网补充",
        value=effective_allow_web,
        disabled=current_use_direct_rag,
        key="guide_allow_web_toggle",
    )

    audience_active = not mode_forces_agent
    audience = st.selectbox(
        "受众",
        options=audience_options,
        index=audience_options.index(st.session_state.get("guide_audience", "大众观众"))
        if st.session_state.get("guide_audience", "大众观众") in audience_options else 0,
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
    role             = message.get("role", "assistant")
    content          = message.get("content", "")
    citations_payload = message.get("citations")
    runtime_status   = message.get("runtime_status") if role == "assistant" else None

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
                source  = item.get("source", "unknown")
                page    = item.get("page")
                snippet = item.get("snippet", "")
                url     = item.get("url")
                header  = f"{item.get('index', '')}. {source}"
                if page is not None:
                    header += f" (p.{page})"
                if url:
                    st.markdown(f"**{header}** [链接]({url})")
                else:
                    st.markdown(f"**{header}**")
                st.write(snippet)
            st.caption("以上为检索到的关键片段。")


def render_guide_page(*, run_agent_request_streaming, run_direct_rag_request):
    _inject_css()

    # ── 页头 ──────────────────────────────────────────────
    head_left, head_right = st.columns([3, 1])
    with head_left:
        st.title("文化导览")
        st.caption("围绕侗绣纹样做讲解、展签转译与工艺解释")
    with head_right:
        st.write("")
        if st.button("清空对话", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    # ── 模式状态栏 ────────────────────────────────────────
    mode_label     = st.session_state.get("guide_mode", "导览讲解")
    strategy_label = st.session_state.get("guide_strategy", "快速导览（直连RAG）")
    audience       = st.session_state.get("guide_audience", "大众观众")
    citations_on   = st.session_state.get("guide_citations", True)
    web_on         = st.session_state.get("guide_allow_web", False)

    _render_status_bar(mode_label, strategy_label, audience, citations_on, web_on)

    st.markdown(
        '<hr style="border:none;border-top:2px solid #c9a227;margin:8px 0 14px;">',
        unsafe_allow_html=True,
    )

    # ── 示例问题 ──────────────────────────────────────────
    st.caption("示例问题")
    q_cols = st.columns(len(GUIDE_SAMPLE_QUESTIONS), gap="small")
    for i, (col, q) in enumerate(zip(q_cols, GUIDE_SAMPLE_QUESTIONS)):
        with col:
            if st.button(q, key=f"preset_{i}", use_container_width=True):
                st.session_state["preset_prompt"] = q
                st.rerun()

    st.divider()

    # ── 对话区 ────────────────────────────────────────────
    messages = st.session_state.get("messages", [])

    if not messages:
        st.markdown(
            """
            <div style="text-align:center; padding:40px 20px;">
                <div style="font-size:14px; color:#6b5a3a; line-height:1.9;">
                    点击上方示例问题，或在下方输入框直接提问
                </div>
                <div style="font-size:12px; color:#a89878; margin-top:6px;">
                    支持纹样讲解 · 展签生成 · 深度研究 · FAQ · 联网检索
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        show_count = min(6, len(messages))
        if len(messages) > show_count:
            with st.expander(f"更早的对话（{len(messages) - show_count} 条）", expanded=False):
                for msg in messages[:-show_count]:
                    _render_message_block(msg)
        for msg in messages[-show_count:]:
            _render_message_block(msg)

    # ── 输入框 ────────────────────────────────────────────
    prompt = st.chat_input("输入侗绣相关问题…")
    if not prompt:
        prompt = st.session_state.pop("preset_prompt", "")

    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state["messages"].append({"role": "user", "content": prompt})

        mode      = MODE_MAP[mode_label]
        use_direct = strategy_label == "快速导览（直连RAG）"
        use_agent  = not use_direct or mode != "guide"

        with st.spinner("稍等…"):
            placeholder       = st.empty()
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
