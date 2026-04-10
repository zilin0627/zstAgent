import streamlit as st


def render_ai_workflow_page(*, ai_workflow_page: str, workflow_images: dict[str, str], render_metric, render_section_heading):
    st.title(ai_workflow_page)
    st.caption("从纹样灵感到当代视觉表达，向观众展示侗绣元素如何被看见、理解与再设计。")
    st.divider()

    intro_left, intro_right = st.columns([1.08, 0.92], gap="large")
    with intro_left:
        st.markdown("## 从传统纹样走向当代视觉")
        st.write(
            "这一页不再强调技术细节本身，而是更适合观众理解的方式，"
            "去展示侗绣纹样如何从图像观察出发，逐步进入视觉转化、创意生成与实际应用。"
        )
        st.markdown("- 先看见纹样本身的结构、色彩与节奏。")
        st.markdown("- 再提炼能够进入现代设计语境的视觉特征。")
        st.markdown("- 最后把这些特征延展到文创、海报、包装与传播场景中。")
    with intro_right:
        st.markdown("### 页面导览")
        st.info("这一页更偏向观众浏览体验：先理解纹样如何被转化，再看到它如何进入当代视觉与应用场景。")
        st.markdown("- 适合展览浏览")
        st.markdown("- 适合课程展示")
        st.markdown("- 适合作品集截图")
        st.markdown("- 适合项目打包演示")

    st.divider()
    overview_cols = st.columns(4, gap="large")
    with overview_cols[0]:
        render_metric("观看重点", "纹样转化", "更强调观众能看懂的视觉转化过程")
    with overview_cols[1]:
        render_metric("内容结构", "4 段", "从观察、提炼到延展与应用")
    with overview_cols[2]:
        render_metric("呈现方式", "图像 + 说明", "减少参数堆叠，强化浏览体验")
    with overview_cols[3]:
        render_metric("适合场景", "展示 / 上传", "更适合直接给老师、评审或观众浏览")

    st.divider()
    stage_cols = st.columns(4, gap="medium")
    stages = [
        ("01", "纹样观察", "从龙纹、花纹、树纹等典型母题中识别核心图形特征。"),
        ("02", "视觉提炼", "保留对称、放射、围合、层级等具有代表性的形式语言。"),
        ("03", "风格延展", "把传统纹样转化为更适合海报、包装与数字传播的视觉表达。"),
        ("04", "应用呈现", "让生成结果回到文创展示、场景应用与平台互动中。"),
    ]
    for col, item in zip(stage_cols, stages):
        idx, title, desc = item
        with col:
            st.markdown(f"#### {idx}")
            st.markdown(f"**{title}**")
            st.write(desc)

    st.divider()
    story_left, story_right = st.columns([1.0, 1.0], gap="large")
    with story_left:
        render_section_heading("观众可以看到什么", "更像一条完整的视觉故事线，而不是技术说明书")
        st.markdown("- 侗绣纹样有哪些容易被一眼识别的图形特点")
        st.markdown("- 传统纹样进入现代视觉后，哪些特征被保留下来")
        st.markdown("- 同一类纹样如何在不同载体上呈现不同气质")
        st.markdown("- 这些视觉结果最后如何进入文创和传播场景")
    with story_right:
        render_section_heading("页面不重点展开的内容", "避免把后台思路全部暴露给普通观众")
        st.markdown("- 不详细展开训练参数与工程配置")
        st.markdown("- 不直接展示完整提示词编写逻辑")
        st.markdown("- 不把内部资料整理过程逐项摊开")
        st.markdown("- 保留必要的说明，但以观众可理解的语言表达")

    st.divider()
    gallery_cols = st.columns(3, gap="large")
    gallery_items = [
        ("纹样与文创延展", workflow_images["showcase"], "展示纹样如何进入明信片、包装和样机场景。"),
        ("视觉整理与生成过渡", workflow_images["workflow"], "强调从纹样观察到视觉转化的连续关系。"),
        ("元素分析与结果呈现", workflow_images["analysis"], "让观众看到图案元素如何发展为新的视觉结果。"),
    ]
    for col, item in zip(gallery_cols, gallery_items):
        title, image_path, desc = item
        with col:
            try:
                st.image(image_path, use_container_width=True)
            except Exception:
                st.warning("该图片暂时无法显示。")
            st.markdown(f"#### {title}")
            st.caption(desc)

    st.divider()
    value_cols = st.columns([1.05, 0.95], gap="large")
    with value_cols[0]:
        render_section_heading("这些视觉结果最后会去哪里", "把页面和平台其它模块连接起来")
        st.markdown("- 在纹样图谱中，它帮助观众理解哪些特征被保留下来。")
        st.markdown("- 在 AI 共创实验中，它变成更直观的设计灵感来源。")
        st.markdown("- 在文创展示中，它继续落到海报、包装、配饰与周边。")
        st.markdown("- 在场景应用中，它进一步进入展览、课堂与传播内容。")
    with value_cols[1]:
        render_section_heading("更适合上传与展示的原因", "页面尽量收口到清晰、稳定、观众友好的结构")
        st.markdown("- 页面命名更自然，不再用“展板1/2/3”做主结构")
        st.markdown("- 内容更偏结果展示，不暴露过多内部方法细节")
        st.markdown("- 结构更适合截图、录屏、汇报和打包展示")
