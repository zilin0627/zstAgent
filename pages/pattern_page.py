import streamlit as st


FILTER_OPTIONS = ["全部", "动物纹", "人物纹", "植物纹 / 天体纹", "组合纹", "几何纹 / 花卉纹"]
SCAN_FILTER_OPTIONS = ["全部", "龙纹类", "花纹类", "盘型类", "树纹类"]


def _render_pattern_card(*, item, guide_page: str, cocreate_page: str, apply_cocreate_preset):
    try:
        st.image(item["image"], use_container_width=True)
    except Exception:
        st.warning("该纹样图片暂时无法显示。")

    st.markdown(f"#### {item['name']}")
    st.caption(f"{item['category']}｜{' / '.join(item['tags'])}")
    st.write(item["summary"])
    st.markdown(f"**常见载体**：{item['carrier']}")
    st.markdown(f"**视觉关键词**：{'、'.join(item['keywords'])}")

    with st.expander("查看图案特征", expanded=False):
        for feature in item["features"]:
            st.markdown(f"- {feature}")

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button(f"了解 {item['name']}", key=f"pattern-ask-{item['name']}", use_container_width=True):
            st.session_state["current_page"] = guide_page
            st.session_state["preset_prompt"] = f"请介绍侗族刺绣中的{item['name']}，重点说明构成特点、视觉特征和常见应用。"
            st.rerun()
    with action_col2:
        if st.button(f"进入共创", key=f"pattern-cocreate-{item['name']}", use_container_width=True):
            apply_cocreate_preset(
                item["name"],
                f"围绕{item['name']}展开当代转化",
                "海报视觉",
                "传统庄重",
                f"希望围绕{item['name']}展开当代转化，保留其核心构图特征与文化气质。",
            )
            st.session_state["current_page"] = cocreate_page
            st.rerun()


def _render_scan_card(*, item, idx: int, guide_page: str, cocreate_page: str, apply_cocreate_preset):
    scan_key = f"{idx}-{item['name']}-{item['related_pattern']}"
    try:
        st.image(item["image"], use_container_width=True)
    except Exception:
        st.warning("该扫图图片暂时无法显示。")

    st.markdown(f"#### {item['name']}")
    st.caption(f"类别：{item['category']}｜对应图谱：{item['related_pattern']}")
    st.write(item["caption"])

    scan_action_col1, scan_action_col2 = st.columns(2)
    with scan_action_col1:
        if st.button(f"查看关联纹样：{item['related_pattern']}", key=f"scan-link-{scan_key}", use_container_width=True):
            st.session_state["preset_prompt"] = f"请介绍侗族刺绣中的{item['related_pattern']}，并结合真实绣片说明它在构图和工艺表现上的特点。"
            st.session_state["current_page"] = guide_page
            st.rerun()
    with scan_action_col2:
        if st.button(f"以这张扫图进入共创", key=f"scan-cocreate-{scan_key}", use_container_width=True):
            apply_cocreate_preset(
                item["related_pattern"],
                f"围绕{item['name']}展开当代转化",
                "海报视觉",
                "传统庄重",
                f"请结合真实扫图《{item['name']}》展开创意提案，重点吸收其{item['caption']}",
            )
            st.session_state["current_page"] = cocreate_page
            st.rerun()


