import streamlit as st


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
    st.caption("默认先展示图、名称、摘要和少量关键词；更详细的信息放进展开区域。")
    st.divider()

    overview_left, overview_right = st.columns([0.9, 1.1], gap="large")
    with overview_left:
        render_section_heading("图谱导览", "先筛选，再逐个展开看会更轻松")
        st.write(
            "这一页把典型母题和真实扫图放在一起，方便从图像观察进入进一步理解。"
            "为了减少反复跳转，我保留了筛选、导览入口和共创入口，但会尽量让结构更清楚。"
        )
    with overview_right:
        st.markdown("**浏览提示**")
        st.markdown("- 先按类型筛选，减少一次看到太多内容。\n- 先看图片和摘要，再决定要不要进入导览。\n- 如果想做设计延展，再进入 AI 共创。")

    st.divider()
    overview_cols = st.columns(4, gap="large")
    with overview_cols[0]:
        st.metric("已展示纹样", str(len(pattern_items)), help="当前图谱卡片总数")
    with overview_cols[1]:
        st.metric("图谱类型", "5 类", help="动物、人物、组合、植物/天体、几何/花卉")
    with overview_cols[2]:
        st.metric("了解", "已开发", help="跳到智能导览并自动带入该纹样问题")
    with overview_cols[3]:
        st.metric("进入共创", "已开发", help="跳到 AI 共创实验并自动预填当前纹样")

    st.divider()
    filter_options = ["全部", "动物纹", "人物纹", "植物纹 / 天体纹", "组合纹", "几何纹 / 花卉纹"]
    selected_filter = st.radio("按类型筛选", filter_options, horizontal=True, key="pattern_filter")
    visible_items = [
        item for item in pattern_items if selected_filter == "全部" or item["category"] == selected_filter
    ]

    if not visible_items:
        st.info("当前筛选条件下暂无纹样卡片。")
        return

    st.divider()
    for start in range(0, len(visible_items), 2):
        cols = st.columns(2, gap="large")
        for col, item in zip(cols, visible_items[start : start + 2]):
            with col:
                try:
                    st.image(item["image"], width="stretch")
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
                    if st.button(f"了解 {item['name']}", key=f"pattern-ask-{item['name']}", width="stretch"):
                        st.session_state["current_page"] = guide_page
                        st.session_state["preset_prompt"] = f"请介绍侗族刺绣中的{item['name']}，重点说明构成特点、视觉特征和常见应用。"
                        st.rerun()
                with action_col2:
                    if st.button(f"进入共创", key=f"pattern-cocreate-{item['name']}", width="stretch"):
                        apply_cocreate_preset(
                            item["name"],
                            f"围绕{item['name']}展开当代转化",
                            "海报视觉",
                            "传统庄重",
                            f"希望围绕{item['name']}展开当代转化，保留其核心构图特征与文化气质。",
                        )
                        st.session_state["current_page"] = cocreate_page
                        st.rerun()

    st.divider()
    st.caption("按钮说明：‘了解’会跳到智能导览；‘进入共创’会跳到 AI 共创；扫图区的‘查看关联纹样’会带着扫图线索去导览，‘以这张扫图进入共创’会直接预填共创。")
    render_section_heading("刺绣扫图", "从真实绣片扫描中观察针脚、材质与构图细节")
    scan_filter_options = ["全部", "龙纹类", "花纹类", "盘型类", "树纹类"]
    selected_scan_filter = st.radio("按扫图类别浏览", scan_filter_options, horizontal=True, key="pattern_scan_filter")
    visible_scan_items = [
        item for item in pattern_scan_items if selected_scan_filter == "全部" or item["category"] == selected_scan_filter
    ]
    scan_cols = st.columns(3, gap="large")
    for idx, item in enumerate(visible_scan_items):
        with scan_cols[idx % 3]:
            st.image(item["image"], width="stretch")
            st.markdown(f"#### {item['name']}")
            st.caption(f"类别：{item['category']}｜对应图谱：{item['related_pattern']}")
            st.write(item["caption"])
            scan_action_col1, scan_action_col2 = st.columns(2)
            with scan_action_col1:
                if st.button(f"查看关联纹样：{item['related_pattern']}", key=f"scan-link-{item['name']}", width="stretch"):
                    st.session_state["preset_prompt"] = f"请介绍侗族刺绣中的{item['related_pattern']}，并结合真实绣片说明它在构图和工艺表现上的特点。"
                    st.session_state["current_page"] = guide_page
                    st.rerun()
            with scan_action_col2:
                if st.button(f"以这张扫图进入共创", key=f"scan-cocreate-{item['name']}", width="stretch"):
                    apply_cocreate_preset(
                        item["related_pattern"],
                        f"围绕{item['name']}展开当代转化",
                        "海报视觉",
                        "传统庄重",
                        f"请结合真实扫图《{item['name']}》展开创意提案，重点吸收其{item['caption']}",
                    )
                    st.session_state["current_page"] = cocreate_page
                    st.rerun()

    st.divider()
    detail_cols = st.columns(2, gap="large")
    with detail_cols[0]:
        render_section_heading("图谱阅读维度", "适合从图像观察延伸到更深入的知识理解")
        st.markdown("- 纹样名称与类型")
        st.markdown("- 核心构图关系")
        st.markdown("- 局部线条与重复节奏")
        st.markdown("- 常见载体与视觉位置")
        st.markdown("- 适合延展的设计方向")
    with detail_cols[1]:
        render_section_heading("延伸入口", "纹样图谱可与其它模块形成连续浏览")
        st.markdown("- 进入智能导览，获取讲解词和展签说明")
        st.markdown("- 进入文创展示，查看纹样转化案例")
        st.markdown("- 进入 AI 共创实验，生成概念提案")
        st.markdown("- 进入场景应用，思考展陈与传播方式")
