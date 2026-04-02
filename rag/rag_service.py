"""
rag.rag_service 的 Docstring
用户提问， 检索参考文档， 将提问和参考资料提交给模型进行总结
"""

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


def print_prompt(prompt: str):
    """
    打印提示模板
    """
    print("="*50)
    print(prompt.to_string())
    print("="*50)
    return prompt

class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain
    
    def retrieve_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)
    
    def rag_summarize(self, query: str) -> str:
        context = ""
        docs = self.retrieve_docs(query)
        for idx, doc in enumerate(docs, start=1):
            context += f"【参考资料{idx}】： {doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke({"input": query, "context": context})
    

if __name__ == "__main__":
    rag_service = RagSummarizeService()
    result = rag_service.rag_summarize("小户型适合哪些扫地机器人")
    print(result)