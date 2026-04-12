import streamlit as st
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
PATTERN_DIR = ASSETS_DIR / "patterns"
SHOWCASE_DIR = ASSETS_DIR / "showcase"


SCENARIO_APPLICATIONS = [
    {
        "title": "虚拟博物馆沉浸导览",
        "subtitle": "角色引导、展厅浏览、互动问答",
        "desc": "让用户从“进入展厅”开始理解侗绣，而不是只停留在静态浏览层。",
    },
    {
        "title": "展馆 / 景区数字讲解",
        "subtitle": "扫码导览、展签生成、故事化讲述",
        "desc": "把静态展板延展成可讲解、可提问、可继续传播的数字入口。",
    },
    {
        "title": "研学课堂与美育活动",
        "subtitle": "课程包、任务卡、共创工作坊",
        "desc": "让侗绣纹样从“被看见”走向“被理解、被讲述、被动手表达”。",
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


def render_scenario_page(*, render_section_heading):
    st.title("场景落地")
    st.caption("让侗绣从内容展示走向导览体验、文化讲述、文创转化与持续传播。")
    st.divider()

    intro_left, intro_right = st.columns([1.08, 0.92], gap="large")
    with intro_left:
        st.markdown("### 从“看见纹样”走向“走进侗绣世界”")
        st.write(
            "如果前面的图谱与导览解决了“有什么纹样”和“纹样是什么意思”，"
            "那么场景落地页更适合继续回答：这些内容怎样进入虚拟博物馆、线下展陈、课堂活动与文创传播，"
            "真正形成一个可以被观看、被讲述、被体验的文化闭环。"
        )
        st.write(
            "它不只是一个展示页，更像是侗绣内容从资料、图像、知识，逐渐走向角色、故事和日常使用场景的连接层。"
        )
    with intro_right:
        st.info(
            "结合你已有的侗族虚拟博物馆项目，这一页最适合承接“展厅入口 + 导览角色 + 纹样故事 + 文创转化”这条完整路线。"
        )

    scenario_cols = st.columns(4, gap="large")
    for col, item in zip(scenario_cols, SCENARIO_APPLICATIONS):
        with col:
            st.markdown(f"#### {item['title']}")
            st.caption(item["subtitle"])
            st.write(item["desc"])

    st.divider()
    render_section_heading("角色引入：让侗绣被更自然地讲出来", "一个能陪伴用户进入侗乡世界的数字小使者")
    ip_left, ip_right = st.columns([0.92, 1.08], gap="large")
    with ip_left:
        st.markdown("### 锦小绣")
        st.caption("侗族刺绣非遗守护精灵 · 侗乡文化小使者")
        st.write(
            "她以侗族传统刺绣与织锦纹样为核心视觉符号，是一个兼具民族气质与亲和力的数字导览形象。"
            "在页面里，她不是简单的卡通装饰，而是负责把纹样、生活与故事串联起来的讲述者。"
        )
        st.markdown("#### 形象印象")
        for item in IP_FEATURES:
            st.markdown(f"- {item}")
    with ip_right:
        st.markdown("#### 角色故事")
        st.write(
            "锦小绣像是从侗乡老绣娘的绣绷上醒来的一缕彩线。她熟悉鼓楼、风雨桥、寨门与节庆的气息，"
            "也记得阿妈们在月光下挑花、打籽、辫绣的样子。那些被绣进衣裙的太阳、鸟纹、蝴蝶和龙纹，"
            "对她来说不是图案，而是侗族人对自然、生活与美好愿望的表达。"
        )
        st.write(
            "因此，当她出现在虚拟博物馆或数字导览里，用户感受到的就不只是知识说明，"
            "而是一种有人带领、有人讲述、有人陪伴的进入方式。"
        )

    st.divider()
    meaning_left, meaning_right = st.columns([1, 1], gap="large")
    with meaning_left:
        render_section_heading("纹样不只是图案，也是一种生活语言", "每一种纹样，都能成为一段更容易被记住的故事")
        for name, meaning in PATTERN_MEANINGS:
            st.markdown(f"- **{name}**：{meaning}")
        st.write(
            "这些图案之所以动人，不在于形式本身，而在于它们与侗族人的服饰、节庆、祝愿和日常记忆始终连在一起。"
        )
    with meaning_right:
        render_section_heading("锦小绣可以怎么讲这些内容", "从纹样出发，再回到人、生活与情感")
        st.write(
            "她可以从一枚太阳花纹讲到光明与祝福，从对鸟纹讲到和合与陪伴，从蝴蝶纹讲到自由与灵动，"
            "再把这些寓意自然带回到侗族人的服饰场景、生活经验与文化情感中。"
        )
        st.write(
            "这样，用户记住的不只是纹样名称，而是‘为什么会这样绣、为什么值得被继续看见’。"
        )

    st.divider()
    render_section_heading("视觉资源与场景表达", "从原始纹样到文创转化，形成更完整的展示路径")
    image_cols = st.columns(3, gap="large")
    with image_cols[0]:
        st.image(_asset(PATTERN_DIR / "duiniaowen.png"), caption="原始纹样：对鸟纹", use_container_width=True)
    with image_cols[1]:
        st.image(_asset(PATTERN_DIR / "taiyanghuawen.png"), caption="主题纹样：太阳花纹", use_container_width=True)
    with image_cols[2]:
        st.image(
            _asset(SHOWCASE_DIR / "mockups" / "phonecase_longwen.png"),
            caption="转化示意：纹样文创应用",
            use_container_width=True,
        )

    st.markdown("#### 文创视觉延展")
    st.write(
        "结合你现有的角色方向和文创表达，这些视觉可以继续被整理成虚拟博物馆导览页、文创提案页和角色传播页，"
        "让用户看到侗绣如何从原始纹样自然过渡到更年轻化的当代应用。"
    )
    showcase_row_1 = st.columns(3, gap="large")
    for col, (img_path, caption) in zip(showcase_row_1, SHOWCASE_IMAGES[:3]):
        with col:
            st.image(_asset(img_path), caption=caption, use_container_width=True)

    showcase_row_2 = st.columns(3, gap="large")
    for col, (img_path, caption) in zip(showcase_row_2, SHOWCASE_IMAGES[3:]):
        with col:
            st.image(_asset(img_path), caption=caption, use_container_width=True)

    roadmap_left, roadmap_right = st.columns(2, gap="large")
    with roadmap_left:
        render_section_heading("一条自然的落地路径", "从进入场景到形成记忆点")
        for idx, item in enumerate(LANDING_PATH, start=1):
            st.markdown(f"{idx}. {item}")
    with roadmap_right:
        render_section_heading("适合继续延展的文创方向", "让角色、纹样和场景形成统一识别")
        for item in PRODUCT_IDEAS:
            st.markdown(f"- {item}")
        st.write(
            "当角色形象、纹样语言与场景叙事统一之后，这一页就不只是在讲功能，也能自然承接文创展示与品牌传播。"
        )

    st.divider()
    persona_left, persona_right = st.columns([0.95, 1.05], gap="large")
    with persona_left:
        render_section_heading("角色气质", "让非遗传播不再显得遥远")
        for item in IP_PERSONA:
            st.markdown(f"- {item}")
    with persona_right:
        render_section_heading("为什么这一页值得继续加强", "它最适合承接项目展示、答辩表达与落地说明")
        st.markdown("- 它能把“技术功能”翻译成“真实使用场景”。")
        st.markdown("- 它能把“纹样资料”转成“有人讲述的文化内容”。")
        st.markdown("- 它能把“虚拟博物馆”与“IP 导览”连接成更完整的体验路线。")
        st.markdown("- 它能帮助老师、评审或合作方更快理解项目的落地价值。")

    st.divider()
    user_cols = st.columns(3, gap="large")
    with user_cols[0]:
        render_section_heading("适合的合作对象", "更偏展陈、文旅、教育与数字内容项目")
        for item in B_SIDE_USERS:
            st.markdown(f"- {item}")
    with user_cols[1]:
        render_section_heading("适合的观看者", "更偏普通观众、学生与年轻文化用户")
        for item in C_SIDE_USERS:
            st.markdown(f"- {item}")
    with user_cols[2]:
        render_section_heading("可延展的合作方式", "既能做展示，也能做长期传播与授权")
        for item in BUSINESS_MODELS:
            st.markdown(f"- {item}")
