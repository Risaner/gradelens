# AES-Bench：AI 作文评分偏差基准测试

**量化 AI 作文评分系统（iWrite / 批改网）与人工评分之间的偏差。**

---

## 项目简介

AES-Bench 是一个基准数据集和分析框架，用于衡量 **AI 作文评分系统（iWrite / 批改网 PIGAI）相对于高质量人工评分的偏差。**

本项目使用 48 篇 AI 生成的 CET-4/6 英语作文，涵盖 7 种写作策略，来回答：

> **AI 评分系统是否会过度偏袒模板作文，而低估低质量作文？**

### 核心发现

| 策略 | Agent vs 人工 偏差 | 含义 |
|------|-------------------|------|
| natural（自然写作） | -0.5 | 基本一致 — 无偏差 |
| template（模板写作） | +1.9 | 基本一致 — 轻微偏好 |
| poor（差文） | -24.7 | Agent 严重低估 |
| barely_pass（勉强通过） | -10.0 | Agent 低估 |
| chenglish（中英混合） | -19.5 | Agent 低估 |

**总体结论：** Agent 评分平均比人工低 2 分，**与"AI 必然偏袒模板"的假设矛盾**。

---

## 数据集

- **48 篇作文**，涵盖 4 种文体、3 个难度等级
- 7 种写作策略：natural、template、poor、barely_pass、chenglish、over_optimized、chinese_writing

| 类别 | 数量 | 难度分布 |
|------|------|---------|
| 议论文 (argumentative) | 23 | 高难度：36 / 中等：5 / 低：7 |
| 图表 (chart) | 10 | |
| 新闻 (news) | 9 | |
| 混合 (mixed) | 6 | |

## 评分标准（CET-4/6）

四个维度各 0-25 分，满分 100：

| 维度 | 权重 | 含义 |
|------|------|------|
| **语言** | 25 | 语法准确性、词汇范围、句式多样性 |
| **内容** | 25 | 切题度、论证深度、例证使用 |
| **结构** | 25 | 段落组织、过渡词、头尾完整 |
| **技术** | 25 | 拼写、标点、格式、字数合规 |

## 快速开始

`ash
# 克隆仓库
git clone https://github.com/Risaner/aes-bench.git
cd aes-bench

# 安装依赖
pip install -r requirements.txt
`

### 查看已完成的 Agent 评分

`python
import json

# 加载已评分数据
with open("data/results/agent_scores.json", encoding="utf-8") as f:
    data = json.load(f)

for essay in data["essays"][:5]:
    print(f"{essay['essay_id']}: {essay['overall']}/100")
`

### 运行 Agent 评分

`ash
# 用 Agent 批量评分
python scripts/agent_batch_runner.py

# 运行偏差分析
python scripts/run_gap_analysis.py
`

### 编程式使用

`python
from core.dataset import Dataset
from core.evaluator import Evaluator

# 加载数据
ds = Dataset("data")
essays = ds.load_all()

# 访问单篇作文
for essay in essays:
    print(f"{essay.id}: {essay.strategy}, {essay.difficulty}, {essay.word_count} 词")

# 评估指标
evaluator = Evaluator()
qwk = evaluator.quadratic_weighted_kappa(...)
pcc = evaluator.pearson_correlation(...)
`

## 项目结构

`
aes-bench/
├── core/                   # 核心模块
│   ├── dataset.py          # Essay 数据类 + 数据加载器
│   ├── scorer_registry.py  # 评分器注册表
│   ├── scorers.py          # LLMScorer 基类
│   ├── scorer_registry.py  # 注册表（agent, iwrite, llm）
│   ├── scorers_iwrite.py   # iWrite 浏览器自动化
│   └── evaluator.py        # QWK、PCC、RMSE 指标
├── scorers/                # 评分器实现
│   ├── agent_scorer.py     # ★ Agent 评分器（hermes chat）
│   ├── llm_scorer.py       # OpenAI 评分器
│   ├── iwrite_scorer.py    # iWrite 浏览器自动化
│   └── pigai_scorer.py     # 批改网 API
├── scripts/
│   ├── agent_batch_runner.py    # Agent 批量评分
│   └── run_gap_analysis.py      # 偏差分析
├── data/
│   ├── essays/              # 48 篇作文（JSON + TXT）
│   ├── results/             # Agent 评分结果
│   ├── analysis/            # 偏差分析报告
│   ├── figures/             # 可视化图表
│   └── manual_scores_*.json # 人工评分基准
├── pyproject.toml           # 项目配置
├── requirements.txt         # 依赖
├── .gitignore
└── README.md
`

## 偏差分析方法

偏差 = Agent 评分 - 人工评分。正值表示 Agent 给分更高。

## 许可证

MIT 许可证。详见 [LICENSE](LICENSE)。
