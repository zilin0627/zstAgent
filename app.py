import json
import re
import sys
import pandas as pd
import requests
from collections import Counter
from json import JSONDecoder
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from agent.react_agent import ReactAgent
from pages.ai_workflow_page import render_ai_workflow_page
from pages.cocreate_page import render_cocreate_page
from pages.cultural_page import render_cultural_page
from pages.guide_page import render_guide_page, render_guide_sidebar
from pages.pattern_page import render_pattern_page
from pages.scenario_page import render_scenario_page
from rag.rag_service import RagSummarizeService
from utils.logger_handler import logger


HOME_PAGE = "首页"
GUIDE_PAGE = "文化导览"
PATTERN_PAGE = "纹样图谱"
CULTURAL_PAGE = "文创展陈"
COCREATE_PAGE = "设计工作台"
AI_WORKFLOW_PAGE = "AI 工作流"
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

HOME_HIGHLIGHTS = [
    ("路径一", "看纹样", "先从典型图样、关键词和扫图观察中建立第一印象。"),
    ("路径二", "听讲解", "通过文化导览理解图样背后的构成特点、寓意和使用场景。"),
    ("路径三", "做转化", "进入设计工作台和文创展陈，继续完成设计延展与展示表达。"),
]

def _load_json(relative_path: str):
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


def _asset_path(relative_path: str) -> str:
    return str(PROJECT_ROOT / relative_path)


