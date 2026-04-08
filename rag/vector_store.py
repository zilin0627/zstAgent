import os
import sys

# 兼容：允许 `python rag/vector_store.py` 直接运行
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from langchain_chroma import Chroma
from utils.config_handler import chroma_config
from utils.path_tool import get_abs_path
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
from langchain_core.documents import Document


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
        """
        get_retriever 的 Docstring
        从向量数据库中获取一个检索器，用于根据查询向量进行相似度检索。
        :param self: self 实例
        :return: 一个检索器
        """
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})
    
    def load_document(self):
        """
        load_document 的 Docstring
        从数据文件中加载文档，将文档内容转换为向量，存储到向量数据库中。
        :param self: self 实例
        :return: None
        """
        
        def check_md5_hex(md5_for_check: str):
            # 检查md5文件是否存在
            if not os.path.exists(get_abs_path(chroma_config["md5_hex_store"])):
                open(get_abs_path(chroma_config["md5_hex_store"]), "w").close()
                return False   # md5未处理 文件不存在, 则返回False
            
            with open(get_abs_path(chroma_config["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.strip() == md5_for_check:
                        return True   # 该md5已处理过, 则返回True
            return False   # 该md5未处理过, 则返回False
        
        def save_md5_hex(md5_for_save: str):
            # 将md5写入文件, 每行一个md5
            with open(get_abs_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_save + "\n")   
        
        def get_file_documents(read_path: str):
            # 从文件中加载文档
            if read_path.endswith(".pdf"):
                documents = pdf_loader(read_path)
            elif read_path.endswith(".txt"):
                documents = txt_loader(read_path)
            else:
                 return []
            return documents
        
        # 从数据文件中加载文档
        allowed_files_path = listdir_with_allowed_type(
            dir_path=get_abs_path(chroma_config["data_path"]),
            allowed_types=tuple(chroma_config["allow_knowledge_file_type"])
        )
        for file_path in allowed_files_path:
            # 获取文件的md5值
            md5_hex = get_file_md5_hex(file_path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]该文件内容已经存在知识库内， 跳过: {file_path}")
                continue
            
            try:
                documents: list[Document] = get_file_documents(file_path)

                if not documents:
                    logger.warning(f"[加载知识库]文件 {file_path} 没有有效内容， 跳过")
                    continue

                split_documents = self.spliter.split_documents(documents)
                if not split_documents:
                    logger.warning(f"[加载知识库]文件 {file_path} 分片后没有有效内容， 跳过")
                    continue
                # 将文档内容转换为向量，存储到向量数据库中
                self.vector_store.add_documents(split_documents)
                # 记录该文件的md5值
                save_md5_hex(md5_hex)
                logger.info(f"[加载知识库]文件 {file_path} 加载完成")
            except Exception as e:
                # exc_info=True 会将异常信息(堆栈信息)打印到日志
                logger.error(f"[加载知识库]文件 {file_path} 加载时出错: {str(e)}", exc_info=True)
                continue

if __name__ == "__main__":
    print("加载知识库...")
    vector_store_service = VectorStoreService()
    vector_store_service.load_document()

    retriever = vector_store_service.get_retriever()

    res = retriever.invoke("迷路")
    for item in res:
        print(item.page_content)
        print("-"*20)
    