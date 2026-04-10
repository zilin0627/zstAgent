import streamlit as st


def render_scenario_page(*, scenario_page: str, render_section_heading):
    st.title(scenario_page)
    st.caption("围绕展陈、教育、品牌传播与数字媒介，展示纹样的应用落地场景。")
    st.divider()

    scenario_cols = st.columns(4, gap="large")
    scenario_data = [
        ("展陈导览", "展签、导视系统、互动问答屏", "适合博物馆、校园展和主题展。"),
        ("教育研学", "课程包、活动手册、手作工作坊", "让纹样从看见转变为理解与参与。"),
        ("品牌视觉", "主 KV、包装系统、节日礼盒", "增强品牌的文化辨识度。"),
        ("数字传播", "网页专题、短视频包装、社媒素材", "适合做更轻量的内容传播。"),
    ]
    for col, item in zip(scenario_cols, scenario_data):
        title, subtitle, desc = item
        with col:
            st.markdown(f"#### {title}")
            st.caption(subtitle)
            st.write(desc)

    st.divider()
    roadmap_left, roadmap_right = st.columns(2, gap="large")
    with roadmap_left:
        render_section_heading("典型流程", "从看懂纹样到形成具体应用的常见路径")
        st.markdown("1. 先通过智能导览获取背景说明与关键词。")
        st.markdown("2. 再到纹样图谱确认图形结构和常见载体。")
        st.markdown("3. 结合共创实验整理海报、包装或课程方向。")
        st.markdown("4. 最后落到展览、教学、品牌或传播场景中。")
    with roadmap_right:
        render_section_heading("落地关注点", "评估一个方案是否真正适合使用时可重点看这些方面")
        st.markdown("- 信息是否清楚易懂")
        st.markdown("- 互动体验是否自然")
        st.markdown("- 纹样表达是否准确")
        st.markdown("- 是否方便继续传播和延展")