def _inject_global_styles():
    st.markdown(
        """
        <style>
        /* ========== 全局基础 ========== */
        :root {
            --xiu-ink: #202124;
            --xiu-muted: #4b5563;
            --xiu-accent: #d84c4c;
            --xiu-accent-soft: #fbe4e4;
            --xiu-line: rgba(32, 33, 36, 0.10);
            --xiu-shadow: 0 6px 16px rgba(17, 24, 39, 0.03);
            --xiu-panel: rgba(255, 255, 255, 0.92);
            --xiu-panel-strong: rgba(255, 255, 255, 0.98);
        }

        /* 整体背景 */
        .stApp {
            background:
                linear-gradient(180deg, #f8f8f4 0%, #f6f6f1 100%);
            color: var(--xiu-ink);
        }

        /* 主要内容区宽度与间距 */
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        /* ========== 保留侧边栏开关，只弱化顶部条 ========== */
        header[data-testid="stHeader"] {
            background: transparent !important;
            border-bottom: none !important;
            height: auto !important;
        }
        .main .block-container {
            padding-top: 0.6rem !important;
        }
        /* =================================== */
        

        /* ========== 侧边栏紧凑化 ========== */
        [data-testid="stSidebar"] {
            background: #f3f5f4;
            border-right: 1px solid rgba(32, 33, 36, 0.08);
            min-width: 240px !important;
            max-width: 260px !important;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] [data-baseweb="radio"] *,
        [data-testid="stSidebar"] [role="radiogroup"] * {
            color: var(--xiu-ink) !important;
            font-size: 0.85rem !important;
        }
        /* 单选项做成可见的选中态，避免看不出点的是哪个 */
        [data-testid="stSidebar"] [data-baseweb="radio"] label,
        [data-testid="stSidebar"] [role="radiogroup"] label,
        [data-baseweb="radio"] label,
        [role="radiogroup"] label {
            border: 1px solid transparent !important;
            border-radius: 12px !important;
            padding: 0.35rem 0.55rem !important;
            transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] label:hover,
        [data-testid="stSidebar"] [role="radiogroup"] label:hover,
        [data-baseweb="radio"] label:hover,
        [role="radiogroup"] label:hover {
            background: #f5f5f3 !important;
            border-color: #e5e7eb !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] label:has(input:checked),
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked),
        [data-baseweb="radio"] label:has(input:checked),
        [role="radiogroup"] label:has(input:checked) {
            background: #fbe4e4 !important;
            border-color: #efb3b3 !important;
            color: #b93838 !important;
            font-weight: 700 !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] label:has(input:checked) *,
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *,
        [data-baseweb="radio"] label:has(input:checked) *,
        [role="radiogroup"] label:has(input:checked) * {
            color: #b93838 !important;
        }
        /* 去掉侧边栏单选前面的黑圆点 */
        [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child,
        [data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child,
        [data-testid="stSidebar"] input[type="radio"] {
            display: none !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] label {
            padding-left: 0 !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] label > div {
            gap: 0.25rem !important;
        }
        [data-testid="stSidebar"] .stCaption {
            color: var(--xiu-muted) !important;
            font-size: 0.75rem !important;
        }
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            font-size: 1.1rem !important;
        }
        /* 隐藏原生导航 */
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavSeparator"] {
            display: none;
        }

        /* ========== 标题字号整体缩小 ========== */
        h1 {
            font-size: 1.8rem !important;
            margin-bottom: 0.4rem !important;
        }
        h2 {
            font-size: 1.4rem !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.3rem !important;
        }
        h3 {
            font-size: 1.15rem !important;
            margin-top: 0.6rem !important;
            margin-bottom: 0.2rem !important;
        }
        h4 {
            font-size: 1rem !important;
            margin-bottom: 0.2rem !important;
        }

        /* ========== 正文与辅助文字 ========== */
        h1, h2, h3, h4, h5, h6,
        p, li, label, span, div,
        .stMarkdown, .stText {
            color: var(--xiu-ink);
        }
        p, li, .stMarkdown, .stText {
            font-size: 0.88rem !important;
            line-height: 1.5 !important;
        }
        .stCaption {
            font-size: 0.78rem !important;
            color: var(--xiu-muted) !important;
        }

        /* 去掉全站默认列表黑圆点，保留自定义内容展示 */
        ul, ol {
            list-style: none !important;
            padding-left: 0 !important;
            margin-left: 0 !important;
        }
        li::marker {
            content: "" !important;
        }

        /* ========== 卡片与面板（紧凑内边距） ========== */
        div[data-testid="stMetric"] {
            background: transparent;
            border: 1px solid var(--xiu-line);
            border-radius: 12px;
            padding: 0.5rem 0.8rem;
            box-shadow: none;
        }
        div[data-testid="stMetric"] label {
            font-size: 0.75rem !important;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }

        .xiu-hero {
            padding: 0.1rem 0 0.2rem;
        }
        .xiu-card, .xiu-strip, .xiu-gallery, .xiu-module-row {
            background: var(--xiu-panel);
            border: 1px solid rgba(32, 33, 36, 0.06);
            border-radius: 14px;
            box-shadow: var(--xiu-shadow);
            backdrop-filter: blur(8px);
        }
        .xiu-card {
            padding: 0.7rem 0.9rem;
            height: 100%;
        }
        .xiu-strip {
            padding: 0.7rem 0.9rem;
        }
        .xiu-gallery {
            padding: 0.8rem;
        }
        .xiu-module-row {
            padding: 0.7rem 0.9rem;
            margin-bottom: 0.6rem;
        }

        .xiu-eyebrow {
            color: var(--xiu-accent);
            font-size: 0.7rem;
            letter-spacing: 0.03em;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .xiu-title {
            font-size: 2rem;
            line-height: 1.2;
            font-weight: 800;
            color: var(--xiu-ink);
            margin-bottom: 0.5rem;
            max-width: 12ch;
        }
        .xiu-desc {
            font-size: 0.85rem;
            line-height: 1.6;
            color: var(--xiu-muted);
        }

        .xiu-card h4, .xiu-strip h4, .xiu-module-row h4 {
            color: var(--xiu-ink);
            margin-bottom: 0.2rem;
            font-size: 0.95rem;
        }

        .xiu-chip {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            margin: 0.15rem 0.3rem 0 0;
            border-radius: 999px;
            background: var(--xiu-accent-soft);
            color: var(--xiu-accent);
            font-size: 0.75rem;
            font-weight: 600;
        }

        .xiu-chain {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.6rem;
        }
        .xiu-chain-item {
            background: transparent;
            border: 1px dashed var(--xiu-line);
            border-radius: 12px;
            padding: 0.6rem 0.5rem;
            text-align: center;
            font-weight: 700;
            font-size: 0.8rem;
            color: #4a5d66;
        }

        .xiu-section-intro {
            max-width: 760px;
            color: var(--xiu-muted);
            line-height: 1.6;
            margin-bottom: 0.6rem;
            font-size: 0.85rem;
        }

        .xiu-feature-list {
            display: grid;
            gap: 0.5rem;
            margin-top: 0.2rem;
        }
        .xiu-feature-item {
            padding: 0.6rem 0;
            border-bottom: 1px solid var(--xiu-line);
        }
        .xiu-feature-item strong {
            color: var(--xiu-ink);
            display: block;
            margin-bottom: 0.1rem;
            font-size: 0.9rem;
        }

        /* ========== 对话气泡（紧凑版） ========== */
        .user-bubble {
            background: #eef6fb;
            color: #202124;
            padding: 0.6rem 0.9rem;
            border-radius: 16px 16px 4px 16px;
            margin: 0.4rem 0;
            max-width: 85%;
            margin-left: auto;
            border: 1px solid #d7e6f1;
            font-size: 0.88rem;
            line-height: 1.5;
        }
        .assistant-bubble {
            background: #ffffff;
            color: #202124;
            padding: 0.6rem 0.9rem;
            border-radius: 16px 16px 16px 4px;
            margin: 0.4rem 0;
            max-width: 85%;
            border: 1px solid #e5e7eb;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            font-size: 0.88rem;
            line-height: 1.5;
        }
        .thought-box {
            background: #faf6ee;
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            border-left: 3px solid #c9ab7a;
            margin: 0.3rem 0;
            font-size: 0.8rem;
            color: #5b4630;
        }

        details {
            background: #fbfbf8;
            border: 1px solid #ece7dd;
            border-radius: 10px;
            padding: 0.4rem 0.8rem;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #202124;
        }

        /* ========== 按钮紧凑化 + 明确前景色，避免深浅主题串色 ========== */
        .stButton button, .stFormSubmitButton button {
            font-size: 0.85rem !important;
            padding: 0.3rem 0.9rem !important;
            border-radius: 999px !important;
            background: #ffffff !important;
            color: #202124 !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: none !important;
        }
        .stButton button *, .stFormSubmitButton button * {
            color: #202124 !important;
        }
        .stButton button:hover, .stFormSubmitButton button:hover {
            background: #f5f5f3 !important;
            border-color: #d7dce2 !important;
            color: #202124 !important;
        }

        /* ========== 输入框、选择框等：强制浅底深字 ========== */
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] input {
            font-size: 0.85rem !important;
            background: #f8f9fb !important;
            color: #202124 !important;
            border: 1px solid #e3e7ed !important;
            border-radius: 12px !important;
        }
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        [data-testid="stChatInput"] textarea::placeholder,
        [data-testid="stChatInput"] input::placeholder {
            color: #9aa3af !important;
            opacity: 1 !important;
        }

        /* ========== 下拉框弹层：覆盖 BaseWeb 默认深色菜单 ========== */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] * {
            color: #202124 !important;
        }
        div[data-baseweb="popover"] > div,
        div[data-baseweb="select"] ul,
        div[data-baseweb="select"] li,
        div[role="listbox"],
        div[role="option"] {
            background: #ffffff !important;
            color: #202124 !important;
            border-color: #e3e7ed !important;
        }
        div[role="listbox"] {
            border: 1px solid #e3e7ed !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 28px rgba(17, 24, 39, 0.08) !important;
        }
        div[role="option"]:hover,
        div[role="option"][aria-selected="true"] {
            background: #f3f6fa !important;
            color: #202124 !important;
        }

        /* ========== 桌面端底部聊天区：覆盖 Streamlit 默认深色容器 ========== */
        [data-testid="stChatInput"] {
            background: #f6f6f1 !important;
            border-top: 1px solid rgba(32, 33, 36, 0.08) !important;
        }
        [data-testid="stChatInput"] > div {
            background: transparent !important;
        }
        [data-testid="stBottomBlockContainer"],
        [data-testid="stBottom"] {
            background: #f6f6f1 !important;
        }
        [data-testid="stChatInput"] button {
            background: #ffffff !important;
            color: #202124 !important;
            border: 1px solid #e3e7ed !important;
        }
        [data-testid="stChatInput"] button svg {
            fill: #202124 !important;
        }
        /* 图片自适应：限制最大高度，避免撑爆卡片 */
    img {
        max-height: 240px;
        width: auto;
        object-fit: contain;
    }

    /* 在小屏幕上进一步缩小图片 */
    @media (max-width: 768px) {
        img {
            max-height: 180px;
        }
    }
        /* ========== 移动端适配 ========== */
        @media (max-width: 900px) {
            .xiu-chain { grid-template-columns: 1fr; }
            .xiu-title { font-size: 1.5rem; max-width: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


PATTERN_ATLAS_ITEMS = _load_json("data/platform/pattern_atlas.json")
PATTERN_SCAN_ITEMS = _load_json("data/platform/pattern_scans.json")
CULTURAL_SHOWCASE = _load_json("data/platform/cultural_showcase.json")
AI_WORKFLOW_CONTENT = _load_json("data/platform/ai_workflow.json")


if "current_page" not in st.session_state:
    st.session_state.current_page = HOME_PAGE


st.set_page_config(page_title="侗绣 AI 辅助设计平台", page_icon="🧵", layout="wide")
_inject_global_styles()


def _extract_citations(text: str):
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
    if not answer:
        return answer

    cleaned = answer
    cleaned = re.sub(r"\[\[THOUGHT\]\].*", " ", cleaned)
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

    filtered_lines = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if re.search(r"https?://|www\.", stripped, flags=re.I):
            continue
        filtered_lines.append(line)
    cleaned = "\n".join(filtered_lines)
    cleaned = re.sub(r"(?m)^\s*[\-•]\s*$", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*网络补充来源\s*$\n?", "", cleaned)

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


def _extract_web_results_from_tool_text(tool_text: str) -> list[dict]:
    if not tool_text:
        return []
    try:
        payload = json.loads(tool_text)
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    results = payload.get("results", []) or []
    web_citations = []
    seen_urls = set()
    for item in results:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip() or "网页结果"
        snippet = str(item.get("snippet", "")).strip()
        if not url or url in seen_urls:
            continue
        if not re.match(r"^https?://", url, flags=re.I):
            continue
        if re.search(r"(^|://)(www\.)?gzsich\.gov\.cn/?$", url, flags=re.I):
            continue
        seen_urls.add(url)
        web_citations.append(
            {
                "index": len(web_citations) + 1,
                "source": title,
                "page": None,
                "snippet": snippet[:220],
                "url": url,
                "metadata": {"source_type": "web"},
            }
        )
    return web_citations


def _merge_citations(base_citations, web_citations: list[dict]):
    if not web_citations:
        return base_citations
    if isinstance(base_citations, dict):
        payload = dict(base_citations)
        existing = payload.get("citations", []) or []
        payload["citations"] = existing + web_citations
        return payload
    if isinstance(base_citations, list):
        return base_citations + web_citations
    return {"citations": web_citations}


def _normalize_thought_label(tool_name: str, tool_text: str) -> str:
    if tool_name == "classify_intent":
        return "正在判断问题类型与回答路径…"
    if tool_name == "rag_summarize":
        return "正在检索本地知识库并提取相关资料…"
    if tool_name == "fetch_exhibit":
        return "正在匹配相关展品或纹样条目…"
    if tool_name == "web_search":
        results = _extract_web_results_from_tool_text(tool_text)
        if results:
            return f"正在补充联网资料，已找到 {len(results)} 条网页线索…"
        return "正在补充联网资料并整理网页来源…"
    if tool_name == "handoff_to_human":
        return "当前资料置信度不足，正在给出保守建议…"
    return "正在整理回答思路…"


def _render_thought_trace_html(thought_steps: list[str]) -> str:
    items = []
    for step in thought_steps:
        text = str(step or "").strip()
        if text:
            items.append(f'<div class="thought-box">{text}</div>')
    return "".join(items)


def _build_runtime_status(*, path: str, allow_web: bool, web_search_called: bool, web_result_count: int, used_local_rag: bool, tool_calls: list[str] | None = None, thought_trace: list[str] | None = None, retrieval_count: int | None = None, confidence: str | None = None, error_notice: dict | None = None) -> dict:
    tool_calls = tool_calls or []
    thought_trace = thought_trace or []

    if path == "direct_rag":
        summary = "本轮使用的是直连 RAG，只参考本地知识库，没有经过联网补充。"
    elif web_search_called and web_result_count > 0:
        summary = f"本轮使用的是 Agent 工作流：先查了本地资料，也补充了联网信息，并拿到 {web_result_count} 条可用网页结果。"
    elif web_search_called:
        summary = "本轮使用的是 Agent 工作流，也尝试了联网补充，但网页检索没有返回可用结果；当前回答主要仍基于本地资料。"
    elif allow_web:
        summary = "本轮使用的是 Agent 工作流，虽然允许联网，但这次问题不需要额外网页补充，回答主要基于本地资料。"
    else:
        summary = "本轮使用的是 Agent 工作流，已按设置只使用本地资料，没有进行联网补充。"

    status = {
        "path": path,
        "allow_web": allow_web,
        "web_search_called": web_search_called,
        "web_result_count": web_result_count,
        "used_local_rag": used_local_rag,
        "tool_calls": tool_calls,
        "thought_trace": thought_trace,
        "retrieval_count": retrieval_count,
        "confidence": confidence,
        "summary": summary,
    }
    if error_notice:
        status["error_notice"] = error_notice
    return status


def _set_last_runtime_status(status: dict | None):
    st.session_state["_last_runtime_status"] = status


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


def _get_pattern_category_counts() -> dict[str, int]:
    counter = Counter()
    for item in PATTERN_ATLAS_ITEMS:
        category = item.get("category", "未分类")
        counter[category] += 1
    return dict(counter)


def _get_pattern_carrier_counts() -> dict[str, int]:
    counter = Counter()
    for item in PATTERN_ATLAS_ITEMS:
        carrier_text = item.get("carrier", "")
        for part in carrier_text.split("、"):
            name = part.strip()
            if name:
                counter[name] += 1
    return dict(counter)


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
    st.caption("以侗绣为首个落地场景的 AI 辅助设计平台")
    st.divider()

    st.markdown(
        """
        <div class="xiu-hero">
            <div class="xiu-eyebrow">AI 辅助设计平台</div>
            <div class="xiu-title">看见纹样，听懂文化，再走向设计转化</div>
            <div class="xiu-desc">
                这里是一个以侗绣为首个落地场景的 AI 辅助设计平台。
                平台把纹样整理、文化导览、知识增强、设计提案与场景应用串成一条连续工作流，
                尝试让传统侗绣从“能被看见”进一步走向“能被理解、能被策划、能被继续设计与传播”。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        ("整理纹样内容", "把典型纹样、扫图观察、构图特征和关键词组织成更容易浏览的内容结构。"),
        ("帮助观众理解", "用导览、问答和展签式表达降低理解门槛，让观众先看懂纹样，再理解文化背景。"),
        ("支持设计转化", "把纹样进一步带到设计工作台、文创展陈和真实应用场景中，形成连续展示链路。"),
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
    _render_section_heading("历史、现状与未来", "把侗绣从文化源流、传承处境和数字化转化三个维度串起来")
    insight_cols = st.columns(3, gap="large")
    insight_items = [
        (
            "历史背景",
            "侗绣长期依附于服饰、礼俗和家庭手工传承，不只是装饰图案，也承载身份表达、生活经验与地方审美。"
        ),
        (
            "现实处境",
            "传统技艺面临传承人减少、使用场景收缩与市场表达单一等问题，很多纹样内容仍分散在实物、文献和口述经验中。"
        ),
        (
            "未来方向",
            "数字化整理、纹样图谱、智能导览与设计转化，可以让侗绣从静态资料走向更易理解、可传播、可再设计的文化内容。"
        ),
    ]
    for col, item in zip(insight_cols, insight_items):
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
    _render_section_heading("平台里可以看到什么", "从纹样内容、结构特征到设计延展，形成一条连续的理解路径")
    content_left, content_right = st.columns([1.1, 0.9], gap="large")

    with content_left:
        st.markdown(
            """
            <div class="xiu-strip">
                <h4>看得见的内容</h4>
                <div class="xiu-desc">
                    平台整理了典型纹样分类、真实扫图样本、常见载体、构图特征和视觉关键词，
                    帮助观众先从图像出发建立对侗绣纹样的整体印象。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="xiu-strip" style="margin-top:0.85rem;">
                <h4>看得懂的内容</h4>
                <div class="xiu-desc">
                    通过文化导览、展签式表达和案例转化，平台继续解释纹样背后的寓意、
                    结构规律与适用场景，让理解过程不只停留在“看图识物”。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="xiu-strip" style="margin-top:0.85rem;">
                <h4>可以继续延展的内容</h4>
                <div class="xiu-desc">
                    从纹样图谱进入设计工作台、文创展陈与场景落地，能进一步看到传统图样如何被转化为
                    明信片、包装、样机和传播展示内容。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with content_right:
        st.markdown(
            """
            <div class="xiu-strip">
                <h4>内容概览</h4>
                <div class="xiu-desc">用轻量数据把平台当前已整理的内容范围先展示出来。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_row_1 = st.columns(2, gap="medium")
        with metric_row_1[0]:
            st.metric("纹样卡片", str(len(PATTERN_ATLAS_ITEMS)), help="当前图谱页已整理的典型纹样卡片数量")
        with metric_row_1[1]:
            st.metric("扫图样本", str(len(PATTERN_SCAN_ITEMS)), help="当前平台收录的真实绣片扫描样本数量")

        metric_row_2 = st.columns(2, gap="medium")
        with metric_row_2[0]:
            st.metric(
                "展示作品",
                str(
                    len(CULTURAL_SHOWCASE.get("postcards", []))
                    + len(CULTURAL_SHOWCASE.get("mockups", []))
                    + len(CULTURAL_SHOWCASE.get("generated", []))
                ),
                help="文创展陈页中的明信片、样机与生成延展内容总数",
            )
        with metric_row_2[1]:
            st.metric("纹样类别", "5 类", help="动物、人物、植物/天体、组合、几何/花卉")

        st.markdown(
            """
            <div class="xiu-strip" style="margin-top:0.85rem;">
                <h4>结构关键词</h4>
                <div class="xiu-desc">
                    对称、放射、围合、盘旋、呼应、生长、层级、节奏 —— 这些词帮助把图样观察转成更容易讲述的视觉语言。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
    _render_section_heading("内容概览图表", "把平台里已经整理的纹样类别与常见载体做成更直观的展示")

    category_counts = _get_pattern_category_counts()
    carrier_counts = _get_pattern_carrier_counts()

    category_df = pd.DataFrame(
        {
            "类别": list(category_counts.keys()),
            "数量": list(category_counts.values()),
        }
    ).set_index("类别")

    carrier_df = pd.DataFrame(
        {
            "载体": list(carrier_counts.keys()),
            "数量": list(carrier_counts.values()),
        }
    ).sort_values("数量", ascending=False).set_index("载体")

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        st.markdown(
            """
            <div class="xiu-strip">
                <h4>纹样类别分布</h4>
                <div class="xiu-desc">
                    当前平台已整理的纹样主要覆盖动物纹、人物纹、植物/天体纹、组合纹与几何/花卉纹。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.bar_chart(category_df, height=320)

    with chart_right:
        st.markdown(
            """
            <div class="xiu-strip">
                <h4>常见载体分布</h4>
                <div class="xiu-desc">
                    纹样并不是孤立存在的，它们通常依附在背带盖片、边饰、胸饰、礼仪性服饰等具体载体上。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.bar_chart(carrier_df, height=320)


def _build_network_error_notice(error: Exception) -> dict[str, str]:
    message = str(error).strip()
    lower_message = message.lower()
    error_type = type(error).__name__

    if isinstance(error, requests.exceptions.SSLError) or "ssl" in lower_message:
        user_message = "当前大模型服务的 HTTPS 连接异常，请检查网络、代理或稍后重试。"
    elif isinstance(error, requests.exceptions.Timeout) or "timed out" in lower_message or "timeout" in lower_message:
        user_message = "当前大模型服务响应超时，请稍后重试。"
    elif isinstance(error, requests.exceptions.ConnectionError) or any(keyword in lower_message for keyword in ["connection aborted", "connection reset", "max retries exceeded", "name resolution"]):
        user_message = "当前无法连接到大模型服务，请检查网络连接或稍后重试。"
    else:
        user_message = "当前大模型服务暂时不可用，请稍后重试。"

    debug_detail = f"{error_type}: {message}".strip(": ")[:300]
    return {
        "code": "model_network_error",
        "message": user_message,
        "detail": debug_detail,
    }


# ================== 保持原有直接调用逻辑，不做 API 替换 ==================
def _run_agent_request_streaming(prompt: str, context: dict, placeholder, thought_placeholder=None):
    response_message = []
    web_citations = []
    thought_steps: list[str] = []
    tool_calls: list[str] = []
    web_search_called = False
    used_local_rag = False

    try:
        response_stream = st.session_state.agent.execute_stream(prompt, context=context)
        for chunk in response_stream:
            if chunk.startswith("[[THOUGHT]]"):
                thought_text = chunk[len("[[THOUGHT]]") :].strip()
                if thought_text.startswith("TOOL::"):
                    _, tool_name, tool_text = thought_text.split("::", 2)
                    tool_calls.append(tool_name)
                    normalized_label = _normalize_thought_label(tool_name, tool_text)
                    thought_steps.append(f"⏳ {normalized_label}")
                    if thought_placeholder is not None:
                        thought_placeholder.markdown(_render_thought_trace_html(thought_steps), unsafe_allow_html=True)
                    if tool_name == "web_search":
                        web_search_called = True
                        web_citations = _extract_web_results_from_tool_text(tool_text)
                    if tool_name == "rag_summarize":
                        used_local_rag = True
                else:
                    thought_steps.append(thought_text)
                    if thought_placeholder is not None:
                        thought_placeholder.markdown(_render_thought_trace_html(thought_steps), unsafe_allow_html=True)
                continue

            response_message.append(chunk)
            partial_text = _clean_answer_text("".join(response_message).strip())
            if partial_text:
                placeholder.markdown(partial_text)
    except Exception as error:
        logger.warning("[Agent] 模型调用失败，返回友好提示", exc_info=True)
        notice = _build_network_error_notice(error)
        fallback_answer = notice["message"]
        placeholder.markdown(fallback_answer)
        if thought_placeholder is not None:
            thought_steps.append("⚠️ 本次未能连通模型服务，已返回诊断提示。")
            thought_placeholder.markdown(_render_thought_trace_html(thought_steps), unsafe_allow_html=True)
        runtime_status = _build_runtime_status(
            path="agent",
            allow_web=bool(context.get("allow_web", False)),
            web_search_called=web_search_called,
            web_result_count=len(web_citations),
            used_local_rag=used_local_rag,
            tool_calls=tool_calls,
            thought_trace=thought_steps,
            error_notice=notice,
        )
        _set_last_runtime_status(runtime_status)
        if not context.get("citations_enabled", True):
            return fallback_answer, None, notice
        return fallback_answer, [], notice

    full_text = "".join(response_message).strip()
    citation_payload = _extract_citations(full_text)
    if isinstance(citation_payload, (list, tuple)):
        answer = citation_payload[0] if len(citation_payload) >= 1 else full_text
        citations = citation_payload[1] if len(citation_payload) >= 2 else None
    else:
        answer = full_text
        citations = None
    answer = _clean_answer_text(str(answer or "").strip())
    citations = _merge_citations(citations, web_citations)
    if not answer:
        answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
    if not context.get("citations_enabled", True):
        citations = None

    thought_steps.append("✅ 回答生成完成")
    if thought_placeholder is not None:
        thought_placeholder.markdown(_render_thought_trace_html(thought_steps), unsafe_allow_html=True)

    runtime_status = _build_runtime_status(
        path="agent",
        allow_web=bool(context.get("allow_web", False)),
        web_search_called=web_search_called,
        web_result_count=len(web_citations),
        used_local_rag=used_local_rag,
        tool_calls=tool_calls,
        thought_trace=thought_steps,
    )
    _set_last_runtime_status(runtime_status)
    return answer, citations, None


def _run_direct_rag_request(prompt: str):
    try:
        raw_result = st.session_state.rag_service.rag_summarize_with_citations(prompt)
    except Exception as error:
        logger.warning("[RAG] 模型调用失败，返回友好提示", exc_info=True)
        notice = _build_network_error_notice(error)
        runtime_status = _build_runtime_status(
            path="direct_rag",
            allow_web=False,
            web_search_called=False,
            web_result_count=0,
            used_local_rag=True,
            error_notice=notice,
        )
        _set_last_runtime_status(runtime_status)
        return notice["message"], [], None, None, notice

    try:
        payload = json.loads(raw_result)
    except Exception:
        cleaned = _clean_answer_text(str(raw_result).strip())
        runtime_status = _build_runtime_status(
            path="direct_rag",
            allow_web=False,
            web_search_called=False,
            web_result_count=0,
            used_local_rag=True,
        )
        _set_last_runtime_status(runtime_status)
        return (
            cleaned or "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。",
            None,
            None,
            None,
            None,
        )

    answer = _clean_answer_text(str(payload.get("answer", "")).strip())
    citations = payload.get("citations", [])
    retrieval = payload.get("retrieval", [])
    confidence = payload.get("confidence", "low")
    system_notice = payload.get("system_notice")

    if not answer:
        answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"

    runtime_status = _build_runtime_status(
        path="direct_rag",
        allow_web=False,
        web_search_called=False,
        web_result_count=0,
        used_local_rag=True,
        retrieval_count=len(retrieval) if isinstance(retrieval, list) else None,
        confidence=confidence,
    )
    _set_last_runtime_status(runtime_status)
    return answer, citations, retrieval, confidence, system_notice
# =============================================================


if "rag_service" not in st.session_state:
    st.session_state.rag_service = RagSummarizeService()

if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.subheader("导航")
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

    # 只在导览页显示设置面板
    if st.session_state.current_page == GUIDE_PAGE:
        render_guide_sidebar(current_page=st.session_state.current_page, guide_page=GUIDE_PAGE)
    else:
        st.caption("浏览模式")


if st.session_state.current_page == HOME_PAGE:
    _render_homepage()
elif st.session_state.current_page == GUIDE_PAGE:
    render_guide_page(
        run_agent_request_streaming=_run_agent_request_streaming,
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
