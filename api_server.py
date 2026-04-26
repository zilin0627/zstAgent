import json
import re
import sys
from json import JSONDecoder
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.tools.agent_tools import classify_intent
from agent.react_agent import ReactAgent
from rag.rag_service import RagSummarizeService
from pages.cocreate_page import build_cocreate_query
from pages.scenario_page import SCENARIO_APPLICATIONS, B_SIDE_USERS, C_SIDE_USERS, BUSINESS_MODELS
from pages.guide_page import GUIDE_SAMPLE_QUESTIONS, MODE_MAP

app = FastAPI(title="侗绣平台 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/assets", StaticFiles(directory=str(PROJECT_ROOT / "assets")), name="assets")
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

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


def _normalize_citations(citations):
    if isinstance(citations, dict):
        return citations.get("citations", []) or []
    if isinstance(citations, list):
        return citations
    return []


def _finalize_agent_response(full_text: str, rag_citations: list[dict], web_citations: list[dict], citations_enabled: bool):
    citation_payload = _extract_citations(full_text)
    if isinstance(citation_payload, (list, tuple)):
        answer = citation_payload[0] if len(citation_payload) >= 1 else full_text
        citations = citation_payload[1] if len(citation_payload) >= 2 else None
    else:
        answer = full_text
        citations = None

    answer = _clean_answer_text(str(answer or "").strip())
    if not citations and rag_citations:
        citations = rag_citations
    citations = _merge_citations(citations, web_citations)
    citations = _normalize_citations(citations)
    if not citations_enabled:
        citations = None
    return answer, citations


def _merge_citations(base_citations, extra_citations):
    base_items = _normalize_citations(base_citations)
    extra_items = _normalize_citations(extra_citations)
    if not extra_items:
        return base_items
    if not base_items:
        return extra_items

    merged = []
    seen = set()
    for item in base_items + extra_items:
        if not isinstance(item, dict):
            continue
        key = (
            str(item.get("source", "")),
            str(item.get("page", "")),
            str(item.get("url", "")),
            str(item.get("snippet", ""))[:80],
        )
        if key in seen:
            continue
        seen.add(key)
        normalized = dict(item)
        normalized["index"] = len(merged) + 1
        merged.append(normalized)
    return merged


def _extract_tool_citations(tool_text: str) -> list[dict]:
    if not tool_text:
        return []
    try:
        payload = json.loads(tool_text)
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    return _normalize_citations(payload.get("citations"))


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


def _parse_agent_stream_chunk(chunk: str):
    if not chunk.startswith("[[THOUGHT]]"):
        return chunk, [], []

    thought_text = chunk[len("[[THOUGHT]]") :].strip()
    if not thought_text.startswith("TOOL::"):
        return "", [], []

    try:
        _, tool_name, tool_text = thought_text.split("::", 2)
    except ValueError:
        return "", [], []

    rag_citations = _extract_tool_citations(tool_text) if tool_name == "rag_summarize" else []
    web_citations = _extract_web_results_from_tool_text(tool_text) if tool_name == "web_search" else []
    return "", rag_citations, web_citations


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
    rag_citations: list[dict] = []
    web_citations: list[dict] = []
    for chunk in _agent.execute_stream(prompt, context=context):
        visible_chunk, chunk_rag_citations, chunk_web_citations = _parse_agent_stream_chunk(chunk)
        if chunk_rag_citations:
            rag_citations.extend(chunk_rag_citations)
        if chunk_web_citations:
            web_citations.extend(chunk_web_citations)
        if visible_chunk:
            response_message.append(visible_chunk)
    full_text = "".join(response_message).strip()
    citation_payload = _extract_citations(full_text)
    if isinstance(citation_payload, (list, tuple)):
        answer = citation_payload[0] if len(citation_payload) >= 1 else full_text
        citations = citation_payload[1] if len(citation_payload) >= 2 else None
    else:
        answer = full_text
        citations = None
    answer = _clean_answer_text(str(answer or "").strip())
    if not citations and rag_citations:
        citations = rag_citations
    citations = _merge_citations(citations, web_citations)
    if not answer:
        answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
    if not context.get("citations_enabled", True):
        citations = None
    return answer, citations


def _run_direct_rag_request(prompt: str):
    if _rag_service is None:
        detail = _service_startup_error or "RAG service is unavailable"
        return f"RAG 暂不可用：{detail}", None

    try:
        raw_result = _rag_service.rag_summarize_with_citations(prompt)
    except Exception as exc:
        err_lower = str(exc).lower()
        if any(kw in err_lower for kw in ("ssl", "eof", "connection", "timeout", "max retries")):
            return "当前 AI 服务连接异常（SSL / 网络问题），请检查网络后重试。", None
        return f"知识库查询失败，请稍后重试。（{str(exc)[:120]}）", None

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


