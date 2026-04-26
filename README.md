# 锈见侗韵——面向非遗文化理解与创意生成的AI工作流平台

基于 `Streamlit + LangChain + RAG + Agent` 构建的侗族刺绣垂直领域 AI 辅助设计平台，支持：

- **文化导览问答**：引用式知识问答，支持导览/展签/FAQ/深度研究四模式
- **纹样图谱**：典型纹样卡片与真实绣片扫图浏览
- **设计工作台**：将纹样语义转化为结构化创意提案
- **文创展陈**：展示平面、样机与 AIGC 生成延展成果
- **AI 工作流**：可视化展示 RAG 与 Agent 工作链路
- **场景落地**：展馆、文旅、品牌合作等应用场景

---

## 环境要求

- Python 3.12
- 依赖管理：[uv](https://github.com/astral-sh/uv)
- 操作系统：Windows / Linux / macOS
- 无需 GPU，CPU 本地可运行

---

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置 API Key

**Windows PowerShell：**

```powershell
$env:DASHSCOPE_API_KEY="你的 DashScope API Key"
```

**Linux / macOS：**

```bash
export DASHSCOPE_API_KEY="你的 DashScope API Key"
```

> DashScope API Key 可在 [阿里云百炼平台](https://bailian.console.aliyun.com/) 申请，用于驱动 `qwen3-max` 对话模型与 `text-embedding-v4` 向量模型。

### 3. 构建本地知识库（首次运行必须执行）

```bash
uv run python rag/vector_store.py
```

> 将 `data/dong_embroidery/` 下的侗绣文献解析、切分、向量化并写入 `chroma_db/`，约需 2-3 分钟。

### 4. 启动应用

```bash
uv run streamlit run app.py
```

浏览器访问 `http://localhost:8501`

---

## 目录结构

```text
wxyAgent/
├── app.py                  # Streamlit 主入口，页面路由与请求封装
├── api_server.py           # FastAPI 接口服务（可选）
├── runtime_status.py       # 运行状态可视化组件
├── pyproject.toml          # 依赖配置
├── agent/
│   ├── react_agent.py      # LangChain ReAct Agent 执行器
│   └── tools/
│       ├── agent_tools.py  # 工具集（意图识别/RAG/联网/展品/兜底）
│       └── middleware.py   # 模式切换与日志中间件
├── rag/
│   ├── rag_service.py      # 查询改写→多路召回→重排序→生成全链路
│   └── vector_store.py     # 知识库构建与 Chroma 向量库维护
├── model/
│   └── factory.py          # 模型工厂（qwen3-max + text-embedding-v4）
├── pages/                  # 各功能页面实现
├── prompts/                # 四模式专属提示词模板
├── config/                 # rag.yml / chroma.yml / prompts.yml
├── utils/                  # 配置加载 / 提示词 / 日志 / 路径工具
├── data/
│   ├── dong_embroidery/    # 侗绣知识库原始文献（PDF/DOCX/TXT）
│   └── platform/           # 页面结构化 JSON 数据
├── assets/                 # 纹样图片、扫图、文创成果、工作流展板
└── chroma_db/              # 本地向量数据库（运行 vector_store.py 后生成）
```

---

## 常见问题

### API Key 未配置

如果启动后出现：

```text
Did not find dashscope_api_key
```

重新执行环境变量配置命令后重启应用。

### 知识库加载失败

如果出现向量库相关报错，执行重建：

```bash
uv run python rag/vector_store.py
```

系统会自动清理损坏索引并重建，无需手动操作。

### FastAPI 接口服务

如需启用接口服务（可选）：

```bash
uv run uvicorn api_server:app --port 8000
```
