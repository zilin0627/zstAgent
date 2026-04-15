# wxyagent

一个基于 `Streamlit + LangChain + RAG` 的侗族织绣纹样数字体验项目，包含纹样展示、文化导览、RAG 检索问答和设计应用等功能。

当前知识库已升级为**增强型文档解析链路**：

- PDF 优先走 `Unstructured`
- 保留 `PyPDFLoader / pypdf / PyMuPDF` 回退链路
- 支持更丰富的文档结构信息入库，如页码、元素类型、表格标记、OCR 标记等

---

## 你现在最重要的事：按这个顺序做

如果你现阶段目标是“先把知识库搞定，而不只是文本抽取”，建议严格按下面顺序推进：

### 第 1 步：先把环境装好
这是当前最重要的前置条件。

因为你现在已经接入了 `unstructured[pdf]`，如果环境没装好，知识库仍然会自动回退到旧解析器，但你拿不到更好的 PDF 解析效果。

先确认：

```bash
python --version
uv --version
```

项目期望环境：

- Python `3.12`
- `uv`
- Windows 下推荐使用 `PowerShell`

> 本仓库当前 `.python-version` 为 `3.12`。

---

### 第 2 步：安装项目依赖

```bash
uv sync
```

如果你不用 `uv`，也可以：

```bash
pip install -e .
```

这一步会安装新引入的：

- `unstructured[pdf]`
- `pypdf`
- `pymupdf`
- 以及项目已有依赖

---

### 第 3 步：先验证 PDF 解析链路能不能跑通
你现在不要先急着调回答效果，先确认“知识有没有被正确吃进去”。

当前 PDF 解析顺序为：

1. `UnstructuredPDFLoader`
2. `PyPDFLoader`
3. `pypdf`
4. `PyMuPDF`
5. 同名 `txt/docx` 兜底

也就是说：

- 如果 `Unstructured` 能跑通，你就开始获得更强的结构化解析能力
- 如果跑不通，项目不会立刻坏掉，只会退回旧方案

---

### 第 4 步：重建知识库
首次运行或 `data/dong_embroidery/` 中的资料发生变化后，执行：

```bash
uv run python rag/vector_store.py
```

Windows PowerShell 兜底方式：

```powershell
.\.venv\Scripts\python.exe rag\vector_store.py
```

这一步是当前最关键的动作，因为升级是否真正生效，取决于重新导库。

---

### 第 5 步：看日志确认到底走了哪个解析器
重建知识库时，重点观察日志里有没有类似信息：

- `Unstructured加载成功`
- `PyPDFLoader回退读取成功`
- `pypdf回退读取成功`
- `PyMuPDF回退读取成功`
- `PDF读取失败，使用同名TXT兜底`

如果能看到 `Unstructured加载成功`，说明你的新解析链路已经生效。

---

### 第 6 步：再做效果验证
建议你用 2~3 份典型资料验证：

- 正常文字型 PDF
- 扫描版 PDF
- 带图表或复杂排版的 PDF

重点观察：

- 导库后 chunk 数是否增加
- 以前抽不出来的页，现在是否能抽到内容
- 检索结果是否更完整
- 问答时是否能更容易命中图表页、图注页、扫描页文字

---

## 当前项目环境检查结论
基于当前仓库内容，我已经帮你看过项目环境信息，结论如下：

### 已确认

- 系统环境：`Windows 10`
- Shell：`PowerShell`
- 工作区：`e:\github project\wxyAgent`
- 仓库是 Git 项目
- Python 目标版本：`3.12`
- 依赖管理：`uv`

### 项目当前知识库配置

`config/chroma.yml` 当前配置为：

- 知识库目录：`data/dong_embroidery`
- 持久化目录：`chroma_db`
- 支持导入类型：`.txt`、`.pdf`、`.docx`
- `chunk_size = 360`
- `chunk_overlap = 60`

### 当前模型配置