def render_pattern_page(
    *,
    guide_page: str,
    cocreate_page: str,
    pattern_items: list[dict],
    pattern_scan_items: list[dict],
    apply_cocreate_preset,
    render_section_heading,
):
    st.title("纹样图谱")
    st.caption("这是平台的知识入口页：先从母题和真实扫图建立观察，再进入导览理解或设计转化。")
    st.divider()

    intro_left, intro_right = st.columns([1.05, 0.95], gap="large")
    with intro_left:
        render_section_heading("这页到底在做什么", "先看图谱，再去导览和共创，会比直接提问更稳")
        st.write(
            "这一页把典型纹样母题和真实绣片扫图放在一起，帮助用户先建立视觉判断，"
            "再决定下一步是去做知识导览，还是进入设计工作台生成提案。"
        )
        st.markdown("- 先看图样、摘要和关键词，建立第一印象")
        st.markdown("- 再看真实扫图，理解针脚层次、构图关系和材质感")
        st.markdown("- 最后进入智能导览或设计工作台，形成连续使用路径")
    with intro_right:
        st.info("推荐先从一个典型纹样进入，不要一开始就泛泛地问‘侗绣有什么特点’。")
        metric_cols = st.columns(2, gap="medium")
        with metric_cols[0]:
            st.metric("图谱卡片", str(len(pattern_items)))
        with metric_cols[1]:
            st.metric("扫图样本", str(len(pattern_scan_items)))

    st.divider()
    path_cols = st.columns(3, gap="large")
    path_items = [
        ("路径 1", "先识别母题", "从龙纹、对鸟纹、太阳花纹等典型母题进入，快速建立纹样印象。"),
        ("路径 2", "再对照真实扫图", "把图谱卡片和真实绣片放在一起看，更容易理解层次和工艺表现。"),
        ("路径 3", "继续去导览或共创", "需要讲解就进智能导览，需要提案就进设计工作台。"),
    ]
    for col, item in zip(path_cols, path_items):
        step, title, desc = item
        with col:
            st.markdown(f"#### {step}")
            st.caption(title)
            st.write(desc)

    st.divider()
    overview_cols = st.columns(4, gap="large")
    with overview_cols[0]:
        st.metric("图谱类型", "5 类", help="动物、人物、组合、植物/天体、几何/花卉")
    with overview_cols[1]:
        st.metric("知识入口", "已建立", help="从图谱卡片进入导览问答")
    with overview_cols[2]:
        st.metric("设计入口", "已建立", help="从图谱卡片进入设计工作台")
    with overview_cols[3]:
        st.metric("浏览方式", "图谱 + 扫图", help="把标准化图谱和真实绣片观察结合起来")

    st.divider()
    render_section_heading("典型纹样图谱", "先按类型筛选，再逐个查看会更清楚")
    selected_filter = st.radio("按类型筛选", FILTER_OPTIONS, horizontal=True, key="pattern_filter")
    visible_items = [
        item for item in pattern_items if selected_filter == "全部" or item["category"] == selected_filter
    ]

    if not visible_items:
        st.info("当前筛选条件下暂无纹样卡片。")
        return

    for start in range(0, len(visible_items), 2):
        cols = st.columns(2, gap="large")
        for col, item in zip(cols, visible_items[start : start + 2]):
            with col:
                _render_pattern_card(
                    item=item,
                    guide_page=guide_page,
                    cocreate_page=cocreate_page,
                    apply_cocreate_preset=apply_cocreate_preset,
                )

    st.divider()
    render_section_heading("真实刺绣扫图", "这一部分帮助你把图谱理解带回真实绣片")
    st.caption("按钮说明：查看关联纹样会跳到智能导览；以这张扫图进入共创会直接预填设计工作台。")
    selected_scan_filter = st.radio("按扫图类别浏览", SCAN_FILTER_OPTIONS, horizontal=True, key="pattern_scan_filter")
    visible_scan_items = [
        item for item in pattern_scan_items if selected_scan_filter == "全部" or item["category"] == selected_scan_filter
    ]

    if visible_scan_items:
        scan_cols = st.columns(3, gap="large")
        for idx, item in enumerate(visible_scan_items):
            with scan_cols[idx % 3]:
                _render_scan_card(
                    item=item,
                    idx=idx,
                    guide_page=guide_page,
                    cocreate_page=cocreate_page,
                    apply_cocreate_preset=apply_cocreate_preset,
                )
    else:
        st.info("当前筛选条件下暂无扫图样本。")

    st.divider()
    bottom_left, bottom_right = st.columns(2, gap="large")
    with bottom_left:
        render_section_heading("建议从哪些维度读图谱", "这部分适合带着问题去看")
        st.markdown("- 纹样名称与类型：先判断它是动物纹、人物纹还是几何骨架")
        st.markdown("- 核心构图关系：看它是中心式、放射式、围合式还是连续式")
        st.markdown("- 视觉关键词：把‘盘旋、呼应、生长、均衡’这类词和图样对应起来")
        st.markdown("- 常见载体：判断它更适合出现在中心装饰区、边饰还是主题图样中")
        st.markdown("- 延展潜力：思考哪些纹样更适合做海报、包装、课程或展签内容")
    with bottom_right:
        render_section_heading("从这里可以继续去哪", "把这页真正用成平台入口，而不是静态浏览页")
        st.markdown("- 去智能导览：适合继续追问寓意、结构特征和使用场景")
        st.markdown("- 去设计工作台：适合把当前纹样直接转成概念提案")
        st.markdown("- 去文创展陈：适合看纹样已经如何被转化为平面和产品")
        st.markdown("- 去场景落地：适合继续看这些内容如何进入展馆、课堂和品牌传播")
