"""
rag.rag_service 的 Docstring
用户提问， 检索参考文档， 将提问和参考资料提交给模型进行总结
"""

import json
import os

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain
    
    def retrieve_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)
    
    def rag_summarize(self, query: str) -> str:
        context = ""
        docs = self.retrieve_docs(query)
        for idx, doc in enumerate(docs, start=1):
            context += f"【参考资料{idx}】： {doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke({"input": query, "context": context})

    def rag_summarize_with_citations(self, query: str) -> str:
        docs = self.retrieve_docs(query)

        context = ""
        citations = []
        for idx, doc in enumerate(docs, start=1):
            md = doc.metadata or {}
            source = md.get("source") or md.get("file_path") or md.get("path") or "unknown"
            page = md.get("page")
            snippet = (doc.page_content or "").strip()
            source_name = os.path.basename(str(source)) if source else "unknown"

            compact_meta = {
                "source": source_name,
                "page": page,
                "page_label": md.get("page_label"),
                "total_pages": md.get("total_pages"),
                "author": md.get("author"),
            }

            citations.append(
                {
                    "index": idx,
                    "source": source_name,
                    "page": page,
                    "snippet": snippet[:220],
                    "metadata": compact_meta,
                }
            )
            context += f"【参考资料{idx}】： {snippet} | 参考元数据：{compact_meta}\n"

        answer = self.chain.invoke({"input": query, "context": context})
        payload = {"answer": answer, "citations": citations}
        return json.dumps(payload, ensure_ascii=False)
    

if __name__ == "__main__":
    rag_service = RagSummarizeService()
    result = rag_service.rag_summarize_with_citations("三江侗族织绣纹样有哪些典型构成元素？")
    print(result)