`config/rag.yml` 当前配置为：

- 对话模型：`qwen3-max`
- 向量模型：`text-embedding-v4`

> 这说明你当前项目主要依赖 `DashScope` 侧模型能力，环境变量要优先保证这一套可用。

---

## 环境要求

- Python `3.12+`
- `uv`
- 推荐：Windows PowerShell

检查是否安装成功：

```bash
python --version
uv --version
```

---

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

---

## 安装 uv

### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 获取项目

```bash
git clone <your_repo_url>
cd wxyAgent
```

---

## 配置环境变量

本项目至少建议配置：

- `DASHSCOPE_API_KEY`

如果你项目中还有其他调用链依赖，也可以继续保留：

- `OPENAI_API_KEY`

### Windows PowerShell 临时设置

```powershell
$env:DASHSCOPE_API_KEY="your_dashscope_api_key"
$env:OPENAI_API_KEY="your_openai_api_key"
```

### macOS / Linux

```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"
export OPENAI_API_KEY="your_openai_api_key"
```

---

## 安装依赖

推荐：

```bash
uv sync
```

如果 `uv` 临时不可用，也可以：

```bash
pip install -e .
```

---

## 启动项目

推荐方式：

```bash
uv run streamlit run app.py
```

如果 `uv` 临时联网失败，可用本地环境直接启动。

### Windows

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS / Linux

```bash
python -m streamlit run app.py
```

---

## 构建 / 更新知识库

首次运行或更新 `data/dong_embroidery/` 里的资料后，执行：

```bash
uv run python rag/vector_store.py
```

兜底方式：

### Windows

```powershell
.\.venv\Scripts\python.exe rag\vector_store.py
```

### macOS / Linux

```bash
python rag/vector_store.py
```

---

## 新版知识库解析说明

当前版本不再只是“纯文本抽取”。

### PDF 导入逻辑

当前 PDF 导入顺序为：

1. `UnstructuredPDFLoader`
2. `PyPDFLoader`
3. `pypdf`
4. `PyMuPDF`
5. 同名 `txt` / `docx` 兜底

### 新增能力

新版导库会尽量保留以下信息：

- `page`
- `page_number`
- `element_type`
- `source_parser`
- `parser_strategy`
- `has_ocr`
- `has_table`
- `table_html`
- `has_image`

这意味着后续你可以继续做：

- 更好的表格检索
- 图文页增强召回
- OCR 页识别
- 针对不同元素类型的检索策略优化

---

## Windows 下 `Unstructured` 的注意事项

这是当前最容易卡住的一步。

`unstructured[pdf]` 已经加入项目依赖，但在部分 Windows 环境下，复杂 PDF 解析可能仍会受到本机依赖影响。

如果出现以下现象：

- `Unstructured加载失败`
- 复杂扫描 PDF 仍然抽不到内容
- 导库速度明显变慢

先不要慌，因为当前项目已经保留了回退链路，知识库仍然能工作。

你的判断标准应该是：

1. 能否成功导库
2. 是否有一部分 PDF 已经成功走 `Unstructured`
3. 效果是否比旧版更好

如果只是个别文件失败，先继续推进，不要因为追求一次性完美把整个流程卡住。

---

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

---

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

---

## 部署建议

更适合：

- 云服务器 / VPS
- Docker

不太适合直接无改造部署到 Streamlit Community Cloud，因为项目依赖本地知识库和数据文件。

---

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

### 升级成增强 PDF 解析后，为什么效果还是一般？
常见原因有：

- 没有重新导库
- 实际命中的还是回退解析器，不是 `Unstructured`
- 原 PDF 本身质量太差
- 扫描件图片字迹不清
- chunk 切分策略还没针对表格/图片块做进一步优化

所以当前阶段最重要的不是继续调提示词，而是：

1. 先确认新解析链路生效
2. 先完成一次高质量重建知识库
3. 再决定是否继续做表格块、图注块、图片增强 chunk
