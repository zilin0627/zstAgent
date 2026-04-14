import streamlit as st


VIEW_OPTIONS = ["平面成果", "产品样机", "生成延展"]


def _render_gallery_items(items, *, asset_path, columns: int, title_mode: str = "caption"):
    gallery_cols = st.columns(columns, gap="large")
    for idx, item in enumerate(items):
        title, image_path = item
        with gallery_cols[idx % columns]:
            try:
                st.image(asset_path(image_path), use_container_width=True)
            except Exception:
                st.warning("图片暂时无法显示。")
            if title_mode == "caption":
                st.caption(title)
            else:
                st.markdown(f"**{title}**")


def render_cultural_page(*, cultural_showcase: dict, asset_path):
    st.title("文创展陈")
    st.caption("这一页展示纹样如何从知识内容走向平面视觉、产品样机与生成延展，更像设计成果区而不是单纯图片浏览页。")
    st.divider()

    intro_left, intro_right = st.columns([1.05, 0.95], gap="large")
    with intro_left:
        st.markdown("### 这一页在平台里承担什么角色")
        st.write(
            "如果前面的图谱页解决了‘有哪些纹样’，导览页解决了‘这些纹样意味着什么’，"
            "那么这页更适合继续回答：这些纹样怎样被转化为可展示、可传播、可继续设计的成果。"
        )
        st.markdown("- 先看平面成果，观察纹样如何进入视觉版面")
        st.markdown("- 再看产品样机，理解它如何进入具体物件和日常载体")
        st.markdown("- 最后看生成延展，对比传统纹样与新风格之间的关系")
    with intro_right:
        st.info("建议把这一页讲成‘设计转化成果展示’，它比单纯说‘我放了一些图片’更有平台感。")
        metric_cols = st.columns(2, gap="medium")
        with metric_cols[0]:
            st.metric("成果类型", "平面 / 样机 / 生成")
        with metric_cols[1]:
            st.metric("页面角色", "设计成果页")

    st.divider()
    metric_cols = st.columns(4, gap="large")
    for col, item in zip(metric_cols, cultural_showcase["metrics"]):
        label, value = item
        with col:
            st.metric(label, value)

    st.divider()
    path_cols = st.columns(3, gap="large")
    path_items = [
        ("阶段 1", "平面成果", "先看明信片和视觉稿，更容易观察纹样布局、装饰感和版面节奏。"),
        ("阶段 2", "产品样机", "再看手机壳、冰箱贴等样机，理解纹样如何进入具体产品载体。"),
        ("阶段 3", "生成延展", "最后看 AIGC 延展，观察传统纹样与扩展风格之间的关系。"),
    ]
    for col, item in zip(path_cols, path_items):
        step, title, desc = item
        with col:
            st.markdown(f"#### {step}")
            st.caption(title)
            st.write(desc)

    st.divider()
    st.markdown("### 分类查看")
    filter_cols = st.columns([0.26, 0.74], gap="large")
    with filter_cols[0]:
        selected_view = st.radio("浏览方式", VIEW_OPTIONS, label_visibility="collapsed")
    with filter_cols[1]:
        if selected_view == "平面成果":
            st.caption("这部分最适合展示纹样如何进入海报、明信片和展陈类视觉物料。")
            _render_gallery_items(
                cultural_showcase["postcards"],
                asset_path=asset_path,
                columns=4,
                title_mode="caption",
            )
        elif selected_view == "产品样机":
            st.caption("这部分更强调纹样从视觉元素走向具体物件后的应用状态。")
            _render_gallery_items(
                cultural_showcase["mockups"],
                asset_path=asset_path,
                columns=2,
                title_mode="markdown",
            )
        else:
            st.caption("这部分用于展示纹样在生成式设计中的扩展方向，适合讲 AIGC 参与设计表达。")
            _render_gallery_items(
                cultural_showcase["generated"],
                asset_path=asset_path,
                columns=3,
                title_mode="caption",
            )

    st.divider()
    detail_left, detail_right = st.columns([1.15, 0.85], gap="large")
    with detail_left:
        st.markdown("### 这些成果体现了什么")
        st.markdown("- 纹样不只是静态文化素材，还可以成为平面与产品设计的视觉资源")
        st.markdown("- 图谱、导览和设计工作台并不是孤立页面，而是可以继续产出成果的前序环节")
        st.markdown("- 通过样机和生成图展示，平台更容易被讲成‘设计转化链路’，而不是‘图文展示站’")
        st.markdown("- 这部分也能自然支撑比赛里的成果展示、设计验证和落地表达")
    with detail_right:
        st.markdown("### 这些图还能继续怎么用")
        st.markdown("- 平面：海报、明信片、展陈物料")
        st.markdown("- 周边：冰箱贴、手机壳、帆布包、笔记本")
        st.markdown("- 礼赠：丝巾、礼盒包装、伴手礼")
        st.markdown("- 活动：课程材料、主题视觉、节庆物料")

    st.divider()
    bottom_left, bottom_right = st.columns(2, gap="large")
    with bottom_left:
        st.markdown("### 这一页适合怎么讲")
        st.markdown("- 先说这些成果来自侗绣纹样的整理与转化，而不是随意拼贴")
        st.markdown("- 再说平台不仅能理解纹样，还能把纹样继续带到平面、产品和生成设计中")
        st.markdown("- 最后强调这是一条从知识到设计成果的连续路径")
    with bottom_right:
        st.markdown("### 浏览建议")
        st.markdown("- 先看平面成果，理解纹样本身的版面表达")
        st.markdown("- 再看产品样机，判断它进入物件后的呈现状态")
        st.markdown("- 最后看生成延展，比较传统纹样和当代扩展之间的变化")
