# 侗族织绣纹样 · 非遗数字导览员（RAG）

## 项目介绍

一个基于 Streamlit + LangChain 的“非遗数字导览员”，围绕 **侗族织绣/刺绣纹样**进行检索式讲解。

项目采用 RAG（Retrieval-Augmented Generation）增强检索能力：从你的 PDF/文本资料中检索相关段落，再生成讲解内容，并提供“参考资料与出处”用于溯源展示。

## 项目启动

### 配置系统环境变量

- `OPENAI_API_KEY`
- `DASHSCOPE_API_KEY`: DashScope API 密钥，用于访问模型服务。

### 安装依赖和启动项目

```
uv sync   # 安装依赖
uv run streamlit run app.py  # 启动项目
```

### 构建/更新知识库（首次或新增资料后）

将侗族织绣相关资料放入 `data/dong_embroidery/`（支持 `.txt` / `.pdf`），然后执行：

```
uv run python rag/vector_store.py
```

## 项目结构

```text
zstAgent/
├── app.py                    # Streamlit 入口，负责启动 Web 应用
├── agent/                    # 智能体核心逻辑
│   ├── react_agent.py        # ReAct 智能体构建与流程编排
│   └── tools/                # 智能体可调用工具
├── rag/                      # RAG 检索增强模块
│   ├── rag_service.py        # 检索与回答生成服务
│   └── vector_store.py       # 向量库读写与检索封装
├── model/                    # 模型创建与管理
│   └── factory.py            # LLM/Embedding 模型工厂
├── prompts/                  # 提示词模板
│   ├── main_prompt.txt       # 主对话提示词
│   ├── rag_summarize.txt     # RAG 摘要提示词
│   ├── guide_prompt.txt      # 导览讲解口径
│   ├── label_prompt.txt      # 展签文案口径（100-150字）
│   ├── research_prompt.txt   # 深度研究口径
│   ├── faq_prompt.txt        # FAQ 生成口径
│   └── report_prompt.txt     # 历史文件（当前不再使用）
├── config/                   # 配置文件目录（智能体、RAG、提示词等）
│   ├── agent.yml             # 智能体配置
│   ├── chroma.yml            # 向量库配置
│   ├── prompts.yml           # 提示词配置
│   └── rag.yml               # RAG 参数配置
├── utils/                    # 通用工具函数（配置、日志、文件、路径等）
│   ├── config_handler.py     # 配置读取与解析
│   ├── file_handler.py       # 文件处理工具
│   ├── logger_handler.py     # 日志工具
│   ├── path_tool.py          # 路径处理工具
│   └── prompt_loader.py      # 提示词加载工具
├── data/                     # 知识库与业务数据
└── pyproject.toml            # Python 项目依赖与元信息配置
```

## 系统架构

```mermaid
flowchart LR
    U[用户] --> S[Streamlit 页面 app.py]
    S --> A[ReAct 智能体 agent/react_agent.py]

    A --> T[工具层 agent/tools]
    T --> R[RAG 服务 rag/rag_service.py]
    R --> V[向量检索 rag/vector_store.py]
    V --> C[ChromaDB]
    V --> D[知识库数据 data/dong_embroidery/...]

    A --> M[模型工厂 model/factory.py]
    M --> LLM[大模型服务 DashScope/OpenAI]

    A --> P[prompts/ 提示词]
    A --> CFG[config/ 配置]
    A --> UTL[utils/ 通用能力]

```

## 补充说明

- 配置入口在 `config/`，可按需调整模型、RAG 与提示词参数
- 当前知识库路径由 `config/chroma.yml` 的 `data_path` 指定（默认 `data/dong_embroidery`）
- 核心对话流程：`app.py` → `agent/react_agent.py` → `rag/rag_service.py` → `model/factory.py`
