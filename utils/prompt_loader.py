from utils.path_tool import get_abs_path
from utils.config_handler import prompt_config
from utils.logger_handler import logger

def _read_prompt_from_config(key: str, log_prefix: str) -> str:
    try:
        path = get_abs_path(prompt_config[key])
    except KeyError as e:
        logger.error(f"[{log_prefix}]在yaml配置文件中缺少{key}配置项")
        raise e

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[{log_prefix}]加载提示词时出错: {str(e)}")
        raise e

def load_system_prompt() -> str:
    """
    加载系统提示
    从配置文件中加载系统提示，返回系统提示字符串
    """
    return _read_prompt_from_config("main_prompt_path", "load_system_prompt")
    
def load_rag_prompts() -> str:
    """
    加载RAG摘要提示
    从配置文件中加载RAG摘要提示，返回RAG摘要提示字符串
    """
    return _read_prompt_from_config("rag_summarize_prompt_path", "load_rag_prompt")
    
def load_report_prompt() -> str:
    """
    加载报告提示
    从配置文件中加载报告提示，返回报告提示字符串
    """
    return _read_prompt_from_config("report_prompt_path", "load_report_prompt")

def load_guide_prompt() -> str:
    return _read_prompt_from_config("guide_prompt_path", "load_guide_prompt")

def load_label_prompt() -> str:
    return _read_prompt_from_config("label_prompt_path", "load_label_prompt")

def load_research_prompt() -> str:
    return _read_prompt_from_config("research_prompt_path", "load_research_prompt")

def load_faq_prompt() -> str:
    return _read_prompt_from_config("faq_prompt_path", "load_faq_prompt")
    

if __name__ == "__main__":
    print(load_system_prompt())
    print("="*50)
    print(load_rag_prompts())
    print("="*50)
    print(load_report_prompt())
    print("="*50)
    print(load_guide_prompt())
    print("="*50)
    print(load_label_prompt())
    print("="*50)
    print(load_research_prompt())
    print("="*50)
    print(load_faq_prompt())