import json
import os
import re
import sys
from typing import Any

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from model.factory import chat_model
from rag.vector_store import VectorStoreService


TEST_CASES = [
    {
        "question": "三江侗族织绣纹样有哪些典型构成元素？",
        "expected_source": "广西三江侗族织绣纹样形意解构与创新设计_吴婷婷.pdf",
        "expected_keywords": ["三江", "纹样", "构成", "元素"],
    },
    {
        "question": "侗族八菜一汤纹样有什么文化寓意？",
        "expected_source": "侗族“八菜一汤”刺绣纹样解析及创新运用研究_刘佳琪.pdf",
        "expected_keywords": ["八菜一汤", "文化", "寓意"],
    },
    {
        "question": "肇兴侗寨刺绣纹样有哪些美学特征？",
        "expected_source": "肇兴侗寨刺绣纹样的美学特征分析_左小敏.pdf",
        "expected_keywords": ["肇兴", "刺绣纹样", "美学", "特征"],
    },
    {
        "question": "从江侗绣传统纹样在数字化应用上有哪些方向？",
        "expected_source": "从江侗绣传统纹样数字化应用研究_李源.pdf",
        "expected_keywords": ["从江", "侗绣", "数字化", "应用"],
    },
    {
        "question": "三江侗族刺绣纹样在文创产品设计中的应用有哪些？",
        "expected_source": "三江侗族刺绣纹样在文创产品设计中的应用与实践研究——以三江侗族丝巾设计为例_张文州.pdf",
        "expected_keywords": ["三江", "文创", "产品设计", "应用"],
    },
]


