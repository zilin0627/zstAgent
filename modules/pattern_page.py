import streamlit as st


CATEGORY_OPTIONS = [
    "全部",
    "动物纹",
    "人物纹",
    "植物纹 / 天体纹",
    "组合纹",
    "几何纹 / 花卉纹",
]

SCAN_CATEGORY_OPTIONS = ["全部", "龙纹类", "花纹类", "盘型类", "树纹类"]


def render_pattern_page(*, pattern_page: str, pattern_atlas_items: list[dict], pattern_scan_items: list[dict], render_section_heading):
    st.title(pattern_page)
    st.caption("从典型母题、真实扫图与结构特征出发，帮助观众更自然地看懂侗绣纹样。")
    st.divider()

    intro_left, intro_right = st.columns([1.15, 0.85], gap="large")
    with intro_left:
        st.markdown("## 从‘看见纹样’到‘读懂纹样’")
        st.write(
            "这一页不是单纯把纹样图片排开，而是希望帮助观众先认识侗绣中常见的典型母题，"
            "再进一步理解它们的构图方式、常见位置、视觉气质和工艺特点。"
        )
        st.write(
            "你可以先从图谱卡片快速建立印象，再回到真实刺绣扫图观察针脚、层次和边饰关系，"
            "这样更容易把传统纹样理解为有结构、有逻辑、可继续转化的视觉内容。"
        )
    with intro_right:
        render_section_heading("建议观看方式", "先看图谱，再看真实绣片，最后带着理解进入导览与设计模块")
        st.markdown("- 先认名称与类型")
        st.markdown("- 再看构图与主辅关系")
        st.markdown("- 再看真实绣片中的针脚与层次")
        st.markdown("- 最后带着理解进入导览、共创与产品化页面")

    st.divider()
    overview_cols = st.columns(4, gap="large")
    with overview_cols[0]:
        st.metric("典型纹样", str(len(pattern_atlas_items)), help="当前图谱卡片数量")
    with overview_cols[1]:
        st.metric("真实扫图", str(len(pattern_scan_items)), help="当前可浏览的真实刺绣扫图数量")
    with overview_cols[2]:
        st.metric("阅读重点", "构图 + 工艺", help="不仅看图案，也看层次、组织与针脚关系")
    with overview_cols[3]:
        st.metric("适合用途", "理解 / 教学 / 转化", help="既适合观众浏览，也适合后续设计参考")

    st.divider()
    render_section_heading("典型纹样图谱", "先建立对名称、类别、载体与视觉特征的基础印象")
    selected_filter = st.radio("按类型查看", CATEGORY_OPTIONS, horizontal=True, key="pattern_filter")
    visible_items = [
        item for item in pattern_atlas_items if selected_filter == "全部" or item["category"] == selected_filter
    ]

    if not visible_items:
        st.info("当前筛选条件下暂无纹样内容。")
        return

    for start in range(0, len(visible_items), 2):
        cols = st.columns(2, gap="large")
        for col, item in zip(cols, visible_items[start : start + 2]):
            with col:
                st.markdown(f"#### {item['name']}")
                st.caption(item["category"])
                try:
                    st.image(item["image"], use_container_width=True)
                except Exception:
                    st.warning("该纹样图片暂时无法显示。")
                st.write(item["summary"])
                st.caption(f"标签：{' / '.join(item['tags'])}")
                info_col1, info_col2 = st.columns(2, gap="medium")
                with info_col1:
                    st.markdown("**常见位置 / 载体**")
                    st.write(item["carrier"])
                with info_col2:
                    st.markdown("**视觉关键词**")
                    st.write("、".join(item["keywords"]))
                st.markdown("**观察要点**")
                for feature in item["features"]:
                    st.markdown(f"- {feature}")

    st.divider()
    render_section_heading("真实刺绣扫图", "把图谱里的印象带回真实绣片，观察细节、层次和工艺痕迹")
    selected_scan_filter = st.radio("按扫图类别查看", SCAN_CATEGORY_OPTIONS, horizontal=True, key="pattern_scan_filter")
    visible_scan_items = [
        item for item in pattern_scan_items if selected_scan_filter == "全部" or item["category"] == selected_scan_filter
    ]

    if visible_scan_items:
        scan_cols = st.columns(3, gap="large")
        for idx, item in enumerate(visible_scan_items):
            with scan_cols[idx % 3]:
                try:
                    st.image(item["image"], use_container_width=True)
                except Exception:
                    st.warning("该扫图暂时无法显示。")
                st.markdown(f"#### {item['name']}")
                st.caption(f"类别：{item['category']}｜对应纹样：{item['related_pattern']}")
                st.write(item["caption"])
    else:
        st.info("当前筛选条件下暂无扫图内容。")

    st.divider()
    detail_cols = st.columns(2, gap="large")
    with detail_cols[0]:
        render_section_heading("看图时可以重点注意", "如果第一次接触侗绣纹样，可以先从这几个角度观察")
        st.markdown("- 它是中心式构图、对称式构图，还是连续带状组织？")
        st.markdown("- 画面里谁是主纹，谁是陪衬或边饰？")
        st.markdown("- 它更强调放射、围合、重复，还是上下生长关系？")
        st.markdown("- 真实绣片里哪些部分最能看出层次、针脚和密度变化？")
    with detail_cols[1]:
        render_section_heading("看完之后可以去哪里", "这页建立基础理解，后续可以带着问题继续深入")
        st.markdown("- 去智能导览：继续追问某个纹样的寓意、用法和讲解口径")
        st.markdown("- 去 AI 共创实验：把观察到的特征转成设计提案与创意文案")
        st.markdown("- 去 AI 设计流程：理解传统纹样如何进入数字转化")
        st.markdown("- 去文创展示与场景应用：看这些纹样如何进入产品与传播场景")
