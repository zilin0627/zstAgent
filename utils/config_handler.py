import yaml
from utils.path_tool import get_abs_path

def load_config(config_path: str, encoding: str = "utf-8"):
    """
    加载配置文件
    传入配置文件路径，返回配置字典
    """
    with open(get_abs_path(config_path), "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

rag_config = load_config("config/rag.yml")
chroma_config = load_config("config/chroma.yml")
prompt_config = load_config("config/prompts.yml")
agent_config = load_config("config/agent.yml")

if __name__ == "__main__":
    print(rag_config)
    print(chroma_config)
    print(prompt_config)
    print(agent_config)