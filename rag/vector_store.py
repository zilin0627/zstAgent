import os
import re
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

# 兼容：允许 `python rag/vector_store.py` 直接运行
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from model.factory import embed_model
from utils.config_handler import chroma_config
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, load_with_txt_fallback
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

SECTION_PATTERNS = [
    r"^[一二三四五六七八九十]+、.+", r"^（[一二三四五六七八九十]+）.+", r"^\([一二三四五六七八九十]+\).+",
    r"^\d+\.\d+.+", r"^\d+\..+", r"^第[一二三四五六七八九十]+章.+", r"^第[一二三四五六七八九十]+节.+",
]
REGIONS = ["三江", "从江", "黎平", "肇兴", "广西", "贵州"]
KEYWORDS = ["侗绣", "侗族刺绣", "侗族织绣", "纹样", "图案", "构成", "元素", "太阳纹", "龙纹", "凤纹", "鸟纹", "鱼纹", "几何纹", "八菜一汤", "自然崇拜", "图腾", "服饰", "文化", "寓意", "审美", "文创", "包装", "展陈", "视觉设计", "数字化", "转译"]
REFERENCE_MARKERS = ["参考文献", "参考书目", "参考资料", "References"]
TAIL_NOISE_MARKERS = ["作者简介", "作者信息", "基金项目", "收稿日期", "文章编号"]
FAILED_FILES_STORE = "failed_files.txt"


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_config["persist_directory"]),
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separators"],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})

    def is_hnsw_load_error(self, error: Exception) -> bool:
        error_text = str(error).lower()
        return "hnsw" in error_text and "load" in error_text

    def reset_store_files(self) -> None:
        persist_directory = get_abs_path(chroma_config["persist_directory"])
        if os.path.isdir(persist_directory):
            shutil.rmtree(persist_directory)
        os.makedirs(persist_directory, exist_ok=True)

        md5_store = get_abs_path(chroma_config["md5_hex_store"])
        if os.path.exists(md5_store):
            os.remove(md5_store)

    def recover_if_hnsw_broken(self, error: Exception) -> dict[str, str] | None:
        if not self.is_hnsw_load_error(error):
            return None

        logger.warning("[Chroma] 检测到 HNSW 索引损坏，正在自动重建知识库")
        self.reset_store_files()
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_config["persist_directory"]),
        )
        self.load_document()
        return {
            "code": "hnsw_rebuilt",
            "message": "检测到本地向量索引损坏，系统已自动重建知识库，本次回答基于重建后的索引生成。",
        }

    def load_document(self):
        failed_files: list[str] = []

        def check_md5_hex(md5_for_check: str):
            if not md5_for_check:
                return False
            store = get_abs_path(chroma_config["md5_hex_store"])
            if not os.path.exists(store):
                open(store, "w", encoding="utf-8").close()
                return False
            with open(store, "r", encoding="utf-8") as f:
                return any(line.strip() == md5_for_check for line in f.readlines())

        def save_md5_hex(md5_for_save: str):
            if not md5_for_save:
                return
            with open(get_abs_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_save + "\n")

        def write_failed_files():
            failed_path = get_abs_path(FAILED_FILES_STORE)
            if not failed_files:
                if os.path.exists(failed_path):
                    os.remove(failed_path)
                return
            with open(failed_path, "w", encoding="utf-8") as f:
                for item in failed_files:
                    f.write(item + "\n")

        allowed_files_path = listdir_with_allowed_type(
            dir_path=get_abs_path(chroma_config["data_path"]),
            allowed_types=tuple(chroma_config["allow_knowledge_file_type"]),
        )
        processed_txt_fallbacks: set[str] = set()
        for file_path in allowed_files_path:
            if file_path.endswith(".txt") and os.path.splitext(file_path)[0] + ".pdf" in processed_txt_fallbacks:
                logger.info(f"[加载知识库]同名TXT已作为PDF兜底导入，跳过重复TXT: {file_path}")
                continue

            md5_hex = get_file_md5_hex(file_path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]该文件内容已经存在知识库内，跳过: {file_path}")
                continue

            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    docs = self.build_clean_documents(file_path)
                    if not docs:
                        logger.warning(f"[加载知识库]文件 {file_path} 清洗后没有有效内容，跳过")
                        break

                    effective_source = self._resolve_effective_source(file_path)
                    if file_path.endswith(".pdf") and effective_source.endswith(".txt"):
                        processed_txt_fallbacks.add(file_path)

                    self.vector_store.add_documents(docs)
                    save_md5_hex(md5_hex)
                    if effective_source != file_path:
                        fallback_md5 = get_file_md5_hex(effective_source)
                        save_md5_hex(fallback_md5)
                    logger.info(f"[加载知识库]文件 {file_path} 加载完成，共写入 {len(docs)} 个 chunk")
                    break
                except Exception as e:
                    if attempt >= max_attempts:
                        failed_files.append(file_path)
                        logger.error(f"[加载知识库]文件 {file_path} 重试 {max_attempts} 次后仍失败: {str(e)}", exc_info=True)
                    else:
                        wait_seconds = attempt * 3
                        logger.warning(
                            f"[加载知识库]文件 {file_path} 第 {attempt} 次加载失败，将在 {wait_seconds}s 后重试: {str(e)}"
                        )
                        time.sleep(wait_seconds)

        write_failed_files()

    def build_clean_documents(self, file_path: str) -> list[Document]:
        raw_documents = self._get_file_documents(file_path)
        if not raw_documents:
            return []
        file_name = os.path.basename(file_path)
        title, author = self._parse_title_author_from_filename(file_name)
        page_docs = []
        for page_index, raw_doc in enumerate(raw_documents, start=1):
            raw_metadata = dict(raw_doc.metadata or {})
            page = raw_metadata.get("page", page_index)
            text = self._normalize_text(raw_doc.page_content or "")
            if not text:
                continue
            page_docs.append(Document(page_content=text, metadata={
                **raw_metadata,
                "source": file_path,
                "file_name": file_name,
                "title": title,
                "author": author,
                "page": page,
                "section": raw_metadata.get("section") or "原始页内容",
                "page_number": raw_metadata.get("page_number", page),
                "element_type": raw_metadata.get("element_type", "text"),
                "source_parser": raw_metadata.get("source_parser", "unknown"),
                "parser_strategy": raw_metadata.get("parser_strategy", ""),
                "has_ocr": raw_metadata.get("has_ocr", False),
                "has_table": raw_metadata.get("has_table", False),
                "table_html": raw_metadata.get("table_html", ""),
                "has_image": raw_metadata.get("has_image", False),
            }))
        chunk_docs = self.spliter.split_documents(page_docs)
        preserved_docs = []
        for idx, doc in enumerate(chunk_docs, start=1):
            text = self._normalize_text(doc.page_content or "")
            if not text:
                continue
            md = dict(doc.metadata or {})
            region_values = self._extract_regions(text)
            keyword_values = self._extract_keywords(text)
            preserved_docs.append(Document(page_content=text, metadata={
                **md,
                "region": "、".join(region_values) if region_values else "未标注",
                "topic": self._infer_topic(text),
                "knowledge_layer": self._infer_knowledge_layer(text),
                "keywords": "、".join(keyword_values) if keyword_values else "未标注",
                "chunk_id": f"{Path(file_path).stem}-{idx}",
            }))
        return preserved_docs

    def _get_file_documents(self, read_path: str) -> list[Document]:
        docs, _ = load_with_txt_fallback(read_path)
        return docs

    def _resolve_effective_source(self, read_path: str) -> str:
        _, effective_source = load_with_txt_fallback(read_path)
        return effective_source or read_path

    def _parse_title_author_from_filename(self, file_name: str) -> tuple[str, str]:
        name = Path(file_name).stem
        return tuple(part.strip() for part in name.rsplit("_", 1)) if "_" in name else (name.strip(), "")

    def _normalize_text(self, text: str) -> str:
        text = (text or "").replace("\u3000", " ").replace("\xa0", " ").replace("\ufeff", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _detect_repeated_short_lines(self, page_texts: list[str], min_repeat: int = 3) -> set[str]:
        counter = Counter()
        for page in page_texts:
            counter.update({line.strip() for line in page.splitlines() if line.strip() and len(line.strip()) <= 30})
        return {line for line, count in counter.items() if count >= min_repeat}

    def _remove_repeated_short_lines(self, text: str, repeated_lines: set[str]) -> str:
        return "\n".join(line for line in text.splitlines() if line.strip() not in repeated_lines)

    def _remove_page_number_lines(self, text: str) -> str:
        patterns = [r"^-?\s*\d+\s*-?$", r"^第\s*\d+\s*页$", r"^Page\s*\d+$"]
        return "\n".join(line for line in text.splitlines() if not any(re.match(p, line.strip(), re.IGNORECASE) for p in patterns))

    def _remove_toc_lines(self, text: str) -> str:
        return "\n".join(line for line in text.splitlines() if not (re.search(r"[\.．·…]{3,}", line.strip()) and re.search(r"\d+$", line.strip())))

    def _cut_before_markers(self, text: str, markers: list[str]) -> str:
        positions = [text.find(marker) for marker in markers if text.find(marker) != -1]
        return text[:min(positions)].strip() if positions else text

    def _split_into_sections(self, text: str) -> list[tuple[str, str]]:
        sections, current_title, current_lines = [], "正文", []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                if current_lines and current_lines[-1] != "":
                    current_lines.append("")
                continue
            if any(re.match(pattern, line) for pattern in SECTION_PATTERNS):
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines).strip()))
                current_title, current_lines = line[:80], []
                continue
            current_lines.append(line)
        if current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))
        return sections or [("正文", text)]

    def _split_into_paragraphs(self, text: str) -> list[str]:
        return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and not self._looks_like_title_only(p.strip())]

    def _looks_like_title_only(self, text: str) -> bool:
        return len(text) <= 30 and self._sentence_count(text) == 0 and any(re.match(pattern, text) for pattern in SECTION_PATTERNS)

    def _is_high_quality_chunk(self, text: str) -> bool:
        return len(text) >= 50 and not self._is_reference_like(text) and self._chinese_ratio(text) >= 0.3 and self._sentence_count(text) >= 1 and self._noisy_symbol_ratio(text) <= 0.45

    def _is_reference_like(self, text: str) -> bool:
        lower = text.lower()
        return any(marker in text for marker in REFERENCE_MARKERS) or (text.count("[") >= 2 and text.count("]") >= 2) or len(re.findall(r"\d{4}", text)) >= 3 or any(word in lower for word in ["出版社", "学报", "期刊", "vol.", "no."])

    def _chinese_ratio(self, text: str) -> float:
        return len(re.findall(r"[\u4e00-\u9fff]", text)) / max(len(text), 1)

    def _sentence_count(self, text: str) -> int:
        return len([s for s in re.split(r"[。！？!?]", text) if s.strip()])

    def _noisy_symbol_ratio(self, text: str) -> float:
        return len(re.findall(r"[\d\[\]\(\)\-—…·\.]", text)) / max(len(text), 1)

    def _is_duplicate_chunk(self, text: str, seen_texts: list[str], threshold: float = 0.9) -> bool:
        normalized = re.sub(r"\s+", "", text)
        if not normalized:
            return True
        current = set(normalized)
        for seen in seen_texts:
            other = re.sub(r"\s+", "", seen)
            if normalized == other:
                return True
            union = current | set(other)
            if union and len(current & set(other)) / len(union) >= threshold:
                return True
        return False

    def _extract_regions(self, text: str) -> list[str]:
        return [region for region in REGIONS if region in text]

    def _infer_topic(self, text: str) -> str:
        if any(word in text for word in ["寓意", "文化", "象征", "审美", "民俗", "信仰", "崇拜"]):
            return "文化内涵"
        if any(word in text for word in ["设计", "应用", "文创", "包装", "展陈", "视觉", "数字化", "转译"]):
            return "设计应用"
        if any(word in text for word in ["纹样", "图案", "构成", "元素", "服饰"]):
            return "纹样特征"
        return "其他"

    def _infer_knowledge_layer(self, text: str) -> str:
        if any(word in text for word in ["名称", "构成", "元素", "来源", "类型", "图案"]):
            return "基础事实层"
        if any(word in text for word in ["寓意", "象征", "民俗", "审美", "信仰", "崇拜"]):
            return "文化解释层"
        if any(word in text for word in ["文创", "包装", "视觉", "导视", "展陈", "数字化", "转译", "应用"]):
            return "设计应用层"
        return "问答支撑层"

    def _extract_keywords(self, text: str) -> list[str]:
        return [keyword for keyword in KEYWORDS if keyword in text]


if __name__ == "__main__":
    print("加载知识库...")
    vector_store_service = VectorStoreService()
    vector_store_service.load_document()
    retriever = vector_store_service.get_retriever()
    res = retriever.invoke("迷路")
    for item in res:
        print(item.page_content)
        print("-" * 20)
