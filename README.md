# wxyagent

一个基于 `Streamlit + LangChain + RAG` 的侗族织绣纹样数字体验项目，包含纹样展示、文化导览、RAG 检索问答和设计应用等功能。

## 环境要求

- Python 3.12+
- uv

检查是否安装成功：

```bash
python --version
uv --version
```

## 安装 Python

### Windows
到官网下载安装 Python 3.12：<https://www.python.org/downloads/>

安装时记得勾选：

```text
Add python.exe to PATH
```

### macOS

```bash
brew install python@3.12
```

### Linux

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv -y
```

## 安装 uv

### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 获取项目

```bash
git clone <your_repo_url>
cd wxyAgent
```

## 配置环境变量

需要配置：

- `OPENAI_API_KEY`
- `DASHSCOPE_API_KEY`

Windows PowerShell 临时设置：

```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
$env:DASHSCOPE_API_KEY="your_dashscope_api_key"
```

macOS / Linux：

```bash
export OPENAI_API_KEY="your_openai_api_key"
export DASHSCOPE_API_KEY="your_dashscope_api_key"
```

## 安装依赖

```bash
uv sync
```

## 启动项目

推荐方式：

```bash
uv run streamlit run app.py
```

如果 `uv` 临时联网失败，可用本地环境直接启动：

### Windows

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS / Linux

```bash
python -m streamlit run app.py
```

## 构建 / 更新知识库

首次运行或更新 `data/dong_embroidery/` 里的资料后，执行：

```bash
uv run python rag/vector_store.py
```

兜底方式：

### Windows

```powershell
.\.venv\Scripts\python.exe rag/vector_store.py
```

### macOS / Linux

```bash
python rag/vector_store.py
```

## 项目结构

```text
wxyAgent/
├── app.py
├── pyproject.toml
├── uv.lock
├── README.md
├── agent/
├── rag/
├── model/
├── prompts/
├── config/
├── modules/
├── pages/
├── assets/
├── data/
├── chroma_db/
└── utils/
```

## 给别人运行

别人本地运行时，按这个顺序即可：

```bash
git clone <your_repo_url>
cd wxyAgent
uv sync
uv run streamlit run app.py
```

如果知识库需要重建：

```bash
uv run python rag/vector_store.py
```

## 部署建议

更适合：

- 云服务器 / VPS
- Docker

不太适合直接无改造部署到 Streamlit Community Cloud，因为项目依赖本地知识库和数据文件。

## 常见问题

### 为什么 `uv run` 有时失败？
通常是 `uv` 在运行前检查依赖时联网超时，不一定是代码有问题。这时可先用：

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### `chroma_db/chroma.sqlite3` 要不要提交？
- 想共享现成知识库：可以提交
- 想让别人自己生成：不提交，并让对方执行

```bash
uv run python rag/vector_store.py
```
