# 基于 LLM Agent 的智能电影推荐系统

无服务器部署、本地单机运行的端到端智能电影推荐平台，完整覆盖"数据采集-召回-重排-离线评估-模型治理-智能搜索"全链路。融合 **LLM Agent 智能中枢 + 向量语义检索 + PPO强化学习重排** 架构，实现自然语言驱动的智能语义搜索与个性化推荐。

## 技术栈

**核心技术**：PyTorch、Word2Vec/GloVe、PPO强化学习、协同过滤、LLM Agent、向量检索、Scrapy、pandas、Flask、SQLite、Vue.js、MLflow、Chart.js

## 项目特色

### 🤖 LLM Agent 智能搜索中枢

- **自然语言驱动的智能搜索**：将向量检索、电影筛选、数据查询、指标分析等能力封装为标准化工具（Tool），实现自然语言驱动的智能语义搜索
- **口语化跨维度检索**：支持用户通过场景、情节、主题、风格等口语化描述进行跨维度模糊检索（如"一个男人站在大雨里"、"墨西哥亡灵节"），由 LLM 完成意图解析、关键词提取与检索任务拆解
- **Agent 四大核心模块**：
  - **规划器（Planner）**：根据顶层目标自动拆解执行步骤
  - **工具注册表（ToolRegistry）**：标准化工具封装与调用
  - **记忆池（MemoryPool）**：全局状态感知与上下文记忆
  - **行动日志（ActionLog）**：完整的决策日志与执行追踪
- **全流程自动化**：集成爬虫工具（CrawlerTool）、评估工具（EvaluationTool）、训练工具（TrainingTool）、监控工具（MonitorTool），实现数据采集、模型训练、效果评估的全流程自动化

### 🎯 混合召回 + 语义增强 + 强化学习重排

- **基线混合召回**：协同过滤 + 内容推荐，解决冷启动与稀疏性问题
- **语义增强召回**：基于 gensim 实现 Word2Vec/GloVe-style 本地轻量语义嵌入，支持接入 Faiss 向量索引实现高效语义检索，提升召回覆盖度与语义相关性
- **PPO 强化学习重排**：融入 ε-greedy 探索、覆盖率与多样性奖励机制，解决传统推荐精准度低、多样性不足、小样本场景排序不稳定的问题
- **在线学习**：用户反馈写入经验池，批量训练更新模型

### 📊 完整离线评估体系

- **五大核心指标**：precision@k、recall@k、ndcg@k、coverage、diversity
- **实验对比**：支持 ablation 对比实验与留一验证
- **量化迭代**：解决推荐效果难以量化、算法迭代无数据支撑的问题

### 🕷️ 数据采集与工程化

- **多客户端爬虫**：基于 Scrapy 实现豆瓣电影 Top250、评论、用户行为样本的多页爬取
- **反爬虫策略**：集成 UA 池、随机延迟、代理池与断点续爬机制
- **三层架构**：基于 Flask + SQLite 搭建项目主体架构，采用 repositories/services/schemas 三层架构重构代码，解耦数据访问、业务逻辑与接口定义
- **现代化前端**：采用 Vue.js 构建个人影院、Top250 榜单、导演详情等交互页面，统一清爽简约蓝色系 UI 设计风格

### 🎨 界面设计

- **数据可视化主题**：基于健康数据可视化设计规范，采用低饱和度 Sage 绿色主色调
- **信息层级分明**：通过卡片分组、字号对比建立清晰的视觉层次
- **统计数据展示**：用户行为统计、推荐准确率、趋势指示器等数据可视化组件
- **响应式布局**：完美适配移动端、平板和桌面设备

### 🤖 推荐算法

- **混合召回**：内容推荐 + 协同过滤，与语义增强链路隔离对比
- **语义增强**：Word2Vec/GloVe 语义召回，支持 `word2vec_content`、`glove_content`、`word2vec_cf`、`glove_cf`、`semantic_hybrid`
- **RL 重排**：PPO 重排层，加入 ε-greedy 探索、覆盖率奖励、多样性加权
- **在线学习**：用户反馈写入经验池，批量训练更新模型

### 🔍 语义搜索