def _route_mode_from_prompt(prompt: str, fallback_mode: str = "guide") -> str:
    try:
        raw = classify_intent.invoke(prompt)
        data = json.loads(raw)
        intent = data.get("intent", "guide")
    except Exception:
        return fallback_mode

    mapping = {
        "guide": "guide",
        "label": "label",
        "faq": "faq",
        "research": "research",
        "design": "research",
    }
    return mapping.get(intent, fallback_mode)

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
    auto_route: bool = True


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
    requested_mode = MODE_MAP.get(payload.mode, "guide")
    actual_mode = _route_mode_from_prompt(payload.prompt, requested_mode) if payload.auto_route else requested_mode

    use_direct_rag = payload.strategy == "快速导览（直连RAG）"
    if actual_mode != "guide":
        use_direct_rag = False

    if use_direct_rag:
        answer, citations = _run_direct_rag_request(payload.prompt)
        retrieval = None
        confidence = None
    else:
        answer, citations = _run_agent_request(
            payload.prompt,
            {
                "mode": actual_mode,
                "audience": payload.audience,
                "citations_enabled": payload.citations_enabled,
                "allow_web": payload.allow_web,
                "lite_guide": True,
            },
        )
        retrieval = None
        confidence = None

    if not payload.citations_enabled:
        citations = None

    return {
        "answer": answer,
        "citations": citations,
        "mode": actual_mode,
        "retrieval": retrieval,
        "confidence": confidence,
    }


@app.post("/api/studio/generate")
def studio_generate(payload: StudioRequest):
    try:
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
        return {"answer": answer, "citations": citations}
    except Exception as exc:
        err_lower = str(exc).lower()
        if any(kw in err_lower for kw in ("ssl", "eof", "connection", "timeout", "max retries")):
            friendly = "当前 AI 服务连接异常（SSL / 网络问题），请检查网络后重试。"
        else:
            friendly = f"生成时出现异常，请稍后重试。（{str(exc)[:120]}）"
        return {"answer": friendly, "citations": None, "error": True}


# ── SSE 流式端点（供 HTML 前端使用）────────────────────────
class GuideStreamRequest(BaseModel):
    prompt: str
    mode: str = "guide"
    audience: str = "大众观众"
    citations_enabled: bool = True
    allow_web: bool = False
    use_agent: bool = True


@app.post("/api/guide/stream")
def guide_stream(payload: GuideStreamRequest):
    def event_generator():
        try:
            if payload.use_agent and _agent is not None:
                response_message = []
                rag_citations: list[dict] = []
                web_citations: list[dict] = []
                for chunk in _agent.execute_stream(
                    payload.prompt,
                    context={
                        "mode": payload.mode,
                        "audience": payload.audience,
                        "citations_enabled": payload.citations_enabled,
                        "allow_web": payload.allow_web,
                    },
                ):
                    visible_chunk, chunk_rag_citations, chunk_web_citations = _parse_agent_stream_chunk(chunk)
                    if chunk_rag_citations:
                        rag_citations.extend(chunk_rag_citations)
                    if chunk_web_citations:
                        web_citations.extend(chunk_web_citations)
                    if visible_chunk:
                        response_message.append(visible_chunk)
                full_text = "".join(response_message).strip()
                answer, citations = _finalize_agent_response(
                    full_text,
                    rag_citations,
                    web_citations,
                    payload.citations_enabled,
                )
                if not answer:
                    answer = "我已检索到相关资料，但本次输出格式异常。请重试一次，或换一种问法。"
                data = json.dumps({"chunk": answer, "citations": citations}, ensure_ascii=False)
                yield f"data: {data}\n\n"
            elif _rag_service is not None:
                answer, citations = _run_direct_rag_request(payload.prompt)
                data = json.dumps({"chunk": answer, "citations": citations}, ensure_ascii=False)
                yield f"data: {data}\n\n"
            else:
                yield f"data: {json.dumps({'chunk': '服务暂时不可用，请稍后重试。'})}\n\n"
        except Exception as e:
            err_msg = str(e)
            if "SSLError" in err_msg or "ConnectionPool" in err_msg or "dashscope" in err_msg:
                friendly = "网络连接失败，无法访问 AI 服务（可能是 VPN 或网络问题），请检查网络后重试。"
            else:
                friendly = f"出现错误：{err_msg[:200]}"
            yield f"data: {json.dumps({'chunk': friendly, 'error': True}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── HTML 页面路由 ────────────────────────────────────────────
@app.get("/")
def page_home(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/guide")
def page_guide(request: Request):
    return templates.TemplateResponse(request, "guide.html", context={
        "sample_questions": GUIDE_SAMPLE_QUESTIONS,
        "mode_options": list(MODE_MAP.keys()),
    })

@app.get("/pattern")
def page_pattern(request: Request):
    return templates.TemplateResponse(request, "pattern.html", context={
        "patterns": _pattern_items,
        "scans": _pattern_scan_items,
    })

@app.get("/cocreate")
def page_cocreate(request: Request):
    pattern_names = [p["name"] for p in _pattern_items]
    return templates.TemplateResponse(request, "cocreate.html", context={
        "pattern_names": pattern_names,
        "patterns": _pattern_items,
        "scans": _pattern_scan_items,
    })