class StandaloneRerankEvaluator:
    def __init__(self, recall_k: int = 12, rerank_k: int = 6):
        self.recall_k = recall_k
        self.rerank_k = rerank_k
        self.vector_store_service = VectorStoreService()
        self.retriever = self.vector_store_service.vector_store.as_retriever(search_kwargs={"k": recall_k})
        self.rerank_chain = self._init_rerank_chain()

    def _init_rerank_chain(self):
        prompt = PromptTemplate.from_template(
            """
你是一个RAG检索重排助手。
请判断“用户问题”和“候选资料”之间的相关性，返回JSON，不要输出其他内容。

评分标准：
- 9~10：直接回答问题，信息具体，几乎可直接作为最终答案依据
- 7~8：高度相关，有明显帮助，但不是最直接答案
- 4~6：部分相关，只能提供背景信息
- 0~3：基本无关，或噪声较多

用户问题：
{query}

候选资料：
{document}

只返回：
{{"score": 0-10, "reason": "不超过30字"}}
""".strip()
        )
        return prompt | chat_model | StrOutputParser()

    def retrieve(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def lexical_score(self, query: str, doc: Document) -> float:
        content = (doc.page_content or "")[:1500]
        if not query or not content:
            return 0.0

        tokens = [
            item.strip() for item in re.split(r"[，。！？；、\s]+", query) if item.strip()
        ]
        score = 0.0
        for token in tokens:
            if token and token in content:
                score += 1.0

        metadata = doc.metadata or {}
        if metadata.get("keywords") and metadata.get("keywords") != "未标注":
            score += 0.2
        if metadata.get("topic") and metadata.get("topic") != "其他":
            score += 0.1
        return round(score, 4)

    def llm_rerank_one(self, query: str, doc: Document) -> dict[str, Any]:
        content = (doc.page_content or "").strip()[:1200]
        last_error = ""
        for attempt in range(1, 4):
            try:
                raw = self.rerank_chain.invoke({"query": query, "document": content})
                result = self._parse_rerank_output(raw)
                result["attempt"] = attempt
                return result
            except Exception as exc:
                last_error = str(exc)
        fallback_score = self.lexical_score(query, doc)
        return {
            "score": min(10.0, round(fallback_score, 4)),
            "reason": f"LLM失败回退:{last_error[:18]}",
            "attempt": 3,
            "fallback": True,
        }

    def _parse_rerank_output(self, raw_text: str) -> dict[str, Any]:
        text = (raw_text or "").strip()
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return {"score": 0.0, "reason": f"解析失败: {text[:60]}"}

        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"score": 0.0, "reason": f"JSON失败: {text[:60]}"}

        score = data.get("score", 0)
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0
        score = max(0.0, min(10.0, score))
        reason = str(data.get("reason", "")).strip()[:30]
        return {"score": score, "reason": reason}

    def evaluate_case(self, case: dict[str, Any]) -> dict[str, Any]:
        question = case["question"]
        expected_source = case["expected_source"]
        expected_keywords = case.get("expected_keywords", [])

        docs = self.retrieve(question)
        lexical_ranked = sorted(
            [{"doc": doc, "lexical_score": self.lexical_score(question, doc)} for doc in docs],
            key=lambda item: item["lexical_score"],
            reverse=True,
        )

        coarse_candidates = lexical_ranked[: self.rerank_k]
        reranked = []
        for item in coarse_candidates:
            rerank_result = self.llm_rerank_one(question, item["doc"])
            reranked.append(
                {
                    "doc": item["doc"],
                    "lexical_score": item["lexical_score"],
                    "rerank_score": rerank_result["score"],
                    "reason": rerank_result["reason"],
                }
            )
        reranked.sort(key=lambda item: item["rerank_score"], reverse=True)

        before_sources = [self._source_name(item["doc"]) for item in coarse_candidates]
        after_sources = [self._source_name(item["doc"]) for item in reranked]

        before_hit = expected_source in before_sources
        after_hit = expected_source in after_sources
        before_mrr = self._mrr(before_sources, expected_source)
        after_mrr = self._mrr(after_sources, expected_source)

        top_after = reranked[:3]
        keyword_overlap = []
        for item in top_after:
            text = item["doc"].page_content or ""
            overlap = [kw for kw in expected_keywords if kw in text]
            keyword_overlap.append(
                {
                    "source": self._source_name(item["doc"]),
                    "matched_keywords": overlap,
                }
            )

        return {
            "question": question,
            "expected_source": expected_source,
            "before_hit@6": before_hit,
            "after_hit@6": after_hit,
            "before_mrr": before_mrr,
            "after_mrr": after_mrr,
            "before_top6": [self._brief_item(item["doc"], item["lexical_score"], None, "") for item in coarse_candidates],
            "after_top6": [
                self._brief_item(
                    item["doc"],
                    item["lexical_score"],
                    item["rerank_score"],
                    item["reason"],
                    item.get("attempt"),
                    item.get("fallback", False),
                )
                for item in reranked
            ],
            "keyword_overlap": keyword_overlap,
        }

    def run(self, cases: list[dict[str, Any]]) -> dict[str, Any]:
        results = [self.evaluate_case(case) for case in cases]
        before_hits = sum(1 for item in results if item["before_hit@6"])
        after_hits = sum(1 for item in results if item["after_hit@6"])
        before_mrr = round(sum(item["before_mrr"] for item in results) / max(len(results), 1), 4)
        after_mrr = round(sum(item["after_mrr"] for item in results) / max(len(results), 1), 4)

        return {
            "summary": {
                "cases": len(results),
                "recall_before@6": round(before_hits / max(len(results), 1), 4),
                "recall_after@6": round(after_hits / max(len(results), 1), 4),
                "mrr_before": before_mrr,
                "mrr_after": after_mrr,
            },
            "details": results,
        }

    def _brief_item(self, doc: Document, lexical_score: float, rerank_score: float | None, reason: str, attempt: int | None = None, fallback: bool = False) -> dict[str, Any]:
        metadata = doc.metadata or {}
        return {
            "source": self._source_name(doc),
            "page": metadata.get("page"),
            "topic": metadata.get("topic"),
            "knowledge_layer": metadata.get("knowledge_layer"),
            "lexical_score": lexical_score,
            "rerank_score": rerank_score,
            "reason": reason,
            "attempt": attempt,
            "fallback": fallback,
            "snippet": (doc.page_content or "").strip()[:160],
        }

    def _source_name(self, doc: Document) -> str:
        metadata = doc.metadata or {}
        source = metadata.get("source") or metadata.get("file_path") or metadata.get("path") or "unknown"
        return os.path.basename(str(source))

    def _mrr(self, ranked_sources: list[str], expected_source: str) -> float:
        for idx, source in enumerate(ranked_sources, start=1):
            if source == expected_source:
                return round(1 / idx, 4)
        return 0.0


if __name__ == "__main__":
    evaluator = StandaloneRerankEvaluator(recall_k=12, rerank_k=6)
    report = evaluator.run(TEST_CASES)
    print(json.dumps(report, ensure_ascii=False, indent=2))
