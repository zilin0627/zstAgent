import streamlit as st


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


def build_cocreate_query(pattern_name: str, theme: str, target: str, tone: str, extra: str, related_scans: list[dict], allow_web: bool, get_pattern_item):
    pattern = get_pattern_item(pattern_name) or {}
    extra_requirement = extra.strip() if extra else "无"
    scan_names = "、".join(item["name"] for item in related_scans) if related_scans else "当前未选择对应扫图"
    scan_context = "\n".join(f"- {item['name']}：{item['caption']}" for item in related_scans) if related_scans else "- 暂无对应扫图说明"
    web_instruction = "可以在本地资料不足时联网补充最新公开信息，但应优先采用本地知识库。" if allow_web else "仅使用本地知识库与已有资料，不联网。"

    return f"""请为侗族织绣纹样生成一组可直接用于提案的创意方案。\n\n核心纹样：{pattern_name}\n纹样类别：{pattern.get('category', '未标注')}\n共创主题：{theme}\n应用方向：{target}\n风格倾向：{tone}\n常见载体：{pattern.get('carrier', '未标注')}\n视觉关键词：{'、'.join(pattern.get('keywords', [])) or '未标注'}\n图谱摘要：{pattern.get('summary', '未标注')}\n图案特征：{'；'.join(pattern.get('features', [])) or '未标注'}\n关联真实扫图：{scan_names}\n扫图观察线索：\n{scan_context}\n补充要求：{extra_requirement}\n联网策略：{web_instruction}\n\n请优先基于本地资料提炼该纹样的构图线索、视觉气质、文化语义与可转化方向，再输出以下内容：\n1. 概念标题：给出 3 个备选标题，每个不超过 12 个字；\n2. 创意定位：120-180 字；\n3. 主文案：90-140 字，可直接用于页面首屏或展陈说明；\n4. 视觉关键词：给出 6 个；\n5. 设计转化建议：给出 3 条，说明适合落在哪种介质或场景；\n6. 图像使用建议：结合图谱卡片与真实扫图，说明适合保留哪些视觉特征。\n\n要求：\n- 只输出最终结果，不要复述任务；\n- 中文输出，适合设计提案语境；\n- 不要编造具体年代、仪式、地域来源等未证实细节；\n- 如果本地资料不足，请用保守表述。"""


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
    st.caption("用选择代替大段输入，让这里更像设计工作台，而不是提示词实验区。")
    st.divider()

    steps_cols = st.columns(3, gap="large")
    step_data = [
        ("步骤 1", "选择纹样", "先从图谱母题中锁定一个核心纹样，明确本次共创的视觉中心。"),
        ("步骤 2", "参考扫图", "查看与该纹样关联的真实刺绣扫图，提取针脚、层次和构图特征。"),
        ("步骤 3", "生成提案", "结合主题、方向与风格倾向，生成可直接进入方案讨论的文案结果。"),
    ]
    for col, item in zip(steps_cols, step_data):
        step, title, desc = item
        with col:
            st.markdown(f"#### {step}")
            st.caption(title)
            st.write(desc)

    st.divider()
    lab_left, lab_right = st.columns([1.05, 0.95], gap="large")
    with lab_left:
        pattern_name = st.selectbox("核心纹样", get_pattern_names(), key="cocreate_pattern")
        pattern_item = get_pattern_item(pattern_name) or {}
        default_theme = f"围绕{pattern_name}展开当代转化"
        theme = st.text_input("设计方向", value=default_theme, key="cocreate_theme")
        target = st.selectbox("应用方向", ["海报视觉", "丝巾设计", "课程工作坊", "品牌包装"], key="cocreate_target")
        tone = st.selectbox("风格倾向", ["传统庄重", "轻盈现代", "几何理性", "节庆热烈"], key="cocreate_tone")
        extra = st.text_area("补充说明", value=st.session_state.get("cocreate_extra", "希望既有传统纹样依据，也适合当代传播语境。"), height=120, key="cocreate_extra")
        with st.expander("高级设置", expanded=False):
            allow_web = st.toggle("允许联网补充", value=True, key="cocreate_allow_web")
            generation_mode = st.radio("生成模式", options=["快速模式（直连知识库）", "标准模式（Agent 工作流）"], index=0, key="cocreate_generation_mode")
        generate = st.button("生成设计提案", key="cocreate_generate", width="stretch")

        st.markdown("### 快速示例")
        for sample in COCREATE_PROMPT_EXAMPLES:
            if st.button(sample["label"], key=f"cocreate-example-{sample['label']}", width="stretch"):
                apply_cocreate_preset(
                    sample["pattern"],
                    f"围绕{sample['pattern']}展开当代转化",
                    sample["target"],
                    sample["tone"],
                    sample["extra"],
                )
                st.rerun()

    with lab_right:
        related_scans = get_related_scan_items(pattern_name)
        st.markdown("### 纹样输入预览")
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
        if allow_web:
            st.caption("本次生成将优先使用本地知识库，并在必要时补充公开网络资料。")
        else:
            st.caption("本次生成仅使用本地知识库与当前图谱资料。")
        if generation_mode == "快速模式（直连知识库）":
            st.caption("快速模式会直接调用本地知识库总结，速度更快，适合先出初稿。")
        else:
            st.caption("标准模式会经过 Agent 工作流，并支持联网补充，内容通常更完整。")

    st.divider()
    reference_cols = st.columns([1.1, 0.9], gap="large")
    with reference_cols[0]:
        render_section_heading("图谱与扫图联动", "先观察图谱卡片，再对照真实绣片，有助于提升提案质量")
        if pattern_item:
            st.image(pattern_item["image"], width="stretch")
            st.markdown(f"#### {pattern_name}")
            st.caption(pattern_item.get("category", ""))
            for feature in pattern_item.get("features", []):
                st.markdown(f"- {feature}")
        if st.button(f"进入图谱查看 {pattern_name}", key="cocreate-go-pattern", width="stretch"):
            st.session_state["current_page"] = pattern_page
            st.rerun()
    with reference_cols[1]:
        render_section_heading("关联真实扫图", "可直接把扫图中的针脚层次、边饰关系带入共创")
        related_scans = get_related_scan_items(pattern_name)
        if related_scans:
            for item in related_scans[:2]:
                st.image(item["image"], width="stretch")
                st.caption(f"{item['name']}｜{item['category']}")
        else:
            st.caption("当前暂无关联扫图。")

    st.divider()
    result_cols = st.columns([1.15, 0.85], gap="large")
    with result_cols[0]:
        render_section_heading("创意结果区", "生成后可直接复制用于方案提案、展陈初稿或概念页")
        if generate:
            related_scans = get_related_scan_items(pattern_name)
            cocreate_prompt = build_cocreate_query(pattern_name, theme, target, tone, extra, related_scans, allow_web, get_pattern_item)
            if generation_mode == "快速模式（直连知识库）":
                with st.spinner("正在快速生成创意提案..."):
                    answer, citations = run_direct_rag_request(cocreate_prompt)
            else:
                stream_placeholder = st.empty()
                with st.spinner("正在生成创意提案..."):
                    answer, citations = run_agent_request_streaming(
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

        cocreate_result = st.session_state.get("cocreate_result", "")
        if cocreate_result:
            result_sections = parse_cocreate_sections(cocreate_result)
            st.text_area("提案结果文本", value=cocreate_result, height=280, key="cocreate_result_text")
            if result_sections:
                for title, body in result_sections:
                    st.markdown(f"#### {title}")
                    st.write(body or "-")
            else:
                st.write(cocreate_result)
            cocreate_citations = st.session_state.get("cocreate_citations")
            citation_items = []
            if isinstance(cocreate_citations, dict):
                citation_items = cocreate_citations.get("citations", []) or []
            elif isinstance(cocreate_citations, list):
                citation_items = cocreate_citations
            if citation_items:
                with st.expander("本次创意参考资料", expanded=False):
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
        else:
            st.caption("完成纹样选择后点击“生成创意提案”，这里会显示概念标题、主文案和转化建议。")

    with result_cols[1]:
        render_section_heading("使用建议", "帮助浏览者更快上手这个共创模块")
        st.markdown("- 先从‘选择核心纹样’开始，不建议一开始就输入太泛的主题。")
        st.markdown("- 优先观察关联扫图中的层次、边饰和针脚，再写补充要求。")
        st.markdown("- 如果要做比赛、课程或品牌方案，可把具体用途写进补充要求。")
        st.markdown("- 开启联网后，系统会在本地资料不足时补充公开背景信息。")

    st.divider()
    usage_cols = st.columns(2, gap="large")
    with usage_cols[0]:
        render_section_heading("推荐操作方式", "适合第一次使用的浏览者")
        st.markdown("1. 选择一个纹样，例如龙纹、太阳榕树纹或混沌花纹。")
        st.markdown("2. 查看右侧图谱摘要与关联真实扫图，先形成视觉判断。")
        st.markdown("3. 选择应用方向和风格，再补充具体场景要求。")
        st.markdown("4. 生成后把结果带回图谱或导览页面继续追问。")
    with usage_cols[1]:
        render_section_heading("提示词参考", "可以直接参考这些写法")
        st.markdown("- 请围绕龙纹生成一组适合侗绣主题展主视觉的海报文案，强调中心构图与守护感。")
        st.markdown("- 请围绕太阳榕树纹生成一组适合文旅包装的概念提案，突出向上生长与层级关系。")
        st.markdown("- 请结合混沌花纹和真实扫图观察，生成适合课程工作坊的教学型策划文案。")
