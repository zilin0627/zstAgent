import json
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from rag.vector_store import VectorStoreService
from utils.file_handler import pdf_loader, txt_loader

DEFAULT_FILES = [
    "data/dong_embroidery/广西三江侗族织绣纹样形意解构与创新设计_吴婷婷.pdf",
    "data/dong_embroidery/侗族“八菜一汤”刺绣纹样解析及创新运用研究_刘佳琪.pdf",
    "data/dong_embroidery/肇兴侗寨刺绣纹样的美学特征分析_左小敏.pdf",
]


class IngestCompareScript:
    def __init__(self):
        self.vector_store_service = VectorStoreService()

    def compare_file(self, file_path: str) -> dict[str, Any]:
        abs_path = self._abs_path(file_path)
        raw_docs = self._load_raw_documents(abs_path)
        cleaned_docs = self.vector_store_service.build_clean_documents(abs_path)

        raw_pages = [self._normalize(doc.page_content or "") for doc in raw_docs]
        raw_text = "\n\n".join(page for page in raw_pages if page)
        cleaned_chunks = [self._normalize(doc.page_content or "") for doc in cleaned_docs]
        cleaned_text = "\n\n".join(chunk for chunk in cleaned_chunks if chunk)

        raw_chars = len(raw_text)
        cleaned_chars = len(cleaned_text)
        keep_ratio = round(cleaned_chars / raw_chars, 4) if raw_chars else 0.0

        removed_patterns = self._detect_removed_patterns(raw_pages)
        matched_chunks = self._match_chunks_to_raw_pages(raw_pages, cleaned_docs)
        unmatched_pages = self._find_unmatched_pages(raw_pages, cleaned_docs)

        return {
            "file": file_path,
            "abs_path": abs_path,
            "raw_pages": len(raw_docs),
            "cleaned_chunks": len(cleaned_docs),
            "raw_chars": raw_chars,
            "cleaned_chars": cleaned_chars,
            "keep_ratio": keep_ratio,
            "removed_signals": removed_patterns,
            "page_match_examples": matched_chunks[:8],
            "unmatched_raw_pages": unmatched_pages[:8],
            "raw_preview": raw_text[:500],
            "cleaned_preview": cleaned_text[:500],
        }

    def compare_many(self, file_paths: list[str]) -> dict[str, Any]:
        details = [self.compare_file(path) for path in file_paths]
        return {
            "summary": {
                "files": len(details),
                "avg_keep_ratio": round(
                    sum(item["keep_ratio"] for item in details) / max(len(details), 1), 4
                ),
                "total_raw_chars": sum(item["raw_chars"] for item in details),
                "total_cleaned_chars": sum(item["cleaned_chars"] for item in details),
            },
            "details": details,
        }

    def _load_raw_documents(self, abs_path: str):
        if abs_path.endswith(".pdf"):
            return pdf_loader(abs_path) or []
        if abs_path.endswith(".txt"):
            return txt_loader(abs_path) or []
        return []

    def _detect_removed_patterns(self, raw_pages: list[str]) -> dict[str, Any]:
        joined = "\n".join(raw_pages)
        return {
            "has_reference_marker": any(marker in joined for marker in ["参考文献", "参考书目", "参考资料", "References"]),
            "has_tail_marker": any(marker in joined for marker in ["作者简介", "作者信息", "基金项目", "收稿日期", "文章编号"]),
            "page_number_like_lines": self._count_page_number_lines(raw_pages),
            "toc_like_lines": self._count_toc_lines(raw_pages),
            "repeated_short_lines": self._count_repeated_short_lines(raw_pages),
        }

    def _match_chunks_to_raw_pages(self, raw_pages: list[str], cleaned_docs: list[Any]) -> list[dict[str, Any]]:
        examples = []
        for idx, doc in enumerate(cleaned_docs[:20], start=1):
            chunk = self._normalize(doc.page_content or "")
            if not chunk:
                continue
            best_page = None
            best_score = 0.0
            best_page_text = ""
            for page_idx, raw_text in enumerate(raw_pages, start=1):
                score = self._similarity(chunk[:300], raw_text[:2000])
                if score > best_score:
                    best_score = score
                    best_page = page_idx
                    best_page_text = raw_text
            metadata = doc.metadata or {}
            examples.append(
                {
                    "chunk_index": idx,
                    "metadata_page": metadata.get("page"),
                    "best_raw_page": best_page,
                    "similarity": round(best_score, 4),
                    "chunk_preview": chunk[:160],
                    "raw_page_preview": best_page_text[:160],
                }
            )
        return examples

    def _find_unmatched_pages(self, raw_pages: list[str], cleaned_docs: list[Any]) -> list[dict[str, Any]]:
        cleaned_by_page: dict[int, list[str]] = {}
        for doc in cleaned_docs:
            metadata = doc.metadata or {}
            page = metadata.get("page")
            if isinstance(page, int):
                cleaned_by_page.setdefault(page, []).append(self._normalize(doc.page_content or ""))

        unmatched = []
        for page_idx, raw_text in enumerate(raw_pages, start=1):
            normalized_raw = self._normalize(raw_text)
            if len(normalized_raw) < 80:
                continue
            page_chunks = cleaned_by_page.get(page_idx, [])
            best_score = 0.0
            for chunk in page_chunks:
                score = self._similarity(normalized_raw[:500], chunk[:500])
                if score > best_score:
                    best_score = score
            if best_score < 0.12:
                unmatched.append(
                    {
                        "page": page_idx,
                        "similarity": round(best_score, 4),
                        "raw_preview": normalized_raw[:180],
                    }
                )
        return unmatched

    def _count_page_number_lines(self, raw_pages: list[str]) -> int:
        patterns = [r"^-?\s*\d+\s*-?$", r"^第\s*\d+\s*页$", r"^Page\s*\d+$"]
        count = 0
        for page in raw_pages:
            for line in page.splitlines():
                stripped = line.strip()
                if any(re.match(pattern, stripped, re.IGNORECASE) for pattern in patterns):
                    count += 1
        return count

    def _count_toc_lines(self, raw_pages: list[str]) -> int:
        count = 0
        for page in raw_pages:
            for line in page.splitlines():
                stripped = line.strip()
                if re.search(r"[\.．·…]{3,}", stripped) and re.search(r"\d+$", stripped):
                    count += 1
        return count

    def _count_repeated_short_lines(self, raw_pages: list[str], min_repeat: int = 3) -> int:
        counter: dict[str, int] = {}
        for page in raw_pages:
            for line in page.splitlines():
                stripped = line.strip()
                if stripped and len(stripped) <= 30:
                    counter[stripped] = counter.get(stripped, 0) + 1
        return sum(1 for _, repeat in counter.items() if repeat >= min_repeat)

    def _similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a, b).ratio()

    def _normalize(self, text: str) -> str:
        text = (text or "").replace("\u3000", " ").replace("\xa0", " ").replace("\ufeff", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _abs_path(self, file_path: str) -> str:
        if os.path.isabs(file_path):
            return file_path
        return str((Path(_PROJECT_ROOT) / file_path).resolve())


if __name__ == "__main__":
    script = IngestCompareScript()
    files = sys.argv[1:] or DEFAULT_FILES
    report = script.compare_many(files)
    report_path = os.path.join(_PROJECT_ROOT, "rag", "ingest_compare_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({"report_path": report_path, "summary": report["summary"]}, ensure_ascii=False, indent=2))