支持多种查询方式：
- **场景描述**："一个男人站在大雨里"、"冰山撞击沉船"
- **情节描述**："逃出监狱"、"多层梦境植入"、"用石锤挖隧道"
- **主题描述**："希望与自由"、"音乐家族传承"、"亡灵世界冒险"
- **文化元素**："墨西哥亡灵节"、"京剧演员的命运"

测试通过率：**100%**（20个测试用例全部通过）

## 技术架构

### 后端技术栈

- **Web 框架**：Flask 2.3+
- **数据库**：SQLite（支持 Redis 缓存）
- **推荐算法**：scikit-learn、NumPy、Pandas
- **爬虫系统**：requests、BeautifulSoup4、Selenium
- **强化学习**：本地 PPO 实现

### 前端技术栈

- **模板引擎**：Jinja2
- **样式系统**：数据可视化主题 CSS
- **响应式设计**：移动优先，自适应布局

### 项目结构

```text
movie_search_agent/
├── app.py                          # Flask 应用入口
├── config.py                       # 配置管理
├── agent/                          # Agent 系统
│   ├── agent_core.py              # 调度中枢
│   ├── tool_registry.py           # 工具注册中心
│   ├── planner.py                 # 任务规划器
│   ├── memory_pool.py             # 全局状态池
│   ├── action_log.py              # 行为日志
│   ├── event_bus.py               # 事件总线
│   ├── cli.py                     # 命令行工具
│   └── tools/                     # 标准化工具集
│       ├── base_tool.py           # 工具基类
│       ├── crawler_tool.py        # 爬虫工具
│       ├── evaluation_tool.py     # 评估工具
│       ├── training_tool.py       # 训练工具
│       └── monitor_tool.py        # 监控工具
├── myutils/                        # 核心工具模块
│   ├── admin_api.py               # 后台管理 API
│   ├── app_logging.py             # 日志系统
│   ├── evaluation.py              # 离线评估指标
│   ├── behaviorData.py            # 用户行为数据
│   ├── recommend.py               # 推荐引擎入口
│   ├── crawler/                   # 爬虫模块
│   │   ├── core.py               # 爬虫核心功能
│   │   ├── jobs.py               # 爬虫任务管理
│   │   ├── douban_api_client.py  # 豆瓣 API 客户端
│   │   └── browser_client.py     # 浏览器自动化客户端
│   ├── recommender/               # 推荐算法
│   │   ├── content_based.py      # 内容推荐
│   │   ├── collaborative_filtering.py  # 协同过滤
│   │   ├── hybrid_recommender.py # 混合推荐
│   │   └── semantic_embeddings.py # 语义嵌入
│   └── rl/                        # 强化学习
│       ├── cache.py              # 缓存管理
│       ├── features.py           # 特征工程
│       ├── semantic.py           # 语义特征
│       └── local_ppo.py          # PPO 实现
├── repositories/                   # 数据访问层
│   ├── behavior_repository.py
│   ├── experiment_repository.py
│   ├── model_repository.py
│   ├── movie_repository.py
│   └── system_repository.py
├── services/                       # 业务逻辑层
│   ├── behavior_service.py
│   ├── catalog_service.py
│   ├── experiment_service.py
│   ├── model_service.py
│   ├── recommendation_service.py
│   └── system_service.py
├── templates/                      # 前端模板
│   ├── base.html
│   ├── index.html
│   ├── search.html
│   ├── movie.html
│   ├── recommend.html
│   └── admin_*.html
├── static/                         # 静态资源
│   ├── css/
│   │   └── data-viz-theme.css   # 数据可视化主题
│   ├── cover/                    # 电影封面
│   └── js/
└── .agentdocs/                     # 设计文档
    └── design.md                  # 设计系统规范
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

### 3. 访问系统

浏览器访问：http://127.0.0.1:5001

默认管理员账号：
- 邮箱：`alice@example.com`
- 密码：`123456`

## 数据采集

### 爬取电影数据（含封面）

```bash
# 爬取 Top250 电影数据并下载封面
python -m myutils.crawler.jobs movies --pages 8

# 不下载封面
python -m myutils.crawler.jobs movies --pages 8 --no-covers
```

### 补充电影简介

```bash
# 使用豆瓣 API（推荐）
python -m myutils.crawler.jobs summaries --limit-movies 20

# 使用浏览器客户端
python -m myutils.crawler.jobs summaries --limit-movies 20 --use-browser

