import json
import re
import sys
from json import JSONDecoder
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PAGES_DIR = PROJECT_ROOT / "pages"
for path in (PROJECT_ROOT, PAGES_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

import streamlit as st

from agent.react_agent import ReactAgent
from ai_workflow_page import render_ai_workflow_page
from cocreate_page import render_cocreate_page
from cultural_page import render_cultural_page
from guide_page import render_guide_page, render_guide_sidebar
from pattern_page import render_pattern_page
from scenario_page import render_scenario_page
from rag.rag_service import RagSummarizeService


HOME_PAGE = "首页"
GUIDE_PAGE = "文化导览"
PATTERN_PAGE = "纹样图谱"
CULTURAL_PAGE = "文创展陈"
COCREATE_PAGE = "设计工作台"
AI_WORKFLOW_PAGE = "幕后方法"
SCENARIO_PAGE = "场景落地"

NAV_PAGES = [
    HOME_PAGE,
    GUIDE_PAGE,
    PATTERN_PAGE,
    CULTURAL_PAGE,
    COCREATE_PAGE,
    AI_WORKFLOW_PAGE,
    SCENARIO_PAGE,
]

PROJECT_ROOT = Path(__file__).resolve().parent


HERO_IMAGE = "assets/workflow/boards/board_1.png"
HOME_HIGHLIGHTS = [
    ("路径一", "看纹样", "先从典型图样、关键词和扫图观察中建立第一印象。"),
    ("路径二", "听讲解", "通过文化导览理解图样背后的构成特点、寓意和使用场景。"),
    ("路径三", "做转化", "进入设计工作台和文创展陈，继续完成设计延展与展示表达。"),
]
HOME_SCENARIOS = [
    ("展馆导览", "适合展览讲解、展签说明和观众互动问答。"),
    ("文创设计", "适合浏览纹样如何被转化为明信片、包装与周边。"),
    ("课程体验", "适合课堂展示、研学活动和创意工作坊使用。"),
]
HOME_BUSINESS_CHAIN = ["纹样整理", "导览理解", "创意生成", "设计转化", "场景应用"]


def _load_json(relative_path: str):
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


def _asset_path(relative_path: str) -> str:
    return str(PROJECT_ROOT / relative_path)


def _inject_global_styles():
    st.markdown(
        """
        <style>
        :root {
            --xiu-ink: #1f2a30;
            --xiu-muted: #61717a;
            --xiu-accent: #2e5b66;
            --xiu-accent-soft: #dbe9ea;
            --xiu-line: rgba(46, 91, 102, 0.12);
            --xiu-shadow: 0 14px 32px rgba(35, 56, 64, 0.05);
            --xiu-panel: rgba(253, 253, 250, 0.78);
            --xiu-panel-strong: rgba(255, 255, 253, 0.96);
        }
        .stApp {
            background:
                radial-gradient(circle at 0% 0%, rgba(180, 214, 218, 0.28), transparent 24%),
                radial-gradient(circle at 100% 10%, rgba(232, 220, 195, 0.22), transparent 24%),
                linear-gradient(180deg, #f6f7f4 0%, #f2f4ef 100%);
            color: var(--xiu-ink);
        }
        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 3.4rem;
            max-width: 1180px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #eef3f1 0%, #e8eeeb 100%);
            border-right: 1px solid rgba(46, 91, 102, 0.08);
        }
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavSeparator"] {
            display: none;
        }
        div[data-testid="stMetric"] {
            background: transparent;
            border: 1px solid var(--xiu-line);
            border-radius: 14px;
            padding: 0.95rem 1rem;
            box-shadow: none;
        }
        .xiu-hero {
            padding: 0.2rem 0 0.4rem;
        }
        .xiu-card, .xiu-strip, .xiu-gallery, .xiu-module-row {
            background: var(--xiu-panel);
            border: 1px solid var(--xiu-line);
            border-radius: 18px;
            box-shadow: var(--xiu-shadow);
            backdrop-filter: blur(8px);
        }
        .xiu-card {
            padding: 1rem 1.05rem 0.95rem;
            height: 100%;
        }
        .xiu-strip {
            padding: 1rem 1.05rem;
        }
        .xiu-gallery {
            padding: 1rem;
        }
        .xiu-module-row {
            padding: 1rem 1.1rem;
            margin-bottom: 0.85rem;
        }
        .xiu-eyebrow {
            color: var(--xiu-accent);
            font-size: 0.79rem;
            letter-spacing: 0.05em;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .xiu-title {
            font-size: 2.45rem;
            line-height: 1.18;
            font-weight: 800;
            color: var(--xiu-ink);
            margin-bottom: 0.9rem;
            max-width: 11ch;
        }
        .xiu-desc {
            font-size: 0.98rem;
            line-height: 1.82;
            color: var(--xiu-muted);
        }
        .xiu-card h4, .xiu-strip h4, .xiu-module-row h4 {
            color: var(--xiu-ink);
            margin-bottom: 0.34rem;
            font-size: 1.03rem;
        }
        .xiu-chip {
            display: inline-block;
            padding: 0.28rem 0.78rem;
            margin: 0.2rem 0.34rem 0 0;
            border-radius: 999px;
            background: var(--xiu-accent-soft);
            color: var(--xiu-accent);
            font-size: 0.84rem;
            font-weight: 600;
        }
        .xiu-chain {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.8rem;
        }
        .xiu-chain-item {
            background: transparent;
            border: 1px dashed var(--xiu-line);
            border-radius: 15px;
            padding: 0.92rem 0.75rem;
            text-align: center;
            font-weight: 700;
            color: #4a5d66;
        }
        .xiu-section-intro {
            max-width: 760px;
            color: var(--xiu-muted);
            line-height: 1.85;
            margin-bottom: 0.9rem;
        }
        .xiu-feature-list {
            display: grid;
            gap: 0.75rem;
            margin-top: 0.4rem;
        }
        .xiu-feature-item {
            padding: 0.85rem 0;
            border-bottom: 1px solid var(--xiu-line);
        }
        .xiu-feature-item:last-child {
            border-bottom: none;
        }
        .xiu-feature-item strong {
            color: var(--xiu-ink);
            display: block;
            margin-bottom: 0.2rem;
        }
        @media (max-width: 900px) {
            .xiu-chain { grid-template-columns: 1fr; }
            .xiu-title { font-size: 1.78rem; max-width: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


HOME_MODULES = [
    {
        "title": PATTERN_PAGE,
        "tag": "纹样内容",
        "desc": "查看典型侗绣纹样的分类、图像特征与少量关键词。",
        "highlight": "先看图，再决定要不要展开细节。",
    },
    {
        "title": GUIDE_PAGE,
        "tag": "文化理解",
        "desc": "通过预设问题、导览结果和展签式内容理解纹样背景。",
        "highlight": "更像导览机和展签助手，而不是聊天工具。",
    },
    {
        "title": COCREATE_PAGE,
        "tag": "设计转化",
        "desc": "选择纹样、方向和风格，快速生成更适合方案讨论的设计提案。",
        "highlight": "低输入、高选择，减少提示词表单感。",
    },
    {
        "title": CULTURAL_PAGE,
        "tag": "文创展陈",
        "desc": "按平面、产品和生成延展分组浏览作品，强化展陈感与作品感。",
        "highlight": "更像作品浏览页，而不是模块说明页。",
    },
    {
        "title": SCENARIO_PAGE,
        "tag": "应用展示",
        "desc": "展示平台如何进入展馆、课堂、品牌和传播等真实场景。",
        "highlight": "强调落地方式，不强调功能罗列。",
    },
    {
        "title": AI_WORKFLOW_PAGE,
        "tag": "方法说明",
        "desc": "解释为什么做、如何整理、AI 做了什么，以及最终输出了什么。",
        "highlight": "服务于答辩表达与项目讲述。",
    },
]

PATTERN_ATLAS_ITEMS = _load_json("data/platform/pattern_atlas.json")
PATTERN_SCAN_ITEMS = _load_json("data/platform/pattern_scans.json")
CULTURAL_SHOWCASE = _load_json("data/platform/cultural_showcase.json")
AI_WORKFLOW_CONTENT = _load_json("data/platform/ai_workflow.json")


def _go_to(page: str):
    st.session_state.current_page = page


if "current_page" not in st.session_state:
    st.session_state.current_page = HOME_PAGE


st.set_page_config(page_title="侗族织绣纹样平台", page_icon="🧵", layout="wide")
_inject_global_styles()


def _extract_citations(text: str):
    """
    从模型输出中抽取引用区块：
    [[CITATIONS]]
    {...json...}
    [[/CITATIONS]]
    """
    if not text:
        return text, None

    start_tag = "[[CITATIONS]]"
    end_tag = "[[/CITATIONS]]"
    start = text.rfind(start_tag)
    end = text.rfind(end_tag)
    if start != -1 and end != -1 and end > start:
        json_part = text[start + len(start_tag) : end].strip()
        answer = (text[:start] + text[end + len(end_tag) :]).strip()
        try:
            data = json.loads(json_part)
            if isinstance(data, dict) and not answer:
                answer = str(data.get("answer", "")).strip()
            return answer, data
        except Exception:
            pass

    decoder = JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, end = decoder.raw_decode(text[i:])
            if isinstance(obj, dict) and "answer" in obj and "citations" in obj:
                prefix = text[:i].strip()
                answer = prefix if prefix else str(obj.get("answer", "")).strip()
                return answer, obj
        except Exception:
            continue

    try:
        return text, None
    except Exception:
        return text, None


def _clean_answer_text(answer: str) -> str:
    """
    清洗模型正文中的工具回显噪音（例如 web_search 的 {"query":...,"results":[...]}）。
    """
    if not answer:
        return answer

    cleaned = answer

    # 去掉残留的引用区块与异常标签，避免直接显示在页面正文中
    cleaned = re.sub(r"\[\[?/?CITATIONS\]?\]", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\{\s*\"answer\"\s*:\s*.*?\"citations\"\s*:\s*\[.*?\]\s*\}", " ", cleaned, flags=re.S)

    cleaned = re.sub(
        r'\s*\{"query"\s*:\s*".*?"\s*,\s*"results"\s*:\s*\[.*?\]\}\s*',
        " ",
        cleaned,
        flags=re.S,
    )

    cleaned = re.sub(r"(?m)^\s*#{1,6}\s*网络补充来源\s*$", "网络补充来源", cleaned)
    cleaned = cleaned.replace("###### 网络补充来源", "网络补充来源")
    cleaned = cleaned.replace("### 网络补充来源", "网络补充来源")
    cleaned = cleaned.replace("## 网络补充来源", "网络补充来源")

    cleaned = re.sub(r"（?注：此为示意链接，实际搜索未返回具体结果）?", "", cleaned)

    lines = [line.rstrip() for line in cleaned.splitlines()]
    normalized_lines = []
    last_meaningful = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            normalized_lines.append("")
            continue

        if stripped == last_meaningful:
            continue

        if stripped.endswith("？") and last_meaningful == "":
            continue

        normalized_lines.append(stripped)
        last_meaningful = stripped

    cleaned = "\n".join(normalized_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _render_metric(label: str, value: str, help_text: str):
    st.metric(label, value, help=help_text)


def _render_section_heading(title: str, subtitle: str):
    st.markdown(f"### {title}")
    st.caption(subtitle)


def _get_pattern_names() -> list[str]:
    return [item["name"] for item in PATTERN_ATLAS_ITEMS]


def _get_pattern_item(name: str) -> dict | None:
    for item in PATTERN_ATLAS_ITEMS:
        if item["name"] == name:
            return item
    return None


def _get_related_scan_items(pattern_name: str) -> list[dict]:
    return [item for item in PATTERN_SCAN_ITEMS if item.get("related_pattern") == pattern_name]


def _apply_cocreate_preset(pattern_name: str, theme: str, target: str, tone: str, extra: str):
    st.session_state["pending_cocreate_preset"] = {
        "pattern": pattern_name,
        "theme": theme,
        "target": target,
        "tone": tone,
        "extra": extra,
    }


def _render_homepage():
    st.title("绣见侗韵")
    st.caption("侗绣文化体验与设计转化平台")
    st.divider()

    st.markdown(
        """
        <div class="xiu-hero">
            <div class="xiu-eyebrow">侗绣文化体验与设计转化平台</div>
            <div class="xiu-title">看见纹样，听懂文化，再走向设计转化</div>
            <div class="xiu-desc">
                这里不是功能堆叠式工具页，而是一个以侗绣纹样为线索展开的文化体验入口。
                你可以先看纹样、再听讲解，也可以继续进入设计工作台和文创展陈，理解传统图样如何被转化为今天可展示、可传播的内容。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        if st.button("进入纹样图谱", key="hero-pattern", width="stretch"):
            _go_to(PATTERN_PAGE)
            st.rerun()
    with action_col2:
        if st.button("进入文化导览", key="hero-guide", width="stretch"):
            _go_to(GUIDE_PAGE)
            st.rerun()
    with action_col3:
        if st.button("进入设计工作台", key="hero-studio", width="stretch"):
            _go_to(COCREATE_PAGE)
            st.rerun()

    st.divider()
    _render_section_heading("体验路径", "")
    path_cols = st.columns(3, gap="large")
    for col, item in zip(path_cols, HOME_HIGHLIGHTS):
        title, label, desc = item
        with col:
            st.markdown(
                f"""
                <div class="xiu-strip">
                    <div class="xiu-eyebrow">{title}</div>
                    <h4>{label}</h4>
                    <div class="xiu-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    _render_section_heading("平台价值", "")
    value_cols = st.columns(3, gap="large")
    value_items = [
        ("整理纹样内容", "把典型纹样、扫图观察和图像特征组织成更容易浏览的内容结构。"),
        ("帮助观众理解", "用导览、问答和展签式表达降低理解门槛，让观众先看懂再深入。"),
        ("支持设计转化", "把纹样进一步带到设计工作台、文创展陈和真实应用场景中。"),
    ]
    for col, item in zip(value_cols, value_items):
        title, desc = item
        with col:
            st.markdown(
                f"""
                <div class="xiu-strip">
                    <h4>{title}</h4>
                    <div class="xiu-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    _render_section_heading("页面入口", "")
    for module in HOME_MODULES:
        left, right = st.columns([0.78, 0.22], gap="large")
        with left:
            st.markdown(
                f"""
                <div class="xiu-module-row">
                    <div class="xiu-eyebrow">{module['tag']}</div>
                    <h4>{module['title']}</h4>
                    <div class="xiu-desc">{module['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with right:
            if st.button("进入", key=f"home-{module['title']}", width="stretch"):
                _go_to(module["title"])
                st.rerun()



def _run_agent_request(prompt: str, context: dict):
    response_message = []
    response_stream = st.session_state.agent.execute_stream(prompt, context=context)

    for chunk in response_stream:
        response_message.append(chunk)

    full_text = "".join(response_message).strip()
    answer, citations = _extract_citations(full_text)
    answer = _clean_answer_text(answer.strip())
    if not answer:
        answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
    if not context.get("citations_enabled", True):
        citations = None
    return answer, citations


def _run_agent_request_streaming(prompt: str, context: dict, placeholder):
    response_message = []
    response_stream = st.session_state.agent.execute_stream(prompt, context=context)

    for chunk in response_stream:
        response_message.append(chunk)
        partial_text = _clean_answer_text("".join(response_message).strip())
        if partial_text:
            placeholder.markdown(partial_text)

    full_text = "".join(response_message).strip()
    answer, citations = _extract_citations(full_text)
    answer = _clean_answer_text(answer.strip())
    if not answer:
        answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
    if not context.get("citations_enabled", True):
        citations = None
    return answer, citations


def _run_direct_rag_request(prompt: str):
    raw_result = st.session_state.rag_service.rag_summarize_with_citations(prompt)
    try:
        payload = json.loads(raw_result)
    except Exception:
        cleaned = _clean_answer_text(str(raw_result).strip())
        return cleaned or "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。", None

    answer = _clean_answer_text(str(payload.get("answer", "")).strip())
    citations = payload.get("citations", [])
    if not answer:
        answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
    return answer, citations


if "rag_service" not in st.session_state:
    st.session_state.rag_service = RagSummarizeService()

if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.subheader("平台导航")
    selected_page = st.radio(
        "页面",
        options=NAV_PAGES,
        index=NAV_PAGES.index(st.session_state.current_page),
        key="nav_page_selector",
    )
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

    st.divider()
    render_guide_sidebar(current_page=st.session_state.current_page, guide_page=GUIDE_PAGE)


if st.session_state.current_page == HOME_PAGE:
    _render_homepage()
elif st.session_state.current_page == GUIDE_PAGE:
    render_guide_page(
        run_agent_request=_run_agent_request,
        run_direct_rag_request=_run_direct_rag_request,
    )

elif st.session_state.current_page == PATTERN_PAGE:
    render_pattern_page(
        guide_page=GUIDE_PAGE,
        cocreate_page=COCREATE_PAGE,
        pattern_items=PATTERN_ATLAS_ITEMS,
        pattern_scan_items=PATTERN_SCAN_ITEMS,
        apply_cocreate_preset=_apply_cocreate_preset,
        render_section_heading=_render_section_heading,
    )

elif st.session_state.current_page == CULTURAL_PAGE:
    render_cultural_page(cultural_showcase=CULTURAL_SHOWCASE, asset_path=_asset_path)

elif st.session_state.current_page == COCREATE_PAGE:
    render_cocreate_page(
        cocreate_page=COCREATE_PAGE,
        pattern_page=PATTERN_PAGE,
        apply_cocreate_preset=_apply_cocreate_preset,
        render_section_heading=_render_section_heading,
        get_pattern_names=_get_pattern_names,
        get_pattern_item=_get_pattern_item,
        get_related_scan_items=_get_related_scan_items,
        run_direct_rag_request=_run_direct_rag_request,
        run_agent_request_streaming=_run_agent_request_streaming,
    )

elif st.session_state.current_page == AI_WORKFLOW_PAGE:
    render_ai_workflow_page(ai_workflow_content=AI_WORKFLOW_CONTENT, asset_path=_asset_path)

elif st.session_state.current_page == SCENARIO_PAGE:
    render_scenario_page(render_section_heading=_render_section_heading)
