"""
utils.path_tool 的 Docstring
为项目提供统一的路径工具
"""

import os

def get_project_root():
    """
    获取项目根目录
    """
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def get_abs_path(relative_path: str) -> str:
    """
    获取绝对路径
    传入相对路径，返回绝对路径
    """
    return os.path.join(get_project_root(), relative_path)


if __name__ == "__main__":
    print(get_project_root())
    print(get_abs_path("config/config.json"))