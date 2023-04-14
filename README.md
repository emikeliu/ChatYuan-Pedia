---
title: BaiKe ChatYuan
emoji: 😅
colorFrom: green
colorTo: pink
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# ChatYuan-BaiKe - ChatYuan 百度百科资料访问工具

## 简介

0. 修改自 l15y/wenda 。
1. 目前支持模型：`ChatYuan`。
2. 能够自动检索问题中的实体词汇并自动搜索百度百科，并将概要内容添加至 prompt 上下文，以此在模型不具备涌现特性或无对应训练数据的情况下完成关于事实问题的更好回答。

---

## 安装
### 方法1 直接在 Docker 中运行

执行以下命令：
```bash
docker build -t fastapi .
docker run  -it -p 7860:7860 fastapi
```

### 方法2 在本地直接运行

执行以下命令：

```bash
pip install -r requirements.txt
uvicorn NewYuan:app --host 0.0.0.0 --port 7860
```

或

```bash
pip install -r requirements.txt
python NewYuan.py
```

### 方法3 在 Huggingface Space 运行（不推荐）

直接将该项目通过 git 推到相应 Huggingface Space 存储库中即可。

## 百度百科的相关限制

本项目通过 `requests` 访问百度百科，可能出现访问被拒绝。此时请通过 ```--firefox``` 命令（本地具有 Firefox(TM) ）或 ```--crm``` 命令（本地具有 Chromium ）或 ```--edge``` 命令（本地具有 Microsoft Edge(R) ）来通过 selenium 模拟本地浏览器访问百度百科以解除百度百科的访问限制。
