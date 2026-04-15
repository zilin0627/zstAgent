# wxyAgent

一个基于 `Streamlit + LangChain + RAG` 的侗族织绣纹样数字体验项目，包含：

- 纹样图谱
- 文化导览
- 设计工作台
- 文创展陈
- 场景落地

---

## 环境信息

### 本地开发

- OS：`Windows 10`
- Shell：`PowerShell`
- 项目路径：`e:\github project\wxyAgent`
- Python：`3.12`
- 依赖管理：`uv`

### 云端部署

- 服务器：`阿里云 ECS`
- 系统：`Linux`
- 项目目录：`/root/wxyAgent`
- 端口：`8501`
- 启动用户：`root`

---

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

Windows PowerShell：

```powershell
$env:DASHSCOPE_API_KEY="你的 DashScope Key"
```

Linux：

```bash
export DASHSCOPE_API_KEY="你的 DashScope Key"
```

### 3. 本地启动

```bash
uv run streamlit run app.py
```

---

## 常用命令

### 本地运行

```bash
uv run streamlit run app.py
```

### 重建知识库

```bash
uv run python rag/vector_store.py
```

### 提交本地修改

```bash
git add .
git commit -m "your message"
git push origin main
```

---

## 云端启动

登录服务器：

```bash
ssh root@你的ECS公网IP
```

进入项目目录：

```bash
cd /root/wxyAgent
```

启动项目：

```bash
export DASHSCOPE_API_KEY="你的 DashScope Key"
nohup uv run streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &
```

查看日志：

```bash
tail -n 50 streamlit.log
```

停止服务：

```bash
pkill -f "streamlit run app.py"
```

---

## 本地修改后同步到云端

### 本地

```bash
git add .
git commit -m "update"
git push origin main
```

### 云端

```bash
cd /root/wxyAgent
git pull origin main
pkill -f "streamlit run app.py"
nohup uv run streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &
```

如果依赖有变化，再执行：

```bash
uv sync
```

---

## 一条命令更新云端

```bash
cd /root/wxyAgent && git pull origin main && pkill -f "streamlit run app.py" && nohup uv run streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &
```

如果依赖也更新了：

```bash
cd /root/wxyAgent && git pull origin main && uv sync && pkill -f "streamlit run app.py" && nohup uv run streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &
```

---

## 常见问题

### 1. 云端 `git pull` 失败

如果报：

```text
GnuTLS recv error (-110)
```

先执行：

```bash
git config --global http.version HTTP/1.1
git pull origin main
```

### 2. 启动后没反应

先检查：

```bash
tail -n 100 streamlit.log
ps -ef | grep streamlit
ss -lntp | grep 8501
```

### 3. 页面没变化

按顺序检查：

1. 本地是否已经 `git push`
2. 云端是否已经 `git pull`
3. 是否已经重启服务
4. 浏览器是否 `Ctrl + F5`

### 4. 环境变量缺失

如果出现：

```text
Did not find dashscope_api_key
```

重新执行：

```bash
export DASHSCOPE_API_KEY="你的 DashScope Key"
```

---

## 项目结构

```text
wxyAgent/
├── app.py
├── pyproject.toml
├── README.md
├── agent/
├── rag/
├── model/
├── prompts/
├── config/
├── pages/
├── assets/
├── data/
└── utils/
```
