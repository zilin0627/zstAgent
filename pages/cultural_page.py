import streamlit as st


def render_cultural_page(*, cultural_showcase: dict, asset_path):
    st.title("文创展陈")
    st.caption("按平面、产品和生成延展分组浏览，让页面更像作品展陈区。")
    st.divider()

    st.markdown("### 从图案到日常物件")
    st.write(
        "这一页不再放展板式主图，而是把重心交给作品本身。"
        "你可以把它理解成一个轻量的作品陈列区：先看平面，再看产品，最后看生成延展。"
    )

    metric_cols = st.columns(4, gap="large")
    for col, item in zip(metric_cols, cultural_showcase["metrics"]):
        label, value = item
        with col:
            st.metric(label, value)

    st.divider()
    st.markdown("### 分类查看")
    filter_cols = st.columns([0.26, 0.74], gap="large")
    with filter_cols[0]:
        selected_view = st.radio("浏览方式", ["明信片", "产品样机", "生成延展"], label_visibility="collapsed")
    with filter_cols[1]:
        if selected_view == "明信片":
            st.caption("先看平面作品，比较容易观察纹样本身的布局和装饰感。")
            postcard_cols = st.columns(4, gap="large")
            for col, item in zip(postcard_cols, cultural_showcase["postcards"]):
                title, image_path = item
                with col:
                    try:
                        st.image(asset_path(image_path), width="stretch")
                    except Exception:
                        st.warning("图片暂时无法显示。")
                    st.caption(title)
        elif selected_view == "产品样机":
            st.caption("再看产品样机，会更容易感受到纹样进入日常物件后的状态。")
            mockup_cols = st.columns(2, gap="large")
            for idx, item in enumerate(cultural_showcase["mockups"]):
                title, image_path = item
                with mockup_cols[idx % 2]:
                    try:
                        st.image(asset_path(image_path), width="stretch")
                    except Exception:
                        st.warning("图片暂时无法显示。")
                    st.markdown(f"**{title}**")
        else:
            st.caption("最后看生成延展，可以对比传统纹样和扩展风格之间的关系。")
            extension_cols = st.columns(3, gap="large")
            for idx, item in enumerate(cultural_showcase["generated"]):
                title, image_path = item
                with extension_cols[idx % 3]:
                    try:
                        st.image(asset_path(image_path), width="stretch")
                    except Exception:
                        st.warning("图片暂时无法显示。")
                    st.caption(title)

    st.divider()
    value_cols = st.columns([1.2, 0.8], gap="large")
    with value_cols[0]:
        st.markdown("### 这些图还能继续怎么用")
        st.markdown("- 平面：海报、明信片、展陈物料")
        st.markdown("- 周边：冰箱贴、手机壳、帆布包、笔记本")
        st.markdown("- 礼赠：丝巾、礼盒包装、伴手礼")
        st.markdown("- 活动：课程材料、主题视觉、节庆物料")
    with value_cols[1]:
        st.markdown("### 浏览建议")
        st.markdown("先看平面，再看产品，最后看生成延展，会更容易比较纹样在不同载体中的变化。")
