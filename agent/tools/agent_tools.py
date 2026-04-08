import os
import csv
import json
import urllib.parse
import urllib.request
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
from rag.vector_store import VectorStoreService
from utils.path_tool import get_abs_path
from utils.config_handler import agent_config
from utils.logger_handler import logger



vector_store = VectorStoreService()
rag = RagSummarizeService()

_exhibits_index: dict[str, dict] = {}

@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    """
    从向量存储中检索参考资料， 并总结问题的答案
    """
    # 返回 JSON 字符串，包含 answer 和 citations，方便上层展示引用溯源
    return rag.rag_summarize_with_citations(query)


@tool(description="联网搜索公开网页信息（用于补充最新背景），返回JSON字符串，包含title/url/snippet列表")
def web_search(query: str) -> str:
    """
    轻量联网检索：
    - 使用 DuckDuckGo Instant Answer API（无需密钥）
    - 返回结构化 JSON，便于模型整合
    """
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
        with urllib.request.urlopen(req, timeout=5) as resp:
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
            # DDG 的 RelatedTopics 可能是列表嵌套
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

        # 去重并截断
        dedup = []
        seen = set()
        for r in results:
            k = r.get("url", "")
            if k and k not in seen:
                seen.add(k)
                dedup.append(r)
            if len(dedup) >= 8:
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

    # 返回紧凑结构，便于模型引用
    parts = []
    for k in ["id", "name", "summary", "source", "era", "technique", "region"]:
        v = (row.get(k) or "").strip()
        if v:
            parts.append(f"{k}={v}")
    return "; ".join(parts)

if __name__ == "__main__":
    print(fetch_exhibit("E001"))