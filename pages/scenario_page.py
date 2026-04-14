import streamlit as st
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
PATTERN_DIR = ASSETS_DIR / "patterns"
SHOWCASE_DIR = ASSETS_DIR / "showcase"


SCENARIO_APPLICATIONS = [
    {
        "title": "虚拟博物馆沉浸导览",
        "subtitle": "角色引导、展厅浏览、互动问答",
        "desc": "让用户从‘进入展厅’开始理解侗绣，而不是只停留在静态浏览层。",
    },
    {
        "title": "展馆 / 景区数字讲解",
        "subtitle": "扫码导览、展签生成、故事化讲述",
        "desc": "把静态展板延展成可讲解、可提问、可继续传播的数字入口。",
    },
    {
        "title": "研学课堂与美育活动",
        "subtitle": "课程包、任务卡、共创工作坊",
        "desc": "让侗绣纹样从‘被看见’走向‘被理解、被讲述、被动手表达’。",
    },
    {
        "title": "文创传播与品牌联动",
        "subtitle": "IP 延展、周边设计、社媒内容",
        "desc": "把纹样、故事和角色统一成更容易被年轻人记住的文化表达。",
    },
]

B_SIDE_USERS = [
    "虚拟博物馆 / 数字展陈项目方",
    "景区与文旅项目方",
    "博物馆、非遗馆、文化馆",
    "高校与中小学研学机构",
    "文创品牌与设计机构",
]

C_SIDE_USERS = [
    "年轻消费者",
    "国潮与非遗爱好者",
    "旅游用户",
    "学生群体",
    "设计从业者与创作者",
]

BUSINESS_MODELS = [
    "平台部署与内容定制",
    "虚拟导览合作",
    "课程包与工作坊服务",
    "IP 形象与文创衍生授权",
    "品牌联名与传播内容共创",
]

PATTERN_MEANINGS = [
    ("太阳花纹", "光明、吉祥与生命力"),
    ("对鸟纹", "平安、和合与幸福"),
    ("蝴蝶纹", "自由、美好与灵动气息"),
    ("八角花纹", "圆满、规整与秩序之美"),
    ("小龙纹", "守护、图腾与精神力量"),
]

IP_FEATURES = [
    "以侗族传统椎髻、银饰、彩线流苏为识别特征，保留民族服饰的精神气质。",
    "服饰以黑、蓝、红、白为主色，融入太阳花纹、对鸟纹、蝴蝶纹与几何挑花纹样。",
    "手持小绣绷或未完成绣片，强调她不是静态吉祥物，而是会讲、会绣、会陪伴的导览角色。",
]

IP_PERSONA = [
    "温柔灵动，耐心细致，带着侗乡日常生活里的亲切感。",
    "熟悉平绣、打籽绣、辫绣、锁绣、挑花等技法，也懂纹样背后的生活寓意。",
    "喜欢在鼓楼旁看阿妈刺绣，在风雨桥上给游客讲侗乡故事。",
    "她的使命，是让侗族刺绣从被观看，走向被理解、被喜爱、被继续使用。",
]

LANDING_PATH = [
    "从虚拟博物馆或专题入口进入，由角色先带用户建立情感连接。",
    "再以重点纹样为线索，把图案、工艺、服饰和侗族生活联系起来。",
    "随后延展到扫图、导览问答、展签内容和场景故事。",
    "最后落到课堂活动、展陈设计、文创周边与社媒传播。",
]

PRODUCT_IDEAS = [
    "角色徽章、贴纸、亚克力立牌、收藏卡",
    "侗绣主题帆布袋、手机壳、杯套、抱枕、书签",
    "虚拟博物馆限定导览卡、角色明信片、纹样卡片",
    "适合研学场景的任务手册、拼贴包、识纹样互动材料",
]

SHOWCASE_IMAGES = [
    (SHOWCASE_DIR / "mockups" / "phonecase_longwen.png", "鼓楼意象的手机壳应用"),
    (SHOWCASE_DIR / "mockups" / "fridge_magnet.png", "适合做旅游纪念品的小体量文创"),
    (SHOWCASE_DIR / "generated" / "taiyanghua_generated.png", "太阳花纹的视觉转化效果"),
    (SHOWCASE_DIR / "generated" / "fusion_generated.png", "多种纹样融合后的当代表达"),
    (SHOWCASE_DIR / "postcards" / "longwen_postcard.png", "适合展陈延展的明信片类载体"),
    (SHOWCASE_DIR / "postcards" / "taiyanghua_postcard.png", "适合收藏传播的纹样卡片"),
]


