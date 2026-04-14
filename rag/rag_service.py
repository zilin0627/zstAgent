"""
升级版 rag_service.py
目标：
1. 保留原有 RAG 能力
2. 增加任务分类与工作流路由
3. 支持知识问答 / 联网补充 / 设计提案
4. 输出统一结构化结果，方便前端展示与 Agent 扩展
"""

import json
import os
import re
from typing import Any, Callable

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from model.factory import chat_model
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts


TERM_ALIASES: dict[str, list[str]] = {
    "八菜一汤": ["八菜一汤", "八菜一汤纹样", "混沌花", "混沌花纹", "八菜一汤 又称 混沌花"],
    "混沌花": ["混沌花", "混沌花纹", "八菜一汤", "八菜一汤纹样"],
    "萨巴天": ["萨巴天", "萨巴天女神", "祖源歌", "创世女神 萨巴天"],
    "动物纹样": ["动物纹样", "龙 凤 鱼 鸟 蝴蝶 牛 马 鸡 虎", "动物题材 侗绣纹样"],
    "植物纹样": ["植物纹样", "花草树木 植物题材 侗绣纹样"],
    "几何纹样": ["几何纹样", "菱形 折线 井纹 八角花 几何图案"],
}


class RagSummarizeService:
    def __init__(self, web_search_fn: Callable[[str], list[dict]] | None = None):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()

        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)

        self.model = chat_model
        self.chain = self._init_chain()
        self.recovery_notice: dict[str, str] | None = None

        # 预留联网搜索能力：外部可注入函数
        # web_search_fn(query) -> [{"title": "...", "snippet": "...", "url": "..."}]
        self.web_search_fn = web_search_fn

    def _init_chain(self):
        return self.prompt_template | self.model | StrOutputParser()

    # =========================
    # 1. Query Rewrite
    # =========================
    def rewrite_query(self, query: str) -> list[str]:
        q = (query or "").strip()
        if not q:
            return []

        rewrites = [q]
        focus = self._detect_query_focus(q)
        alias_rewrites = self._expand_alias_queries(q)

        noisy_tokens = ["请问", "帮我", "你能", "能不能", "一下", "介绍", "说说", "我想知道", "麻烦"]
        compact = q
        for token in noisy_tokens:
            compact = compact.replace(token, "")
        compact = " ".join(compact.split()).strip()

        if compact and compact != q:
            rewrites.append(compact)

        rewrites.extend(alias_rewrites)

        if focus == "taxonomy":
            rewrites.extend(
                [
                    f"侗族织绣纹样 构成元素 分类 {compact or q}",
                    f"侗绣纹样 类型 类别 {compact or q}",
                    f"侗族刺绣 图案 构成 要素 {compact or q}",
                ]
            )
        elif focus == "meaning":
            rewrites.extend(
                [
                    f"侗族织绣纹样 寓意 象征 {compact or q}",
                    f"侗绣纹样 文化含义 {compact or q}",
                ]
            )
        elif focus == "feature":
            rewrites.extend(
                [
                    f"侗族织绣纹样 特点 特征 {compact or q}",
                    f"侗绣纹样 造型 布局 风格 {compact or q}",
                ]
            )
        elif focus == "scene":
            rewrites.extend(
                [
                    f"侗族织绣纹样 使用 场景 部位 {compact or q}",
                    f"侗绣纹样 服饰 用途 {compact or q}",
                ]
            )

        extracted_tokens = self._extract_query_tokens(compact or q)
        keyword_query = " ".join(
            token for token in extracted_tokens
            if len(token) >= 4
            and token not in {"侗族织绣纹样通常有哪些构成元素"}
            and not re.fullmatch(r"[\u4e00-\u9fff]{2,3}", token)
        )
        if keyword_query and keyword_query not in rewrites:
            rewrites.append(keyword_query)

        domain_tokens = ["侗族", "侗绣", "刺绣", "织绣", "纹样", "文创", "展签", "课程", "包装", "海报"]
        if compact and not any(t in compact for t in domain_tokens):
            rewrites.append(f"侗族刺绣 纹样 {compact}".strip())

        seen = set()
        final_queries = []
        for item in rewrites:
            normalized_item = " ".join(str(item).split()).strip()
            if normalized_item and normalized_item not in seen:
                final_queries.append(normalized_item)
                seen.add(normalized_item)

        return final_queries[:4]

    # =========================
    # 2. 文档检索基础能力
    # =========================
    def retrieve_docs(self, query: str) -> list[Document]:
        try:
            self.recovery_notice = None
            return self.retriever.invoke(query)
        except Exception as e:
            recovered = self.vector_store.recover_if_hnsw_broken(e)
            if not recovered:
                raise

            self.recovery_notice = recovered
            self.retriever = self.vector_store.get_retriever()
            return self.retriever.invoke(query)

    def _extract_query_tokens(self, query: str) -> list[str]:
        q = str(query or "").strip()
        if not q:
            return []

        normalized = re.sub(r"[，。！？；：、】【（）()、,.;:!?\n\t]+", " ", q)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        stopwords = {
            "请问", "帮我", "你能", "能不能", "一下", "介绍", "说说", "我想知道", "麻烦",
            "通常", "一般", "一下子", "哪些", "什么", "怎么", "如何", "是否", "一下吧",
        }
        domain_phrases = [
            "侗族织绣", "侗族刺绣", "侗绣纹样", "侗族纹样", "刺绣纹样", "织绣纹样",
            "构成元素", "生活场景", "几何纹样", "动物纹样", "植物纹样", "人物纹样",
            "八菜一汤", "混沌花", "萨巴天",
        ]

        tokens: list[str] = []
        for phrase in domain_phrases:
            if phrase in q:
                tokens.append(phrase)

        for alias_query in self._expand_alias_queries(q):
            tokens.extend(alias_query.split())

        for part in normalized.split(" "):
            part = part.strip()
            if not part or part in stopwords:
                continue
            if len(part) >= 2:
                tokens.append(part)
            if len(part) >= 4:
                for size in (2, 3):
                    for i in range(0, len(part) - size + 1):
                        piece = part[i:i + size]
                        if piece not in stopwords:
                            tokens.append(piece)

        seen = set()
        final_tokens = []
        for token in tokens:
            if token and token not in seen:
                final_tokens.append(token)
                seen.add(token)
        return final_tokens[:24]

    def _expand_alias_queries(self, query: str) -> list[str]:
        q = str(query or "").strip()
        if not q:
            return []

        rewrites: list[str] = []
        for term, aliases in TERM_ALIASES.items():
            if term in q:
                rewrites.extend(aliases)

        if "什么元素" in q or "有哪些元素" in q:
            if "动物" in q:
                rewrites.extend(TERM_ALIASES.get("动物纹样", []))
            if "植物" in q:
                rewrites.extend(TERM_ALIASES.get("植物纹样", []))
            if "几何" in q:
                rewrites.extend(TERM_ALIASES.get("几何纹样", []))

        if "八菜一汤" in q and "寓意" in q:
            rewrites.extend(["八菜一汤 寓意", "混沌花 寓意", "八菜一汤 文化含义"])

        seen = set()
        final_queries = []
        for item in rewrites:
            normalized_item = " ".join(str(item).split()).strip()
            if normalized_item and normalized_item not in seen:
                final_queries.append(normalized_item)
                seen.add(normalized_item)
        return final_queries[:6]

    def _detect_query_focus(self, query: str) -> str:
        q = str(query or "").strip()
        if not q:
            return "general"

        taxonomy_markers = ["有哪些", "哪几类", "类型", "类别", "构成", "元素", "图案", "纹样", "名称", "具体有哪些", "可以列举"]
        meaning_markers = ["寓意", "含义", "象征", "为什么", "代表什么", "意义"]
        feature_markers = ["特点", "特征", "风格", "审美"]
        scene_markers = ["使用", "场景", "应用", "生活", "用在", "用于", "部位", "服饰"]
        craft_markers = ["技法", "工艺", "针法", "材料", "制作", "怎么做", "绣法", "流程"]
        compare_markers = ["区别", "差异", "不同", "对比", "相比", "比较"]

        has_taxonomy = any(marker in q for marker in taxonomy_markers)
        has_meaning = any(marker in q for marker in meaning_markers)
        has_feature = any(marker in q for marker in feature_markers)
        has_scene = any(marker in q for marker in scene_markers)
        has_craft = any(marker in q for marker in craft_markers)
        has_compare = any(marker in q for marker in compare_markers)

        if has_compare:
            return "compare"
        if has_craft:
            return "craft"
        if has_taxonomy and not has_meaning and not has_scene:
            return "taxonomy"
        if has_feature and not has_meaning:
            return "feature"
        if has_meaning:
            return "meaning"
        if has_scene:
            return "scene"
        return "general"

    def _is_background_like_doc(self, doc: Document) -> bool:
        md = doc.metadata or {}
        section = str(md.get("section", ""))
        content = (doc.page_content or "")[:800]
        background_markers = [
            "摘要", "研究背景", "研究目的", "研究意义", "理论意义", "实践意义",
            "答辩委员会", "关键词：", "关键词", "本文选题", "研究现状",
        ]
        return any(marker in section or marker in content for marker in background_markers)

    def _query_focus_adjustment(self, query: str, doc: Document) -> float:
        focus = self._detect_query_focus(query)
        if focus == "general":
            return 0.0

        md = doc.metadata or {}
        section = str(md.get("section", ""))
        topic = str(md.get("topic", ""))
        knowledge_layer = str(md.get("knowledge_layer", ""))
        keywords = str(md.get("keywords", ""))
        region = str(md.get("region", ""))
        content = (doc.page_content or "")[:1200]

        score = 0.0

        if self._is_background_like_doc(doc):
            score -= 2.2

        if focus == "taxonomy":
            direct_markers = [
                "主要分为", "分为", "类别", "类型", "纹样名称", "纹样内容", "核心布局",
                "动物纹样", "植物纹样", "几何纹样", "文字纹样", "特点", "混沌花", "八菜一汤",
            ]
            weak_markers = ["构图", "载体", "文化景观", "文化符号", "研究背景"]
            if any(marker in section or marker in content or marker in keywords for marker in direct_markers):
                score += 3.0
            if "纹样特征" in topic:
                score += 1.2
            if "基础事实层" in knowledge_layer:
                score += 0.8
            if any(marker in content for marker in weak_markers):
                score -= 0.8
            if "设计应用" in topic:
                score -= 1.2

        if focus == "feature":
            if any(marker in section or marker in content for marker in ["特点", "特征", "风格", "核心布局", "色彩", "造型"]):
                score += 2.2
            if "纹样特征" in topic:
                score += 1.0
            if "基础事实层" in knowledge_layer:
                score += 0.5

        if focus == "meaning":
            if any(marker in content or marker in keywords for marker in ["寓意", "象征", "吉祥", "信仰", "崇拜", "祈福"]):
                score += 2.4
            if "文化内涵" in topic or "文化解释层" in knowledge_layer:
                score += 1.0

        if focus == "scene":
            if any(marker in content or marker in keywords for marker in ["服饰", "背带", "头帕", "鞋面", "场景", "使用", "衣襟", "袖口"]):
                score += 2.0
            if "设计应用" in topic:
                score += 0.6
            if "基础事实层" in knowledge_layer:
                score += 0.4

        if focus == "craft":
            if any(marker in section or marker in content or marker in keywords for marker in ["针法", "绣法", "技法", "材料", "工艺", "制作", "挑花", "平绣"]):
                score += 2.6
            if "设计应用" in topic:
                score -= 0.5
            if "基础事实层" in knowledge_layer:
                score += 0.6

        if focus == "compare":
            compare_markers = ["不同", "差异", "相比", "对比", "各有差异", "分别", "地域"]
            if any(marker in content or marker in section for marker in compare_markers):
                score += 2.8
            if any(region_name in query and region_name in content for region_name in ["三江", "从江", "黎平", "肇兴", "广西", "贵州"]):
                score += 1.0
            if region and region != "未标注":
                score += 0.4

        return round(score, 4)

    def _build_answer_query(self, query: str) -> str:
        focus = self._detect_query_focus(query)
        if focus == "taxonomy":
            return (
                f"{query}\n\n"
                "请直接回答类型、类别或构成要点，优先整理本地资料中已经明确列出的分类。"
                "如果资料同时提供题材分类和表现形式分类，先答更贴近用户问题的主分类，再补充另一层分类。"
                "不要先讲研究背景、文化景观、载体或泛泛的使用场景。"
            )
        if focus == "feature":
            return (
                f"{query}\n\n"
                "请直接概括特点，优先说明造型、布局、色彩、风格和表现方式，并尽量点明地域范围。"
            )
        if focus == "meaning":
            return (
                f"{query}\n\n"
                "请直接回答寓意、象征或文化含义，优先使用本地资料里已有的解释，不要泛泛而谈。"
            )
        if focus == "scene":
            return (
                f"{query}\n\n"
                "请直接回答通常用在哪些服饰部位、器物或生活场景中，优先给出具体位置和用途。"
            )
        if focus == "craft":
            return (
                f"{query}\n\n"
                "请直接回答相关技法、绣法、材料或制作方式，优先提取本地资料中的具体做法与术语。"
            )
        if focus == "compare":
            return (
                f"{query}\n\n"
                "请围绕用户要求做对比，尽量分点说明不同地域或不同对象在纹样、寓意、服饰、技法上的差异，避免混成统一结论。"
            )
        return query

    def _score_doc(self, query: str, doc: Document) -> float:
        q = str(query or "").strip()
        content = (doc.page_content or "")[:1200]
        if not q or not content:
            return 0.0

        tokens = self._extract_query_tokens(q)
        score = 0.0
        for tok in tokens:
            if tok in content:
                score += 1.0 if len(tok) >= 4 else 0.6

        md = doc.metadata or {}
        source_text = " ".join(
            str(md.get(key, ""))
            for key in ["source", "file_name", "title", "section", "topic", "keywords", "knowledge_layer", "region"]
        )
        for tok in tokens:
            if tok and tok in source_text:
                score += 0.35 if len(tok) >= 4 else 0.2

        score += self._query_focus_adjustment(q, doc)

        if md.get("source") or md.get("file_path") or md.get("path"):
            score += 0.2
        if md.get("keywords") and md["keywords"] != "未标注":
            score += 0.1
        if md.get("topic") and md["topic"] != "其他":
            score += 0.1

        return round(score, 4)

    def retrieve_docs_with_meta(self, query: str) -> dict[str, Any]:
        expanded_queries = self.rewrite_query(query)
        merged_docs: list[Document] = []
        seen_keys = set()

        for item in expanded_queries:
            docs = self.retrieve_docs(item)
            for doc in docs:
                md = doc.metadata or {}
                key = (
                    str(md.get("source") or md.get("file_path") or md.get("path") or "unknown"),
                    str(md.get("page") or ""),
                    (doc.page_content or "")[:120],
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                merged_docs.append(doc)

        scored = [{"doc": doc, "score": self._score_doc(query, doc)} for doc in merged_docs]
        scored.sort(key=lambda x: x["score"], reverse=True)

        top_items = scored[:4]
        final_docs = [item["doc"] for item in top_items]
        final_scores = [item["score"] for item in top_items]

        if not final_scores:
            confidence = "low"
        elif max(final_scores) >= 2.0:
            confidence = "high"
        elif max(final_scores) >= 1.0:
            confidence = "medium"
        else:
            confidence = "low"

        retrieval = []
        citations = []

        for idx, item in enumerate(top_items, start=1):
            doc = item["doc"]
            md = doc.metadata or {}
            source = md.get("source") or md.get("file_path") or md.get("path") or "unknown"
            source_name = os.path.basename(str(source)) if source else "unknown"

            retrieval.append(
                {
                    "rank": idx,
                    "score": item["score"],
                    "source": source_name,
                    "page": md.get("page"),
                    "snippet": (doc.page_content or "").strip()[:200],
                    "topic": md.get("topic"),
                    "knowledge_layer": md.get("knowledge_layer"),
                }
            )

            citations.append(
                {
                    "index": idx,
                    "source": source_name,
                    "page": md.get("page"),
                    "snippet": (doc.page_content or "").strip()[:220],
                    "metadata": {
                        "page_label": md.get("page_label"),
                        "total_pages": md.get("total_pages"),
                        "author": md.get("author"),
                        "topic": md.get("topic"),
                        "knowledge_layer": md.get("knowledge_layer"),
                        "keywords": md.get("keywords"),
                    },
                }
            )

        return {
            "queries": expanded_queries,
            "docs": final_docs,
            "retrieval": retrieval,
            "citations": citations,
            "confidence": confidence,
            "focus": self._detect_query_focus(query),
        }

    # =========================
    # 3. 任务分类 / 路由
    # =========================
    def classify_task(self, query: str) -> str:
        q = (query or "").strip()

        if not q:
            return "general_qa"

        design_keywords = [
            "设计", "提案", "方案", "海报", "包装", "课程", "展签", "导览词",
            "文案", "策划", "活动方案", "视觉", "品牌"
        ]
        web_keywords = [
            "最新", "现在", "趋势", "案例", "新闻", "市场", "官网", "网页"
        ]
        knowledge_keywords = [
            "是什么", "有哪些", "为什么", "来源", "寓意", "特点", "构成", "元素", "文化", "区别"
        ]

        has_design = any(word in q for word in design_keywords)
        has_web = any(word in q for word in web_keywords)
        has_knowledge = any(word in q for word in knowledge_keywords)

        # 设计类优先，但如果明显带时效性或外部案例需求，后面可以走设计增强版
        if has_design and has_web:
            return "design_task"

        if has_design:
            return "design_task"

        if has_web:
            return "web_search_task"

        if has_knowledge:
            return "knowledge_qa"

        return "general_qa"

    # =========================
    # 4. Prompt 构建
    # =========================
    def _build_context_from_docs(self, docs: list[Document]) -> str:
        context = ""
        for idx, doc in enumerate(docs, start=1):
            md = doc.metadata or {}
            compact_meta = {
                "source": os.path.basename(str(md.get("source") or md.get("file_path") or md.get("path") or "unknown")),
                "page": md.get("page"),
                "topic": md.get("topic"),
                "knowledge_layer": md.get("knowledge_layer"),
                "keywords": md.get("keywords"),
            }
            context += f"【参考资料{idx}】{(doc.page_content or '').strip()} | 元数据：{compact_meta}\n"
        return context

    def _build_quality_instruction(self, query: str, focus: str) -> str:
        if focus == "taxonomy":
            return (
                f"{query}\n\n"
                "请把答案写得像垂直领域导览员，而不是通用百科：先直接给结论，再列出最关键的具体名称或类别。"
                "如果用户问‘有哪些’或‘能不能列举’，请优先列出资料中明确出现的具体纹样名称、动物名称或分类名称，"
                "不要只停留在抽象大类。优先保留参考资料中的术语，如几何纹、动物纹、植物纹、人物纹、组合纹、混沌花、八菜一汤等；"
                "若不同资料分类口径不完全一致，请明确说明是题材分类、造型分类或构图分类。"
            )
        if focus == "meaning":
            return (
                f"{query}\n\n"
                "请先回答这个纹样具体是什么，再回答它的寓意或文化含义。"
                "如果资料里出现别称、地方名称、神话人物或创世叙事，请优先解释这些本地知识点，"
                "不要泛泛地只说‘自然崇拜’或‘审美表达’。"
            )
        if focus == "feature":
            return (
                f"{query}\n\n"
                "请优先概括造型、布局、色彩和表现方式，尽量使用资料中的具体描述词，不要只给宽泛形容。"
            )
        if focus == "scene":
            return (
                f"{query}\n\n"
                "请优先回答具体使用部位、服饰对象和生活场景，避免把用途和寓意混在一起。"
            )
        return query

    def _invoke_llm(self, query: str, context: str) -> str:
        return self.chain.invoke({"input": query, "context": context})

    # =========================
    # 5. RAG 知识问答
    # =========================
    def rag_answer(self, query: str, task_type: str = "knowledge_qa") -> dict[str, Any]:
        payload = self.retrieve_docs_with_meta(query)
        docs = payload["docs"]
        context = self._build_context_from_docs(docs)
        focus = payload.get("focus") or self._detect_query_focus(query)
        answer = self._invoke_llm(self._build_quality_instruction(self._build_answer_query(query), focus), context)

        result = {
            "task_type": task_type,
            "answer": answer,
            "citations": payload["citations"],
            "retrieval": payload["retrieval"],
            "confidence": payload["confidence"],
            "rewritten_queries": payload["queries"],
        }
        if self.recovery_notice:
            result["system_notice"] = self.recovery_notice
        return result

    # =========================
    # 6. 联网增强回答
    # =========================
    def _format_web_results(self, web_results: list[dict]) -> str:
        if not web_results:
            return ""

        lines = []
        for idx, item in enumerate(web_results[:5], start=1):
            title = str(item.get("title", "")).strip()
            snippet = str(item.get("snippet", "")).strip()
            url = str(item.get("url", "")).strip()
            lines.append(f"【网页资料{idx}】标题：{title}；摘要：{snippet}；链接：{url}")
        return "\n".join(lines)

    def web_enhanced_answer(self, query: str) -> dict[str, Any]:
        rag_payload = self.retrieve_docs_with_meta(query)
        docs = rag_payload["docs"]
        rag_context = self._build_context_from_docs(docs)

        web_results = []
        if self.web_search_fn:
            try:
                web_results = self.web_search_fn(query) or []
            except Exception:
                web_results = []

        if not web_results:
            answer = self._invoke_llm(
                f"{query}\n\n当前没有可用的联网补充结果，请仅基于本地知识库回答。",
                rag_context,
            )
            return {
                "task_type": "web_search_task",
                "answer": answer,
                "citations": rag_payload["citations"],
                "retrieval": rag_payload["retrieval"],
                "confidence": rag_payload["confidence"],
                "rewritten_queries": rag_payload["queries"],
                "web_results": [],
                **({"system_notice": self.recovery_notice} if self.recovery_notice else {}),
            }

        web_context = self._format_web_results(web_results)
        final_context = (
            "以下是本地知识库检索结果：\n"
            f"{rag_context}\n\n"
            "以下是联网补充资料：\n"
            f"{web_context}\n"
        )

        prompt_query = (
            f"{query}\n\n"
            "请优先依据本地知识库回答；如果联网信息能补充案例、趋势或外部事实，可作为辅助说明。"
        )
        answer = self._invoke_llm(prompt_query, final_context)

        return {
            "task_type": "web_search_task",
            "answer": answer,
            "citations": rag_payload["citations"],
            "retrieval": rag_payload["retrieval"],
            "confidence": rag_payload["confidence"],
            "rewritten_queries": rag_payload["queries"],
            "web_results": web_results[:5],
            **({"system_notice": self.recovery_notice} if self.recovery_notice else {}),
        }

    # =========================
    # 7. 设计提案生成
    # =========================
    def design_plan(self, query: str) -> dict[str, Any]:
        payload = self.retrieve_docs_with_meta(query)
        docs = payload["docs"]
        context = self._build_context_from_docs(docs)

        design_query = f"""
用户需求：{query}

你是一名文创 AI 设计助手，请基于参考资料生成创意提案。
本平台常见输出包括：海报、包装、课程内容、展签说明、导览文案等。
请按以下结构输出：
1. 输出类型判断（更适合海报 / 包装 / 课程 / 展签 / 通用策划）
2. 核心主题
3. 文化切入点
4. 纹样 / 视觉元素建议
5. 文案建议
6. 应用场景建议
7. 可延展方向
要求：
- 尽量依据参考资料，不要脱离侗绣相关知识背景
- 如果资料不足，要说明哪些部分是基于合理推断的延展建议
- 输出语言适合方案展示、比赛汇报和面试介绍
"""

        answer = self._invoke_llm(design_query, context)

        result = {
            "task_type": "design_task",
            "answer": answer,
            "citations": payload["citations"],
            "retrieval": payload["retrieval"],
            "confidence": payload["confidence"],
            "rewritten_queries": payload["queries"],
        }
        if self.recovery_notice:
            result["system_notice"] = self.recovery_notice
        return result

    # =========================
    # 8. 通用保守回答
    # =========================
    def general_answer(self, query: str) -> dict[str, Any]:
        payload = self.retrieve_docs_with_meta(query)
        docs = payload["docs"]

        if docs:
            return self.rag_answer(query, task_type="general_qa")

        result = {
            "task_type": "general_qa",
            "answer": "当前知识库中没有找到足够相关的内容，建议补充更具体的问题，或结合联网搜索进一步获取资料。",
            "citations": [],
            "retrieval": [],
            "confidence": "low",
            "rewritten_queries": self.rewrite_query(query),
        }
        if self.recovery_notice:
            result["system_notice"] = self.recovery_notice
        return result

    # =========================
    # 9. 统一工作流入口
    # =========================
    def run_workflow(self, query: str) -> dict[str, Any]:
        task_type = self.classify_task(query)

        if task_type == "design_task":
            return self.design_plan(query)

        if task_type == "web_search_task":
            return self.web_enhanced_answer(query)

        if task_type == "knowledge_qa":
            return self.rag_answer(query)

        return self.general_answer(query)

    # =========================
    # 10. 与原先接口兼容
    # =========================
    def rag_summarize(self, query: str) -> str:
        result = self.rag_answer(query)
        return result["answer"]

    def rag_summarize_with_citations(self, query: str) -> str:
        result = self.run_workflow(query)
        return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    rag_service = RagSummarizeService()

    result = rag_service.run_workflow("请帮我做一个侗绣主题文创包装设计提案")
    print(json.dumps(result, ensure_ascii=False, indent=2))