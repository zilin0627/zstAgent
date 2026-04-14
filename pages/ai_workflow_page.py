import streamlit as st


def _render_bullets(items):
    for item in items or []:
        st.markdown(f"- {item}")


def _render_kv_cards(items, columns=3):
    if not items:
        return
    cols = st.columns(columns, gap="large")
    for idx, item in enumerate(items):
        with cols[idx % columns]:
            st.markdown(f"### {item.get('title', '')}")
            if item.get("tag"):
                st.caption(item["tag"])
            if item.get("desc"):
                st.write(item["desc"])


def _render_table(title, rows):
    st.markdown(f"### {title}")
    if rows:
        st.table(rows)
    else:
        st.info("暂无数据")


def _render_section_title(title: str, desc: str | None = None):
    st.markdown(f"## {title}")
    if desc:
        st.caption(desc)


def render_ai_workflow_page(*, ai_workflow_content: dict, asset_path):
    st.title(ai_workflow_content.get("title", "AI 工作流"))
    st.caption(
        ai_workflow_content.get(
            "subtitle",
            "展示平台的核心技术路线、知识库构建方式与 Agent 编排能力。",
        )
    )
    st.divider()

    hero_left, hero_right = st.columns([1.25, 0.75], gap="large")
    with hero_left:
        _render_section_title("这页到底在讲什么")
        st.write(
            ai_workflow_content.get(
                "positioning",
                "这是一个面向文创设计场景的 AI 辅助设计平台。",
            )
        )
        _render_bullets(ai_workflow_content.get("positioning_points", []))

    with hero_right:
        st.info(
            ai_workflow_content.get(
                "hero_note",
                "项目不是单点调用模型，而是围绕知识、工具、模型与输出场景构建完整 AI 工作流。",
            )
        )
        st.metric("项目表达重点", "AI 辅助设计平台")
        st.metric("核心能力", "RAG + Agent")

    st.divider()
    _render_section_title("为什么要做这套工作流", "先讲问题，再讲系统价值，答辩时会更顺")
    pain_left, pain_right = st.columns(2, gap="large")
    with pain_left:
        st.markdown("### 设计与内容生产中的真实痛点")
        _render_bullets(ai_workflow_content.get("pain_points", []))
    with pain_right:
        st.markdown("### 这套平台解决什么问题")
        _render_bullets(ai_workflow_content.get("value_points", []))

    st.divider()
    _render_section_title("完整工作流", "把资料获取、知识增强、工具编排和设计输出连成一条链")
    _render_kv_cards(ai_workflow_content.get("steps", []), columns=5)

    st.divider()
    _render_section_title("知识库底座怎么搭的", "这一部分是项目技术可信度的关键")
    kb_sections = ai_workflow_content.get("knowledge_base_sections", [])
    if kb_sections:
        kb_tabs = st.tabs([item["title"] for item in kb_sections])
        for tab, item in zip(kb_tabs, kb_sections):
            with tab:
                st.markdown(f"### {item['title']}")
                if item.get("summary"):
                    st.write(item["summary"])
                _render_bullets(item.get("bullets", []))
                if item.get("code"):
                    st.code(item["code"], language=item.get("code_language", "python"))
    else:
        st.info("暂无知识库结构说明。")

    st.divider()
    _render_section_title("系统核心：RAG 与 Agent 如何配合", "这部分最适合比赛和面试时重点展开")
    core_left, core_right = st.columns(2, gap="large")

    with core_left:
        st.markdown("### RAG 检索增强链路")
        _render_bullets(ai_workflow_content.get("rag_flow", []))
        st.markdown("### 当前已经落地的能力")
        _render_bullets(ai_workflow_content.get("implemented_points", []))

    with core_right:
        st.markdown("### Agent 工作流编排")
        _render_bullets(ai_workflow_content.get("agent_flow", []))
        st.markdown("### 可视化编排怎么映射")
        _render_bullets(ai_workflow_content.get("dify_mapping", []))

    st.divider()
    _render_section_title("为什么它比通用 AI 更适合这个场景", "不是否定通用模型，而是强调垂直知识增强后的差异")
    advantage_sections = ai_workflow_content.get("advantage_sections", [])
    if advantage_sections:
        compare_tabs = st.tabs([item["title"] for item in advantage_sections])
        for tab, item in zip(compare_tabs, advantage_sections):
            with tab:
                st.markdown(f"### {item['title']}")
                if item.get("summary"):
                    st.write(item["summary"])
                _render_bullets(item.get("bullets", []))
    else:
        st.info("暂无优势说明。")

    _render_table("通用 AI 与本平台的对比", ai_workflow_content.get("compare_table", []))

    st.divider()
    _render_section_title("最终能输出什么", "这一页要把技术和业务结果接起来")
    _render_kv_cards(ai_workflow_content.get("outputs", []), columns=4)

    st.divider()
    _render_section_title("可视化展板 / 架构示意", "适合展示截图、录屏或答辩时辅助说明")
    boards = ai_workflow_content.get("boards", [])
    if boards:
        board_tabs = st.tabs([item[0] for item in boards])
        for tab, item in zip(board_tabs, boards):
            _, image_path, bullets = item
            with tab:
                try:
                    _, img_col, _ = st.columns([0.5, 3, 0.5])
                    with img_col:
                        st.image(asset_path(image_path), use_container_width=True)
                except Exception:
                    st.warning("该图片暂时无法显示。")
                if bullets:
                    st.caption("｜".join(bullets))
    else:
        st.info("暂无展板内容。")

    st.divider()
    advance_left, advance_right = st.columns(2, gap="large")
    with advance_left:
        st.markdown("## 后续还能继续怎么增强")
        _render_bullets(ai_workflow_content.get("next_steps", []))
    with advance_right:
        st.markdown("## 比赛 / 面试时建议怎么讲")
        _render_bullets(ai_workflow_content.get("interview_points", []))

    st.divider()
    summary_left, summary_right = st.columns(2, gap="large")
    with summary_left:
        st.markdown("## 这部分体现了我做了什么")
        _render_bullets(ai_workflow_content.get("work_summary", []))
    with summary_right:
        st.markdown("## 推荐讲述顺序")
        _render_bullets(ai_workflow_content.get("page_summary", []))

    st.divider()
    _render_section_title("一眼能记住的平台关键词")
    metric_cols = st.columns(4, gap="large")
    metrics = ai_workflow_content.get("metrics", [])
    for col, item in zip(metric_cols, metrics):
        label, value = item
        with col:
            st.metric(label, value)
