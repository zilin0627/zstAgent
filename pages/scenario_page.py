import streamlit as st


SCENARIO_APPLICATIONS = [
    {
        "title": "景区 / 展馆数字导览",
        "subtitle": "扫码讲解、展签生成、互动问答",
        "desc": "适合博物馆、校园展和主题展，可作为沉浸式文化体验入口。",
    },
    {
        "title": "研学课堂与美育教育",
        "subtitle": "课程包、活动手册、工作坊",
        "desc": "让纹样从看见转变为理解与参与，适合美育课程和研学活动。",
    },
    {
        "title": "品牌文创共创",
        "subtitle": "主 KV、包装系统、节日礼盒",
        "desc": "增强品牌的文化辨识度，也更贴近国潮文创赛道表达。",
    },
    {
        "title": "数字传播与社媒扩散",
        "subtitle": "网页专题、短视频包装、社媒素材",
        "desc": "适合做更轻量的内容传播，提升年轻用户触达与二次扩散。",
    },
]

B_SIDE_USERS = [
    "景区与文旅项目方",
    "博物馆、非遗馆、文化馆",
    "高校与中小学研学机构",
    "文创品牌与设计机构",
    "地方政府及乡村振兴项目单位",
]

C_SIDE_USERS = [
    "年轻消费者",
    "国潮与非遗爱好者",
    "旅游用户",
    "学生群体",
    "设计从业者与创作者",
]

BUSINESS_MODELS = [
    "平台部署与定制服务",
    "文创产品销售",
    "品牌联名合作",
    "课程与工作坊",
    "数字内容授权",
]


def render_scenario_page(*, render_section_heading):
    st.title("场景落地")
    st.caption("展示平台如何在展馆、课堂、品牌和传播场景中被真正使用。")
    st.divider()

    intro_left, intro_right = st.columns([1.12, 0.88], gap="large")
    with intro_left:
        st.markdown("### 常见使用方式")
        st.write(
            "如果把这个平台理解成一个内容入口，那么场景页更像是在回答：这些内容除了浏览之外，还能在哪里被看到、被使用、被继续展开。"
        )
    with intro_right:
        st.info("这里后续很适合补展馆设计图、课程页面截图或文创商城界面，让场景感更强。")

    scenario_cols = st.columns(4, gap="large")
    for col, item in zip(scenario_cols, SCENARIO_APPLICATIONS):
        with col:
            st.markdown(f"#### {item['title']}")
            st.caption(item["subtitle"])
            st.write(item["desc"])

    st.divider()
    roadmap_left, roadmap_right = st.columns(2, gap="large")
    with roadmap_left:
        render_section_heading("内容如何进入场景", "可以把它理解成一个自然的使用流程")
        st.markdown("1. 先从图谱或导览中理解纹样与文化线索。")
        st.markdown("2. 再根据主题需要选择更合适的视觉元素。")
        st.markdown("3. 接着延展到海报、包装、课程或展览说明中。")
        st.markdown("4. 最后形成更完整的展示、教学或传播内容。")
    with roadmap_right:
        render_section_heading("为什么值得继续展开", "从普通浏览走向更丰富的内容使用")
        st.markdown("- 在展览里，它可以帮助观众更容易看懂纹样。")
        st.markdown("- 在课堂里，它可以把知识讲解与图像观察结合起来。")
        st.markdown("- 在设计里，它可以作为视觉灵感和延展参考。")
        st.markdown("- 在传播里，它可以形成更完整的内容表达。")

    st.divider()
    user_cols = st.columns(3, gap="large")
    with user_cols[0]:
        render_section_heading("适合的合作对象", "更偏场馆、学校与内容项目")
        for item in B_SIDE_USERS:
            st.markdown(f"- {item}")
    with user_cols[1]:
        render_section_heading("适合的观看者", "更偏普通观众与内容使用者")
        for item in C_SIDE_USERS:
            st.markdown(f"- {item}")
    with user_cols[2]:
        render_section_heading("可以延展的方向", "不一定要强调商业，也可以先理解为应用方向")
        for item in BUSINESS_MODELS:
            st.markdown(f"- {item}")