def _asset(path: Path) -> str:
    return str(path)


def _render_bullets(items):
    for item in items:
        st.markdown(f"- {item}")


def render_scenario_page(*, render_section_heading):
    st.title("场景落地")
    st.caption("这一页负责回答：平台不只是在展示侗绣内容，还能如何进入展馆、课堂、文旅与品牌传播等真实使用场景。")
    st.divider()

    intro_left, intro_right = st.columns([1.05, 0.95], gap="large")
    with intro_left:
        render_section_heading("这一页在平台里承担什么角色", "它不是功能说明页，而是平台价值和落地方式的集中表达")
        st.write(
            "如果图谱页解决了‘看什么’，导览页解决了‘怎么理解’，设计工作台和文创展陈解决了‘怎么转化’，"
            "那么场景落地页更适合继续回答：这些内容最终怎样进入真实环境，被观众、学生、游客、机构和品牌真正使用。"
        )
        st.markdown("- 把前面几个页面的内容汇成一条真实使用路径")
        st.markdown("- 把技术能力翻译成展馆、课堂、文旅和传播中的具体体验")
        st.markdown("- 把项目从‘能演示’进一步讲成‘能落地、能合作、能持续延展’")
    with intro_right:
        st.info("这页最适合在答辩或路演时讲‘平台价值’，尤其适合承接虚拟博物馆、数字导览和文创传播这些场景。")
        metric_cols = st.columns(2, gap="medium")
        with metric_cols[0]:
            st.metric("页面角色", "落地价值页")
        with metric_cols[1]:
            st.metric("表达重点", "场景闭环")

    st.divider()
    path_cols = st.columns(4, gap="large")
    path_items = [
        ("阶段 1", "进入场景", "从虚拟博物馆、专题入口或展馆讲解页进入，让用户先愿意停留。"),
        ("阶段 2", "理解内容", "通过角色导览、纹样故事和问答内容，让知识不再只是静态展板。"),
        ("阶段 3", "继续转化", "再延展到设计工作台、文创展陈与课程活动，形成连续使用路径。"),
        ("阶段 4", "形成传播", "最后落到品牌联动、社媒传播、周边展示和长期合作。"),
    ]
    for col, item in zip(path_cols, path_items):
        step, title, desc = item
        with col:
            st.markdown(f"#### {step}")
            st.caption(title)
            st.write(desc)

    st.divider()
    render_section_heading("平台能进入哪些真实场景", "把页面功能翻译成可被理解的使用场景")
    scenario_cols = st.columns(4, gap="large")
    for col, item in zip(scenario_cols, SCENARIO_APPLICATIONS):
        with col:
            st.markdown(f"#### {item['title']}")
            st.caption(item["subtitle"])
            st.write(item["desc"])

    st.divider()
    render_section_heading("角色引入：让知识被更自然地讲出来", "角色不是装饰，而是场景落地里的讲述接口")
    ip_left, ip_right = st.columns([0.95, 1.05], gap="large")
    with ip_left:
        st.markdown("### 锦小绣")
        st.caption("侗族刺绣非遗守护精灵 · 侗乡文化小使者")
        st.write(
            "她以侗族传统刺绣与织锦纹样为核心视觉符号，是一个兼具民族气质与亲和力的数字导览形象。"
            "在场景页里，她承担的是‘带用户进入侗绣世界’的角色，而不只是提供视觉点缀。"
        )
        st.markdown("#### 形象特征")
        _render_bullets(IP_FEATURES)
    with ip_right:
        st.markdown("#### 她为什么对落地有帮助")
        st.write(
            "很多文化项目在传播时会卡在一个问题上：知识是对的，但不够好进入。"
            "角色的价值就在于，她能把纹样、工艺、生活和情感串成更容易被普通用户接受的讲述路径。"
        )
        st.write(
            "因此，当她出现在虚拟博物馆、扫码导览、课堂活动或文创传播中时，用户感受到的就不只是说明文本，"
            "而是一种有人带领、有人陪伴、有人解释的进入方式。"
        )

    st.divider()
    meaning_left, meaning_right = st.columns(2, gap="large")
    with meaning_left:
        render_section_heading("纹样为什么能进入这些场景", "因为它们不仅是图案，也承载故事、情感与祝愿")
        for name, meaning in PATTERN_MEANINGS:
            st.markdown(f"- **{name}**：{meaning}")
        st.write("当纹样本身有文化寓意、视觉识别度和讲述空间时，它们就天然适合进入导览、课程和传播内容。")
    with meaning_right:
        render_section_heading("角色可以怎么把它们讲活", "从纹样出发，再回到人、生活和场景")
        st.write(
            "她可以从太阳花纹讲到光明与祝福，从对鸟纹讲到和合与陪伴，从蝴蝶纹讲到灵动和美好，"
            "再把这些内容带回到侗族人的服饰、节庆和日常生活里。"
        )
        st.write("这样用户记住的就不只是一个纹样名称，而是一段更容易被感知和复述的文化体验。")

    st.divider()
    render_section_heading("视觉资源如何继续变成场景表达", "从原始纹样到设计成果，再进入真实使用环境")
    top_images = st.columns(3, gap="large")
    with top_images[0]:
        st.image(_asset(PATTERN_DIR / "duiniaowen.png"), caption="原始纹样：对鸟纹", use_container_width=True)
    with top_images[1]:
        st.image(_asset(PATTERN_DIR / "taiyanghuawen.png"), caption="主题纹样：太阳花纹", use_container_width=True)
    with top_images[2]:
        st.image(
            _asset(SHOWCASE_DIR / "mockups" / "phonecase_longwen.png"),
            caption="设计转化：纹样文创应用",
            use_container_width=True,
        )

    st.caption("这条路径适合被讲成：原始纹样 -> 导览理解 -> 设计转化 -> 场景传播。")

    showcase_row_1 = st.columns(3, gap="large")
    for col, (img_path, caption) in zip(showcase_row_1, SHOWCASE_IMAGES[:3]):
        with col:
            st.image(_asset(img_path), caption=caption, use_container_width=True)

    showcase_row_2 = st.columns(3, gap="large")
    for col, (img_path, caption) in zip(showcase_row_2, SHOWCASE_IMAGES[3:]):
        with col:
            st.image(_asset(img_path), caption=caption, use_container_width=True)

    st.divider()
    roadmap_left, roadmap_right = st.columns(2, gap="large")
    with roadmap_left:
        render_section_heading("一条更自然的落地路径", "从第一次接触，到形成记忆点和传播意愿")
        for idx, item in enumerate(LANDING_PATH, start=1):
            st.markdown(f"{idx}. {item}")
    with roadmap_right:
        render_section_heading("可以继续延展的文创方向", "让角色、纹样与使用场景形成统一识别")
        _render_bullets(PRODUCT_IDEAS)
        st.write("当角色形象、纹样语言和场景叙事统一后，这页就不只是在讲功能，也能承接展示、合作与传播。")

    st.divider()
    persona_left, persona_right = st.columns([0.95, 1.05], gap="large")
    with persona_left:
        render_section_heading("角色气质", "让非遗传播不再显得遥远")
        _render_bullets(IP_PERSONA)
    with persona_right:
        render_section_heading("为什么这页对项目表达很重要", "它最适合承接答辩里的‘真实价值’部分")
        st.markdown("- 它能把‘技术能力’翻译成‘真实使用场景’。")
        st.markdown("- 它能把‘纹样资料’转成‘有人讲述的文化内容’。")
        st.markdown("- 它能把‘虚拟博物馆’与‘IP 导览’连接成更完整的体验路线。")
        st.markdown("- 它能帮助老师、评审或合作方更快理解项目为什么值得落地。")

    st.divider()
    user_cols = st.columns(3, gap="large")
    with user_cols[0]:
        render_section_heading("适合的合作对象", "更偏展陈、文旅、教育与数字内容项目")
        _render_bullets(B_SIDE_USERS)
    with user_cols[1]:
        render_section_heading("适合的使用者", "更偏普通观众、学生与年轻文化用户")
        _render_bullets(C_SIDE_USERS)
    with user_cols[2]:
        render_section_heading("可延展的合作方式", "既能做展示，也能做长期传播与授权")
        _render_bullets(BUSINESS_MODELS)
