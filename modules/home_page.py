import streamlit as st


def render_home_page(
    *,
    guide_page: str,
    pattern_page: str,
    home_modules: list[dict],
    go_to,
    render_section_heading,
    render_metric,
):
    st.title("侗族刺绣纹样数字体验平台")
    st.caption(
        "从纹样图谱、文化讲解到文创延展与场景应用，"
        "这是一个面向非遗科普、文化展示与文旅传播的侗绣数字入口。"
    )
    st.divider()

    hero_left, hero_right = st.columns([1.15, 0.85], gap="large")
    with hero_left:
        st.markdown("## 这是什么")
        st.write(
            "这里不是单纯的资料列表，也不是只做图像生成的工具页。"
            "它更像一个从侗族刺绣进入的数字体验入口："
            "先看纹样，再理解它的构图、寓意和工艺特点，"
            "然后继续看到文创延展、设计转化和更具体的使用场景。"
        )
        st.write(
            "如果你第一次接触侗绣，可以先从纹样图谱和导览讲解进入；"
            "如果你更关心设计、文创或传播，也可以继续往后看文创展示、共创和场景应用。"
        )

        action_cols = st.columns(2, gap="medium")
        with action_cols[0]:
            if st.button("先看纹样图谱", key="home-entry-pattern", use_container_width=True):
                go_to(pattern_page)
                st.rerun()
        with action_cols[1]:
            if st.button("先看导览讲解", key="home-entry-guide", use_container_width=True):
                go_to(guide_page)
                st.rerun()

    with hero_right:
        render_section_heading("你可以从这里开始", "如果是第一次浏览，建议先从这两个入口进入")
        st.markdown("- 想先看图样、分类和构图特点，可以进入纹样图谱")
        st.markdown("- 想快速了解纹样的含义、用途和文化背景，可以进入智能导览")
        st.markdown("- 后面再继续看文创展示、共创和场景应用，会更容易串起来")

    st.divider()
    render_section_heading("为什么从侗绣纹样进入", "它不只是图案，也连接着服饰、工艺、生活与文化记忆")
    value_cols = st.columns(3, gap="large")
    value_items = [
        (
            "先看见纹样",
            "从龙纹、花纹、植物纹、几何纹等典型母题进入，先建立对侗绣视觉特点的第一印象。",
        ),
        (
            "再理解故事",
            "通过图谱、导览和讲解，去理解纹样背后的寓意、构图方式和刺绣工艺。",
        ),
        (
            "最后连接今天",
            "继续延展到文创、设计、展览、研学和文旅传播等今天的使用场景中。",
        ),
    ]
    for col, item in zip(value_cols, value_items):
        title, desc = item
        with col:
            st.markdown(f"#### {title}")
            st.write(desc)

    st.divider()
    render_section_heading("你可以这样浏览", "从看图到理解，再到延展应用，是一条比较自然的路径")
    chain_cols = st.columns(5, gap="medium")
    chain_items = [
        ("看见纹样", "先从典型图样、扫图和分类中建立对侗绣的初步印象。"),
        ("了解含义", "再通过导览讲解理解纹样、服饰和工艺之间的关系。"),
        ("观察细节", "继续看构图、色彩、载体和真实绣片中的视觉特点。"),
        ("进入延展", "再看看这些纹样如何被转化到文创、设计和数字生成中。"),
        ("回到场景", "最后放回展馆、研学、文旅和传播场景中去理解它的价值。"),
    ]
    for col, item in zip(chain_cols, chain_items):
        title, desc = item
        with col:
            st.markdown(f"#### {title}")
            st.write(desc)

    st.divider()
    metrics_cols = st.columns(4, gap="large")
    with metrics_cols[0]:
        render_metric("浏览路径", "5 步", "从看见纹样到理解故事，再到延展和应用")
    with metrics_cols[1]:
        render_metric("当前模块", "7 页", "首页、图谱、导览、共创、流程、文创、场景应用")
    with metrics_cols[2]:
        render_metric("平台重点", "体验 + 科普", "非遗讲解、文化展示和数字体验")
    with metrics_cols[3]:
        render_metric("后续内容", "持续补充", "后面会继续接入展陈、侗寨、生成图和文创成果")

    st.divider()
    info_left, info_right = st.columns(2, gap="large")
    with info_left:
        render_section_heading("现在可以看到什么", "这些内容已经构成了平台当前的主体部分")
        st.markdown("- 纹样图谱与真实扫图")
        st.markdown("- 智能导览与文化讲解")
        st.markdown("- AI 共创与设计提案")
        st.markdown("- AI 设计流程展示")
        st.markdown("- 文创展示与场景应用入口")
    with info_right:
        render_section_heading("后面还会继续补充什么", "平台会逐步接入更多真实来源与延展成果")
        st.markdown("- 展陈照片、侗寨实拍、服饰照片和展牌整理")
        st.markdown("- 传统纹样资料、工艺说明和更完整的文化线索")
        st.markdown("- 生成图、文创样机、纸品与礼赠方向成果")
        st.caption("这些内容会按页面需要逐步补进来，不会一次性全部堆在首页。")

    st.divider()
    render_section_heading("平台里的主要内容", "你可以从不同入口进入，但看到的是同一条侗绣理解路径")

    row1 = st.columns(2, gap="large")
    row2 = st.columns(2, gap="large")
    row3 = st.columns(2, gap="large")
    row4 = st.columns(1)
    home_rows = [row1, row2, row3, row4]

    module_index = 0
    for row in home_rows:
        for col in row:
            if module_index >= len(home_modules):
                continue
            module = home_modules[module_index]
            with col:
                st.markdown(f"#### {module['title']}")
                st.caption(module["tag"])
                st.write(module["desc"])
                st.info(module["highlight"])
                if st.button(f"进入 {module['title']}", key=f"home-{module['title']}", use_container_width=True):
                    go_to(module["title"])
                    st.rerun()
            module_index += 1

    st.divider()
    bottom_cols = st.columns(3, gap="large")
    with bottom_cols[0]:
        render_section_heading("建议浏览顺序", "第一次进入时，这样看会更顺")
        st.markdown("1. 先在首页建立整体印象。")
        st.markdown("2. 再进入纹样图谱，看典型母题和扫图。")
        st.markdown("3. 通过智能导览理解讲解、展签和工艺说明。")
        st.markdown("4. 再看文创展示、共创和设计流程。")
        st.markdown("5. 最后看场景应用，理解它如何进入今天的生活和传播。")
    with bottom_cols[1]:
        render_section_heading("适合谁使用", "不同人群可以从不同入口进入")
        st.markdown("- 普通观众：先看导览和图谱")
        st.markdown("- 学生与教师：先看图谱、导览和流程")
        st.markdown("- 设计方向：先看文创展示、共创和场景应用")
        st.markdown("- 文旅传播方向：先看首页、导览、展示和场景")
    with bottom_cols[2]:
        render_section_heading("它更接近什么", "这不是单一工具，而是一个偏文化体验的数字平台")
        st.markdown("- 非遗科普入口")
        st.markdown("- 文化展示页面")
        st.markdown("- 文旅传播内容载体")
        st.markdown("- 侗绣纹样数字体验与延展平台")