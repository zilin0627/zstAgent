import streamlit as st


def render_ai_workflow_page(*, ai_workflow_content: dict, asset_path):
    st.title("幕后方法")
    st.caption("解释为什么做、怎么整理、AI 做了什么，以及最终输出了什么。")
    st.divider()

    intro_left, intro_right = st.columns([1.15, 0.85], gap="large")
    with intro_left:
        st.markdown("### 从整理到生成")
        st.write(
            "这一页不是给所有人都必须详细看完的，而是给想继续了解过程的人一个更清晰的入口。"
            "它会展示纹样筛选、标签整理、模型训练和生成延展之间的大致关系。"
        )
        st.markdown("- 先整理纹样和标签。")
        st.markdown("- 再构建生成时需要的描述方式。")
        st.markdown("- 最后把结果延展到展示和设计应用中。")
    with intro_right:
        st.info("这里后续可替换为你 `纹样演示初稿9.18.pptx` 中的训练流程图、参数对比图或板块总结页。")

    st.markdown("### 工作流")
    workflow_cols = st.columns(5, gap="small")
    for col, step in zip(workflow_cols, ai_workflow_content["steps"]):
        with col:
            st.info(step)

    st.markdown("### 展板查看")
    board_tabs = st.tabs([item[0] for item in ai_workflow_content["boards"]])
    for tab, item in zip(board_tabs, ai_workflow_content["boards"]):
        _, image_path, bullets = item
        with tab:
            try:
                st.image(asset_path(image_path), width="stretch")
            except Exception:
                st.warning("该展板图片暂时无法显示。")
            st.caption("｜".join(bullets))

    st.divider()
    summary_col1, summary_col2 = st.columns(2, gap="large")
    with summary_col1:
        st.markdown("### 这部分我做了什么")
        for line in ai_workflow_content["work_summary"]:
            st.markdown(f"- {line}")
    with summary_col2:
        st.markdown("### 页面内直接展示")
        for line in ai_workflow_content["page_summary"]:
            st.markdown(f"- {line}")

    st.divider()
    extra_cols = st.columns(2, gap="large")
    with extra_cols[0]:
        st.markdown("### 可以继续补充什么")
        st.markdown("- `纹样演示初稿9.18.pptx`：适合补流程图和方法示意")
        st.markdown("- `侗绣纹样数据集整理.pdf`：适合补数据来源说明")
        st.markdown("- `详细标签分析.docx`：适合补标签整理依据")
    with extra_cols[1]:
        st.markdown("### 这一页适合谁看")
        st.markdown("- 对普通观众来说，可以简单看看‘这些图是怎么一步步来的’。")
        st.markdown("- 对课程、展示或比赛场景来说，可以把它当作过程说明页。")
        st.markdown("- 对设计相关用户来说，它也能帮助理解生成逻辑与延展方式。")

    st.divider()
    metric_cols = st.columns(4, gap="large")
    for col, item in zip(metric_cols, ai_workflow_content["metrics"]):
        label, value = item
        with col:
            st.metric(label, value)
