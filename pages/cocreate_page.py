import streamlit as st

from pages.runtime_status import render_runtime_status


COCREATE_PROMPT_EXAMPLES = [
    {
        "label": "展陈型示例",
        "pattern": "龙纹",
        "target": "海报视觉",
        "tone": "传统庄重",
        "extra": "希望用于侗绣主题展主视觉，突出守护感、中心构图与礼仪气质。",
    },
    {
        "label": "文创型示例",
        "pattern": "太阳榕树纹",
        "target": "品牌包装",
        "tone": "轻盈现代",
        "extra": "希望保留树形向上生长的视觉特征，并适合茶礼或文旅伴手礼包装。",
    },
    {
        "label": "教学型示例",
        "pattern": "混沌花纹",
        "target": "课程工作坊",
        "tone": "几何理性",
        "extra": "适合高校课程或研学工作坊，突出构图分析、纹样拆解和动手实践转化。",
    },
]

TARGET_OPTIONS = ["海报视觉", "丝巾设计", "课程工作坊", "品牌包装"]
TONE_OPTIONS = ["传统庄重", "轻盈现代", "几何理性", "节庆热烈"]
GENERATION_OPTIONS = ["快速模式（直连知识库）", "标准模式（Agent 工作流）"]


def parse_cocreate_sections(text: str) -> list[tuple[str, str]]:
    import re

    if not text:
        return []

    pattern = re.compile(r"(?m)^\s*(\d+[\.、]\s*[^\n：:]+[：:]?)")
    matches = list(pattern.finditer(text))
    if not matches:
        return [("创意提案", text.strip())] if text.strip() else []

    sections = []
    for idx, match in enumerate(matches):
        title = match.group(1).strip().rstrip("：:")
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append((title, body))
    return sections


def build_cocreate_query(
    pattern_name: str,
    theme: str,
    target: str,
    tone: str,
    extra: str,
    related_scans: list[dict],
    allow_web: bool,
    get_pattern_item,
):
    pattern = get_pattern_item(pattern_name) or {}
    extra_requirement = extra.strip() if extra else "无"
    scan_names = "、".join(item["name"] for item in related_scans) if related_scans else "当前未选择对应扫图"
    scan_context = "\n".join(f"- {item['name']}：{item['caption']}" for item in related_scans) if related_scans else "- 暂无对应扫图说明"
    web_instruction = "可以在本地资料不足时联网补充最新公开信息，但应优先采用本地知识库。" if allow_web else "仅使用本地知识库与已有资料，不联网。"

    return f"""请为侗族织绣纹样生成一组可直接用于提案的创意方案。\n\n核心纹样：{pattern_name}\n纹样类别：{pattern.get('category', '未标注')}\n共创主题：{theme}\n应用方向：{target}\n风格倾向：{tone}\n常见载体：{pattern.get('carrier', '未标注')}\n视觉关键词：{'、'.join(pattern.get('keywords', [])) or '未标注'}\n图谱摘要：{pattern.get('summary', '未标注')}\n图案特征：{'；'.join(pattern.get('features', [])) or '未标注'}\n关联真实扫图：{scan_names}\n扫图观察线索：\n{scan_context}\n补充要求：{extra_requirement}\n联网策略：{web_instruction}\n\n请优先基于本地资料提炼该纹样的构图线索、视觉气质、文化语义与可转化方向，再输出以下内容：\n1. 概念标题：给出 3 个备选标题，每个不超过 12 个字；\n2. 创意定位：120-180 字；\n3. 主文案：90-140 字，可直接用于页面首屏或展陈说明；\n4. 视觉关键词：给出 6 个；\n5. 设计转化建议：给出 3 条，说明适合落在哪种介质或场景；\n6. 图像使用建议：结合图谱卡片与真实扫图，说明适合保留哪些视觉特征。\n\n要求：\n- 只输出最终结果，不要复述任务；\n- 中文输出，适合设计提案语境；\n- 不要编造具体年代、仪式、地域来源等未证实细节；\n- 如果本地资料不足，请用保守表述。"""


