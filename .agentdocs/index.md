# 项目文档索引

## 项目概述
基于强化学习的 Python 豆瓣电影推荐系统，采用 Flask + SQLite 架构，支持本地单机运行。

## 当前任务文档
无进行中的任务

## 已完成任务
`workflow/done/260424-agent-system-upgrade.md` - Agent 系统架构升级（RL 自适应策略 → 工业级 Agent）✅

## 技术架构

### 后端架构
- **框架**：Flask
- **数据库**：SQLite
- **推荐算法**：
  - 混合推荐（内容推荐 + 协同过滤）
  - 语义增强推荐（Word2Vec/GloVe）
  - 强化学习重排（PPO）
- **分层结构**：repository / service / schema

### 前端架构
- **模板引擎**：Jinja2
- **样式**：基于 Bootstrap

## 全局重要记忆
- 项目定位：无服务器部署、本地单机运行
- 语义推荐采用本地轻量级 Word2Vec/GloVe 实现，不依赖重型外部框架
- 所有路径必须使用项目根目录 `/Users/pengkehan/movie_search_agent` 作为基准
