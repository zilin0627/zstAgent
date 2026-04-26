import os
import csv
import json
import urllib.parse
import urllib.request

from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
from utils.path_tool import get_abs_path
from utils.config_handler import agent_config
from utils.logger_handler import logger


rag = RagSummarizeService()
_exhibits_index: dict[str, dict] = {}


def _looks_like_useful_public_url(url: str) -> bool:
    raw = (url or "").strip().lower()
    if not raw.startswith(("http://", "https://")):
        return False

    blocked_tokens = [
        "duckduckgo.com",
        "localhost",
        "127.0.0.1",
        "/html/",
    ]
    if any(token in raw for token in blocked_tokens):
        return False
    return True



@tool(description="识别当前用户问题属于哪类任务，并给出建议路由。返回 JSON 字符串。")
def classify_intent(query: str) -> str:
    q = (query or "").strip()

    if not q:
        return json.dumps(
            {
                "intent": "unknown",
                "need_rag": True,
                "need_web": False,
                "need_human": False,
            },
            ensure_ascii=False,
        )

    lower_q = q.lower()

    if any(token in q for token in ["展签", "展板", "说明牌"]):
        intent = "label"
    elif any(token in q for token in ["faq", "常见问题", "观众会问"]):
        intent = "faq"
    elif any(token in q for token in ["研究", "来源", "地域差异", "象征", "比较", "文献"]):
        intent = "research"
    elif any(token in q for token in ["设计", "转化", "配色", "文创", "包装", "海报", "方案"]):
        intent = "design"
    else:
        intent = "guide"

    need_web = any(token in q for token in ["最新", "现在", "近期", "官网", "网址", "链接"])
    need_human = any(token in q for token in ["投诉", "退款", "人工", "联系工作人员"])

    if "http" in lower_q or "www." in lower_q:
        need_web = True

    return json.dumps(
        {
            "intent": intent,
            "need_rag": True,
            "need_web": need_web,
            "need_human": need_human,
        },
        ensure_ascii=False,
    )


@tool(description="从向量存储中检索参考资料，返回 JSON 字符串，包含 context（可直接用于生成回答的文档原文）/citations/confidence。请基于 context 内容组织最终回答，不要复述 context 字段本身。")
def rag_summarize(query: str) -> str:
    payload = rag.retrieve_docs_with_meta(query)
    context = rag._build_context_from_docs(payload["docs"])
    return json.dumps(
        {
            "context": context,
            "citations": payload["citations"],
            "confidence": payload["confidence"],
            "queries": payload["queries"],
        },
        ensure_ascii=False,
    )


@tool(description="联网搜索公开网页信息（用于补充最新背景），返回JSON字符串，包含title/url/snippet列表")
def web_search(query: str) -> str:
    q = (query or "").strip()
    if not q:
        return json.dumps({"query": "", "results": []}, ensure_ascii=False)

    try:
        params = urllib.parse.urlencode(
            {
                "q": q,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            }
        )
        url = f"https://api.duckduckgo.com/?{params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="ignore"))

        results = []
        abstract = (payload.get("AbstractText") or "").strip()
        abstract_url = (payload.get("AbstractURL") or "").strip()
        heading = (payload.get("Heading") or "").strip()
        if abstract and abstract_url:
            results.append(
                {
                    "title": heading or q,
                    "url": abstract_url,
                    "snippet": abstract[:500],
                }
            )

        for item in payload.get("RelatedTopics", [])[:10]:
            topics = item.get("Topics") if isinstance(item, dict) else None
            if topics:
                for sub in topics[:5]:
                    text = (sub.get("Text") or "").strip()
                    first_url = (sub.get("FirstURL") or "").strip()
                    if text and first_url:
                        results.append(
                            {"title": text[:80], "url": first_url, "snippet": text[:500]}
                        )
            else:
                text = (item.get("Text") or "").strip() if isinstance(item, dict) else ""
                first_url = (
                    (item.get("FirstURL") or "").strip() if isinstance(item, dict) else ""
                )
                if text and first_url:
                    results.append(
                        {"title": text[:80], "url": first_url, "snippet": text[:500]}
                    )

        dedup = []
        seen = set()
        for result in results:
            link = result.get("url", "")
            if not _looks_like_useful_public_url(link):
                continue
            if link not in seen:
                seen.add(link)
                dedup.append(result)
            if len(dedup) >= 5:
                break

        return json.dumps({"query": q, "results": dedup}, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"[web_search]联网检索失败: {str(e)}")
        return json.dumps({"query": q, "results": []}, ensure_ascii=False)


def _load_exhibits():
    if _exhibits_index:
        return

    if "exhibits_data_path" not in agent_config:
        logger.warning("[fetch_exhibit]配置中缺少 exhibits_data_path 字段，跳过展品索引加载")
        return

    path = get_abs_path(agent_config["exhibits_data_path"])
    if not os.path.exists(path):
        logger.warning(f"[fetch_exhibit]展品数据文件不存在: {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                exhibit_id = (row.get("id") or "").strip()
                name = (row.get("name") or "").strip()
                if exhibit_id:
                    _exhibits_index[exhibit_id.lower()] = row
                if name:
                    _exhibits_index[name.lower()] = row
    except Exception as e:
        logger.error(f"[fetch_exhibit]加载展品数据出错: {str(e)}", exc_info=True)


@tool(description="按展品编号或名称检索展品/纹样条目（示例：E001 或 某某纹样），返回结构化信息字符串；未找到返回空字符串")
def fetch_exhibit(query: str) -> str:
    _load_exhibits()
    if not _exhibits_index:
        return ""

    key = (query or "").strip().lower()
    if not key:
        return ""

    row = _exhibits_index.get(key)
    if not row:
        return ""

    parts = []
    for k in ["id", "name", "summary", "source", "era", "technique", "region"]:
        v = (row.get(k) or "").strip()
        if v:
            parts.append(f"{k}={v}")
    return "; ".join(parts)


@tool(description="当资料不足、置信度过低或需要人工接入时，返回统一的兜底建议。")
def handoff_to_human(reason: str) -> str:
    r = (reason or "").strip() or "资料覆盖不足"
    return json.dumps(
        {
            "status": "handoff",
            "reason": r,
            "message": "当前资料不足以给出高置信度回答，建议转交人工讲解员、研究人员或平台管理员进一步处理。",
        },
        ensure_ascii=False,
    )