def _render_reference_citations(citations_payload):
    citation_items = []
    if isinstance(citations_payload, dict):
        citation_items = citations_payload.get("citations", []) or []
    elif isinstance(citations_payload, list):
        citation_items = citations_payload

    if not citation_items:
        return

    with st.expander("本次提案参考资料", expanded=False):
        for item in citation_items:
            if not isinstance(item, dict):
                continue
            source = item.get("source", "unknown")
            page = item.get("page")
            snippet = item.get("snippet", "")
            header = f"{item.get('index', '')}. {source}"
            if page is not None:
                header += f" (page {page})"
            st.markdown(f"**{header}**")
            if snippet:
                st.write(snippet)
        st.caption("以上为本次创意提案使用到的主要知识片段。")


def _render_result_sections(result_text: str):
    result_sections = parse_cocreate_sections(result_text)
    if not result_sections:
        st.write(result_text)
        return

    for title, body in result_sections:
        st.markdown(f"#### {title}")
        st.write(body or "-")


def render_cocreate_page(
    *,
    cocreate_page: str,
    pattern_page: str,
    apply_cocreate_preset,
    render_section_heading,
    get_pattern_names,
    get_pattern_item,
    get_related_scan_items,
    run_direct_rag_request,
    run_agent_request_streaming,
):
    pending_preset = st.session_state.pop("pending_cocreate_preset", None)
    if pending_preset:
        st.session_state["cocreate_pattern"] = pending_preset["pattern"]
        st.session_state["cocreate_theme"] = pending_preset["theme"]
        st.session_state["cocreate_target"] = pending_preset["target"]
        st.session_state["cocreate_tone"] = pending_preset["tone"]
        st.session_state["cocreate_extra"] = pending_preset["extra"]

    st.title(cocreate_page)
    st.caption("把纹样理解、扫图观察和设计方向组织起来，快速生成更像提案初稿的结构化结果。")
    st.divider()

    intro_left, intro_right = st.columns([1.15, 0.85], gap="large")
    with intro_left:
        st.markdown("### 这里不是自由聊天区")
        st.write(
            "这一页更像一个轻量设计工作台：先选纹样，再结合真实扫图和使用场景，"
            "最后生成可直接进入方案讨论的设计提案。"
        )
        st.markdown("- 适合先出海报、包装、课程或展签方向的概念稿")
        st.markdown("- 适合把侗绣纹样从‘知识理解’继续推进到‘设计转化’")
        st.markdown("- 结果优先追求结构清晰、可讨论，而不是一次生成超长提示词")
    with intro_right:
        st.info("推荐先从一个核心纹样进入，再逐步补充风格、场景和用途，生成效果通常更稳定。")
        st.metric("当前目标", "设计提案初稿")
        st.metric("输入方式", "低输入 / 高选择")

    st.divider()
    steps_cols = st.columns(3, gap="large")
    step_data = [
        ("步骤 1", "选择核心纹样", "先锁定一个母题，让本次共创有明确的视觉中心。"),
        ("步骤 2", "带入真实观察", "结合图谱卡片与真实扫图，提取针脚、层次和构图线索。"),
        ("步骤 3", "生成结构化提案", "输出标题、定位、主文案、视觉关键词和转化建议。"),
    ]
    for col, item in zip(steps_cols, step_data):
        step, title, desc = item
        with col:
            st.markdown(f"#### {step}")
            st.caption(title)
            st.write(desc)

    st.divider()
    workspace_left, workspace_right = st.columns([1.05, 0.95], gap="large")

    with workspace_left:
        render_section_heading("设置任务", "")
        col1, col2 = st.columns(2)
        with col1:
            pattern_name = st.selectbox("纹样", get_pattern_names(), key="cocreate_pattern")
            pattern_item = get_pattern_item(pattern_name) or {}   # 紧跟在 pattern_name 后面
            target = st.selectbox("用途", TARGET_OPTIONS, key="cocreate_target")
        with col2:
            # 注意：theme 的默认值里用到了 pattern_name，所以 pattern_name 必须先定义
            default_theme = f"围绕{pattern_name}展开当代转化"
            theme = st.text_input("主题", value=default_theme, key="cocreate_theme")
            tone = st.selectbox("风格", TONE_OPTIONS, key="cocreate_tone")
    
        extra = st.text_area("补充说明", value=st.session_state.get("cocreate_extra", ""), height=80, key="cocreate_extra")

        with st.expander("高级选项"):
            allow_web = st.checkbox("允许联网", value=True, key="cocreate_allow_web")
            generation_mode = st.radio("生成方式", GENERATION_OPTIONS, index=0, key="cocreate_generation_mode", horizontal=True)

        generate = st.button("生成提案", key="cocreate_generate", use_container_width=True)

        st.caption("试试这些：")
        ex_cols = st.columns(3)
        for i, sample in enumerate(COCREATE_PROMPT_EXAMPLES):
            with ex_cols[i]:
                if st.button(sample["label"], key=f"ex_{i}", use_container_width=True):
                    apply_cocreate_preset(
                        sample["pattern"],
                        f"围绕{sample['pattern']}展开当代转化",
                        sample["target"],
                        sample["tone"],
                        sample["extra"],
                    )
                    st.rerun()

    with workspace_right:
        related_scans = get_related_scan_items(pattern_name)
        render_section_heading("本次输入预览", "先确认知识依据和设计语境是否一致")
        st.markdown(f"- 核心纹样：{pattern_name}")
        st.markdown(f"- 纹样类别：{pattern_item.get('category', '未标注')}")
        st.markdown(f"- 常见载体：{pattern_item.get('carrier', '未标注')}")
        st.markdown(f"- 视觉关键词：{'、'.join(pattern_item.get('keywords', [])) or '未标注'}")
        st.info(pattern_item.get("summary", "当前纹样暂无摘要。"))

        if related_scans:
            st.markdown("**关联真实扫图**")
            for item in related_scans[:3]:
                st.markdown(f"- {item['name']}（{item['category']}）")
        else:
            st.caption("当前纹样暂未关联真实扫图。")

        allow_web = st.session_state.get("cocreate_allow_web", True)
        generation_mode = st.session_state.get("cocreate_generation_mode", GENERATION_OPTIONS[0])
        if allow_web:
            st.caption("本次生成将优先使用本地知识库，并在必要时补充公开网络资料。")
        else:
            st.caption("本次生成仅使用本地知识库与当前图谱资料。")

        if generation_mode == GENERATION_OPTIONS[0]:
            st.caption("快速模式更适合先出第一版提案。")
        else:
            st.caption("标准模式会经过 Agent 工作流，通常更完整，也更适合复杂需求。")

    st.divider()
    reference_left, reference_right = st.columns([1.1, 0.9], gap="large")
    with reference_left:
        render_section_heading("图谱卡片参考", "先看图谱，再做提案，通常比直接生成更稳")
        if pattern_item:
            try:
                _, img_col, _ = st.columns([0.5, 3, 0.5])
                with img_col:
                    st.image(pattern_item["image"], use_container_width=True)
            except Exception:
                st.warning("该纹样图片暂时无法显示。")        
            st.markdown(f"#### {pattern_name}")
            st.caption(pattern_item.get("category", ""))
            for feature in pattern_item.get("features", []):
                st.markdown(f"- {feature}")
        if st.button(f"进入图谱查看 {pattern_name}", key="cocreate-go-pattern", use_container_width=True):
            st.session_state["current_page"] = pattern_page
            st.rerun()

    with reference_right:
        render_section_heading("真实扫图参考", "把针脚、层次和边饰关系带回设计转化")
        if related_scans:
            for item in related_scans[:2]:
                try:
                    _, img_col, _ = st.columns([0.5, 3, 0.5])
                    with img_col:
                        st.image(item["image"], use_container_width=True)
                except Exception:
                    st.warning("该扫图暂时无法显示。")
                st.caption(f"{item['name']}｜{item['category']}")
                if item.get("caption"):
                    st.write(item["caption"])            
        else:
            st.caption("当前暂无关联扫图。")

    st.divider()
    result_left, result_right = st.columns([1.15, 0.85], gap="large")
    with result_left:
        render_section_heading("提案结果区", "生成后可直接用于方案初稿、课堂讨论或展陈文案整理")

        if generate:
            related_scans = get_related_scan_items(pattern_name)
            cocreate_prompt = build_cocreate_query(
                pattern_name,
                theme,
                target,
                tone,
                extra,
                related_scans,
                allow_web,
                get_pattern_item,
            )

            if generation_mode == GENERATION_OPTIONS[0]:
                with st.spinner("正在快速生成设计提案..."):
                    answer, citations, _, _, debug_notice = run_direct_rag_request(cocreate_prompt)
            else:
                stream_placeholder = st.empty()
                with st.spinner("正在生成设计提案..."):
                    answer, citations, debug_notice = run_agent_request_streaming(
                        cocreate_prompt,
                        {
                            "mode": "research",
                            "audience": "专业观众",
                            "citations_enabled": True,
                            "allow_web": allow_web,
                        },
                        stream_placeholder,
                    )
                stream_placeholder.empty()

            st.session_state["cocreate_result"] = answer
            st.session_state["cocreate_citations"] = citations
            st.session_state["cocreate_debug_notice"] = debug_notice
            st.session_state["cocreate_runtime_status"] = st.session_state.get("_last_runtime_status")

        cocreate_result = st.session_state.get("cocreate_result", "")
        cocreate_citations = st.session_state.get("cocreate_citations")
        cocreate_debug_notice = st.session_state.get("cocreate_debug_notice")
        cocreate_runtime_status = st.session_state.get("cocreate_runtime_status")

        if cocreate_result:
            render_runtime_status(cocreate_runtime_status)
            st.text_area("提案全文", value=cocreate_result, height=260, key="cocreate_result_text")
            if cocreate_debug_notice:
                st.warning(cocreate_debug_notice.get("message", "本次生成出现异常。"))
                detail = cocreate_debug_notice.get("detail")
                if detail:
                    with st.expander("查看本次调试信息", expanded=False):
                        st.code(detail)
            _render_result_sections(cocreate_result)
            _render_reference_citations(cocreate_citations)
        else:
            st.caption("完成纹样和方向设置后点击“生成设计提案”，这里会显示结构化提案内容。")

    with result_right:
        render_section_heading("怎么用这页更有效", "帮助第一次上手的人更快生成有依据的提案")
        st.markdown("- 先确定一个核心纹样，不建议一开始就给过于宽泛的主题。")
        st.markdown("- 优先观察图谱和扫图，再写补充要求，结果通常更贴近侗绣语境。")
        st.markdown("- 如果目标是比赛、课程或品牌方案，把使用场景写进补充要求会更好。")
        st.markdown("- 快速模式适合先出初稿，标准模式适合需要更完整说明的方案。")

    st.divider()
    usage_left, usage_right = st.columns(2, gap="large")
    with usage_left:
        render_section_heading("推荐操作路径", "第一次使用时，建议这样走")
        st.markdown("1. 选择一个纹样，例如龙纹、太阳榕树纹或混沌花纹。")
        st.markdown("2. 先看右侧图谱摘要和扫图，再决定要不要补充更多应用要求。")
        st.markdown("3. 选择应用方向和风格倾向，生成结构化提案。")
        st.markdown("4. 生成后把结果带回图谱或导览页面继续追问和补充。")
    with usage_right:
        render_section_heading("适合输出到哪些场景", "这样更容易把它讲成平台能力，而不是单页工具")
        st.markdown("- 海报主视觉或展陈说明初稿")
        st.markdown("- 文旅包装与文创概念提案")
        st.markdown("- 课程工作坊与教学活动策划")
        st.markdown("- 展签、导览文案与页面首屏文案")
