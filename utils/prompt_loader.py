from utils.path_tool import get_abs_path
from utils.config_handler import prompt_config
from utils.logger_handler import logger

def load_system_prompt() -> str:
    """
    加载系统提示
    从配置文件中加载系统提示，返回系统提示字符串
    """
    try:
        system_prompt_path = get_abs_path(prompt_config["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompt]再yaml配置文件中缺少main_prompt_path配置项")
        raise e

    
    try:
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[load_system_prompt]加载系统提示时出错: {str(e)}")
        raise e
    
def load_rag_prompts() -> str:
    """
    加载RAG摘要提示
    从配置文件中加载RAG摘要提示，返回RAG摘要提示字符串
    """
    try:
        system_prompt_path = get_abs_path(prompt_config["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompt]再yaml配置文件中缺少rag_summarize_prompt_path配置项")
        raise e

    
    try:
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[load_rag_prompt]加载RAG摘要提示时出错: {str(e)}")
        raise e
    
def load_report_prompt() -> str:
    """
    加载报告提示
    从配置文件中加载报告提示，返回报告提示字符串
    """
    try:
        system_prompt_path = get_abs_path(prompt_config["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompt]再yaml配置文件中缺少report_prompt_path配置项")
        raise e

    
    try:
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[load_report_prompt]加载报告提示时出错: {str(e)}")
        raise e
    

if __name__ == "__main__":
    print(load_system_prompt())
    print("="*50)
    print(load_rag_prompts())
    print("="*50)
    print(load_report_prompt())