# 使用 HTTP 客户端
python -m myutils.crawler.jobs summaries --limit-movies 20 --no-api
```

### 爬取评论数据

```bash
python -m myutils.crawler.jobs comments --pages-per-movie 3 --limit-movies 30
```

### 生成行为样本

```bash
python -m myutils.crawler.jobs behaviors --user-count 60 --min-behaviors 8 --max-behaviors 16
```

## 爬虫特性

### 反爬虫策略

- **多重客户端**：HTTP 客户端、豆瓣 API 客户端、Selenium 浏览器客户端
- **智能延迟**：自适应延迟策略，每 3/5 个请求增加额外延迟
- **请求头伪装**：完整的浏览器请求头，Cookie 模拟
- **UA 池**：多个最新版本的 User-Agent 随机切换
- **代理支持**：可配置代理文件

### 数据管理

- **断点续爬**：状态保存在 `runtime/crawler/checkpoints/`
- **去重清洗**：标题、评论、行为样本自动去重
- **状态追踪**：任务状态写入 `runtime/crawler/crawler_status.json`
- **封面下载**：自动下载电影封面到 `static/cover/`

## 推荐系统

### 推荐算法链路

```
baseline 链路：
- baseline_content      # 基础内容推荐
- baseline_cf           # 基础协同过滤
- baseline_hybrid       # 基础混合推荐

semantic 链路：
- word2vec_content      # Word2Vec 内容推荐
- glove_content         # GloVe 内容推荐
- word2vec_cf           # Word2Vec 协同过滤
- glove_cf              # GloVe 协同过滤
- semantic_hybrid       # 语义混合推荐

rerank 链路：
- ppo_rerank            # PPO 强化学习重排
```

### 模型管理

```bash
# 查看模型状态
python -m myutils.rl.local_ppo status

# 初始化模型
python -m myutils.rl.local_ppo bootstrap

# 训练模型
python -m myutils.rl.local_ppo train --force

# 查看模型版本
python -m myutils.rl.local_ppo list

# 回滚到指定版本
python -m myutils.rl.local_ppo rollback <version_tag>
```

### 离线评估指标

- `precision@k` - 准确率
- `recall@k` - 召回率
- `ndcg@k` - 归一化折损累积增益
- `coverage` - 覆盖率
- `diversity` - 多样性

## Agent 系统

### 命令行工具

```bash
# 执行目标
python -m agent.cli execute "提升多样性"
python -m agent.cli execute "补充数据"

# 监控系统健康
python -m agent.cli monitor

# 查看 Agent 状态
python -m agent.cli status

# 列出所有工具
python -m agent.cli tools
```

### Agent 特性

- **统一调度中枢**：AgentCore 统一感知、决策、执行、监控全系统
- **标准化工具**：爬虫、评估、训练、监控等功能封装为标准化 Tool
- **任务自动规划**：根据顶层目标自动拆解执行步骤
- **全局状态感知**：覆盖指标、用户、数据、模型、资源的全局状态池
- **全链路可观测**：完整的决策日志、工具调用日志、执行轨迹记录
- **事件驱动**：支持指标异常报警、自动触发重训等

### 预定义目标

- **提升多样性**：评估 → 调整权重 → 训练 → 验证
- **提升覆盖率**：评估 → 补充数据 → 训练 → 验证
- **提升准确率**：评估 → 补充简介 → 训练 → 验证
- **补充数据**：爬取电影 → 补充简介 → 爬取评论
- **系统健康检查**：监控指标 → 检查模型状态

## 后台管理

登录管理员账号后可访问：

- `/admin/dashboard` - 系统总览、离线指标、RL 状态
- `/admin/models` - 模型版本管理、训练、回滚
- `/admin/crawler` - 爬虫任务配置、状态查看
- `/admin/experiments` - 实验快照、趋势图表
- `/admin/agent` - Agent 系统控制台

### 管理 API

```
GET  /api/v1/admin/overview
GET  /api/v1/admin/evaluation
GET  /api/v1/admin/models
POST /api/v1/admin/models/bootstrap
POST /api/v1/admin/models/train
POST /api/v1/admin/models/<version_tag>/rollback
GET  /api/v1/admin/crawler/status
POST /api/v1/admin/crawler/run
GET  /api/v1/admin/experiments
POST /api/v1/admin/experiments/run
GET  /api/v1/admin/agent/status
GET  /api/v1/admin/agent/health
POST /api/v1/admin/agent/execute
GET  /api/v1/admin/agent/tools
GET  /api/v1/admin/agent/decisions
GET  /api/v1/admin/agent/stats
```

## 配置项

### 环境变量

```bash
# 应用配置
export SECRET_KEY=dev-secret
export MOVIE_ADMIN_EMAILS=alice@example.com

