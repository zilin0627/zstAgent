import json
import re
import sys
from json import JSONDecoder
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent
PAGES_DIR = PROJECT_ROOT / "pages"
for path in (PROJECT_ROOT, PAGES_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from agent.react_agent import ReactAgent
from rag.rag_service import RagSummarizeService
from cocreate_page import build_cocreate_query
from scenario_page import SCENARIO_APPLICATIONS, B_SIDE_USERS, C_SIDE_USERS, BUSINESS_MODELS
from guide_page import GUIDE_SAMPLE_QUESTIONS, MODE_MAP

app = FastAPI(title="侗绣平台 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/assets", StaticFiles(directory=str(PROJECT_ROOT / "assets")), name="assets")

PROJECT_DATA_DIR = PROJECT_ROOT / "data" / "platform"
_pattern_items = json.loads((PROJECT_DATA_DIR / "pattern_atlas.json").read_text(encoding="utf-8"))
_pattern_scan_items = json.loads((PROJECT_DATA_DIR / "pattern_scans.json").read_text(encoding="utf-8"))
_cultural_showcase = json.loads((PROJECT_DATA_DIR / "cultural_showcase.json").read_text(encoding="utf-8"))
_ai_workflow = json.loads((PROJECT_DATA_DIR / "ai_workflow.json").read_text(encoding="utf-8"))


def _safe_init_services():
    rag_service = None
    agent = None
    startup_error = None
    try:
        rag_service = RagSummarizeService()
        agent = ReactAgent()
    except Exception as exc:
        startup_error = str(exc)
    return rag_service, agent, startup_error


_rag_service, _agent, _service_startup_error = _safe_init_services()


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
            obj, _ = decoder.raw_decode(text[i:])
            if isinstance(obj, dict) and "answer" in obj and "citations" in obj:
                prefix = text[:i].strip()
                answer = prefix if prefix else str(obj.get("answer", "")).strip()
                return answer, obj
        except Exception:
            continue

    return text, None


def _clean_answer_text(answer: str) -> str:
    if not answer:
        return answer

    cleaned = answer
    cleaned = re.sub(r"\[\[?/?CITATIONS\]?\]", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\{\s*\"answer\"\s*:\s*.*?\"citations\"\s*:\s*\[.*?\]\s*\}", " ", cleaned, flags=re.S)
    cleaned = re.sub(r'\s*\{"query"\s*:\s*".*?"\s*,\s*"results"\s*:\s*\[.*?\]\}\s*', " ", cleaned, flags=re.S)
    cleaned = re.sub(r"(?m)^\s*#{1,6}\s*网络补充来源\s*$", "网络补充来源", cleaned)
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


def _run_agent_request(prompt: str, context: dict):
    if _agent is None:
        detail = _service_startup_error or "Agent service is unavailable"
        return f"Agent 暂不可用：{detail}", None

    response_message = []
    for chunk in _agent.execute_stream(prompt, context=context):
        response_message.append(chunk)
    full_text = "".join(response_message).strip()
    answer, citations = _extract_citations(full_text)
    answer = _clean_answer_text(answer.strip())
    if not answer:
        answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
    if not context.get("citations_enabled", True):
        citations = None
    return answer, citations


def _run_direct_rag_request(prompt: str):
    if _rag_service is None:
        detail = _service_startup_error or "RAG service is unavailable"
        return f"RAG 暂不可用：{detail}", None

    raw_result = _rag_service.rag_summarize_with_citations(prompt)
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


def _get_pattern_item(name: str) -> dict | None:
    for item in _pattern_items:
        if item["name"] == name:
            return item
    return None


def _get_related_scan_items(pattern_name: str) -> list[dict]:
    return [item for item in _pattern_scan_items if item.get("related_pattern") == pattern_name]


class GuideRequest(BaseModel):
    prompt: str
    mode: str = "导览讲解"
    strategy: str = "快速导览（直连RAG）"
    audience: str = "大众观众"
    citations_enabled: bool = True
    allow_web: bool = False


class StudioRequest(BaseModel):
    pattern_name: str
    theme: str
    target: str
    tone: str
    extra: str = ""
    allow_web: bool = True
    generation_mode: str = "快速模式（直连知识库）"


@app.get("/api/health")
def health_check():
    return {
        "ok": True,
        "ragReady": _rag_service is not None,
        "agentReady": _agent is not None,
        "startupError": _service_startup_error,
    }


@app.get("/api/platform/content")
def get_platform_content():
    return {
        "patterns": _pattern_items,
        "patternScans": _pattern_scan_items,
        "culturalShowcase": _cultural_showcase,
        "aiWorkflow": _ai_workflow,
        "guideSampleQuestions": GUIDE_SAMPLE_QUESTIONS,
        "guideModes": list(MODE_MAP.keys()),
        "scenarioApplications": SCENARIO_APPLICATIONS,
        "bSideUsers": B_SIDE_USERS,
        "cSideUsers": C_SIDE_USERS,
        "businessModels": BUSINESS_MODELS,
    }


@app.post("/api/guide/query")
def guide_query(payload: GuideRequest):
    mode = MODE_MAP.get(payload.mode, "guide")
    use_direct_rag = payload.strategy == "快速导览（直连RAG）"
    use_agent = (not use_direct_rag) or mode != "guide"

    if use_agent:
        answer, citations = _run_agent_request(
            payload.prompt,
            {
                "mode": mode,
                "audience": payload.audience,
                "citations_enabled": payload.citations_enabled,
                "allow_web": payload.allow_web,
            },
        )
    else:
        answer, citations = _run_direct_rag_request(payload.prompt)

    if not payload.citations_enabled:
        citations = None

    return {
        "answer": answer,
        "citations": citations,
    }


@app.post("/api/studio/generate")
def studio_generate(payload: StudioRequest):
    related_scans = _get_related_scan_items(payload.pattern_name)
    cocreate_prompt = build_cocreate_query(
        payload.pattern_name,
        payload.theme,
        payload.target,
        payload.tone,
        payload.extra,
        related_scans,
        payload.allow_web,
        _get_pattern_item,
    )

    if payload.generation_mode == "快速模式（直连知识库）":
        answer, citations = _run_direct_rag_request(cocreate_prompt)
    else:
        answer, citations = _run_agent_request(
            cocreate_prompt,
            {
                "mode": "research",
                "audience": "专业观众",
                "citations_enabled": True,
                "allow_web": payload.allow_web,
            },
        )

    return {
        "answer": answer,
        "citations": citations,
    }
