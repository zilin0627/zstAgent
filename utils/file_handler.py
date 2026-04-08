
import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def get_file_md5_hex(file_path: str) -> str:
    """
    get_file_md5_hex 的 Docstring
    传入文件路径，返回文件的MD5哈希值的十六进制表示
    """
    if not os.path.exists(file_path):
        logger.error(f"[md5计算]文件不存在: {file_path}")
        return None
    
    if not os.path.isfile(file_path):
        logger.error(f"[md5计算]路径不是文件: {file_path}")
        return None
    
    md5_obj = hashlib.md5()
    chunk_size = 4096  # 4KB 读取文件, 避免内存溢出
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):  # 按块读取大文件
                md5_obj.update(chunk)   # 增量更新MD5哈希值
            
            return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"[md5计算]读取文件 {file_path} 时出错: {str(e)}")
        return None
    
    md5_hex = md5_obj.hexdigest()
    return md5_hex

    chunk_size = 4096  # 4KB 读取文件

def listdir_with_allowed_type(dir_path: str, allowed_types: tuple[str]):
    """
    列出目录下所有符合类型要求的文件
    传入目录路径和允许的文件类型元组，返回符合要求的文件列表
    """
    allowed_files = []
    if not os.path.isdir(dir_path):
        logger.error(f"[listdir_with_allowed_type]路径不是目录: {dir_path}")
        return []
    
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(allowed_types):  # 检查文件是否以允许的类型结尾
                allowed_files.append(os.path.join(root, file))
    
    return allowed_files


def pdf_loader(file_path: str, password: str = None) -> list[Document]:
    """
    加载PDF文件
    传入PDF文件路径，返回PDF文件的内容列表
    """
    try:
        return PyPDFLoader(file_path, password=password).load()
    except Exception as e:
        logger.error(f"[pdf_loader]加载PDF文件 {file_path} 时出错: {str(e)}")
        return None


def txt_loader(file_path: str) -> list[Document]:
    """
    加载TXT文件
    传入TXT文件路径，返回TXT文件的内容列表
    """
    try:
        return TextLoader(file_path, encoding="utf-8").load()
    except Exception as e:
        logger.error(f"[txt_loader]加载TXT文件 {file_path} 时出错: {str(e)}")
        return None