# 强化学习配置
export MOVIE_RL_ENABLED=1
export MOVIE_RL_BATCH_SIZE=100
export MOVIE_RL_MIN_FEEDBACK=5
export MOVIE_PPO_EPOCHS=6
export MOVIE_PPO_LR=0.03
export MOVIE_PPO_CLIP=0.2
export MOVIE_RL_EPSILON=0.1
export MOVIE_RL_DIVERSITY_WEIGHT=0.18
export MOVIE_RL_COVERAGE_WEIGHT=0.12
export MOVIE_KEEP_MODEL_VERSIONS=6

# 缓存配置
export MOVIE_REDIS_URL=redis://127.0.0.1:6379/0

# 爬虫配置
export DOUBAN_MIN_DELAY=5.0
export DOUBAN_MAX_DELAY=10.0
export DOUBAN_TIMEOUT=30
export DOUBAN_RETRIES=6
export DOUBAN_PROXY_FILE=./runtime/crawler/proxies.txt

# LLM 配置（可选）
export MOVIE_LLM_BASE_URL=
export MOVIE_LLM_API_KEY=
export MOVIE_LLM_MODEL=gpt-4o-mini
```

## 技术亮点

### 1. 智能语义搜索

- **多层次匹配**：标题精确匹配、简介关键词匹配、Token 级别匹配、字符级重叠度
- **权重优化**：标题权重 10.0、简介权重 5.0、Token 权重 3.0、字符重叠权重 1.5
- **测试验证**：20 个测试用例 100% 通过率

### 2. 强化学习重排

- **PPO 算法**：本地 PPO 实现，支持在线学习和批量更新
- **探索策略**：ε-greedy 探索，平衡探索与利用
- **多目标优化**：覆盖率奖励、多样性加权
- **模型治理**：版本管理、自动清理、快速回滚

### 3. 数据采集系统

- **多客户端支持**：HTTP、API、浏览器自动化三种客户端
- **智能反爬**：自适应延迟、请求头伪装、Cookie 模拟
- **封面下载**：自动下载并保存电影封面到本地
- **断点续爬**：支持任务中断后继续执行

### 4. 工程架构

- **分层架构**：Repository/Service/Schema 三层分离
- **缓存优化**：内存缓存 + Redis 缓存双层支持
- **日志系统**：结构化日志，便于问题追踪
- **配置管理**：环境变量配置，灵活可调

## 设计系统

项目采用专业的数据可视化设计系统，详见 `.agentdocs/design.md`。

### 设计原则

- 数据可视化优先
- 信息层级分明
- 柔和专业的色彩
- 留白充足

### 页面色彩

- 数据可视化色板：粉色、珊瑚色、桃色、薄荷色
- 状态色：绿色（正常）、黄色（警告）、红色（错误）

## 依赖项

```
Flask>=2.3
beautifulsoup4>=4.12
numpy>=1.26
pandas>=2.0
redis>=5.0
requests>=2.31
scikit-learn>=1.3
selenium>=4.15
webdriver-manager>=4.0
```

## 开发路线

### 已完成

- ✅ 混合推荐算法（内容 + 协同过滤）
- ✅ 语义增强推荐（Word2Vec/GloVe）
- ✅ 智能语义搜索（场景、情节、主题查询）
- ✅ PPO 强化学习重排
- ✅ 工业级 Agent 系统（调度中枢、工具封装、任务规划、可观测）
- ✅ 数据可视化界面
- ✅ 爬虫系统（含封面下载）
- ✅ 后台管理系统
- ✅ 离线评估指标
- ✅ 模型版本管理

### 可扩展方向

- 升级推荐算法：ALS、Wide&Deep、DIN
- A/B 实验系统
- 更强的特征工程
- 监控和任务追踪
- 使用 SQLAlchemy 重构数据层

## 许可证

MIT License

## 致谢

- 数据来源：豆瓣电影
