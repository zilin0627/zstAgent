from datetime import datetime
import logging
from utils.path_tool import get_abs_path
import os

# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")

# 确保日志存在
os.makedirs(LOG_ROOT, exist_ok=True)

# 设置日志格式 error info debug
# 日志格式， 时间 - 日志名称 - 日志级别 - 文件名:行号 - 日志消息
DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)    

def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file: str | None = None
        ) -> logging.Logger:
    """
    获取日志记录器
    传入日志名称，返回日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    # 添加文件处理器
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(DEFAULT_LOG_FORMAT)
        logger.addHandler(file_handler)

    return logger
   

# 快捷获取日志记录器
logger = get_logger()


if __name__ == "__main__":
    logger.info("这是一条 info 日志")
    logger.debug("这是一条 debug 日志")
    logger.error("这是一条 error 日志")
    logger.warning("这是一条 warning 日志")