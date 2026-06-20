# AES-Bench：AI 作文评分偏差基准测试框架

**开源框架，用于量化 AI 作文评分系统与参考评分之间的偏差。**

---

## 项目简介

AES-Bench 是一个**可复用的基准测试框架**，用于衡量 AI 作文评分系统（iWrite / 批改网 PIGAI 等）的评分偏差。

核心价值：**国内首个开源的 AES（自动作文评分）系统评测框架。** 所有 AES 研究都是「如何写好评分模型」，没有人做「如何评测评分模型」的工具。

### 框架能做什么

- 📊 **批量测试**：用统一数据集测试任意 AI 评分系统
- 📐 **多维指标**：QWK、PCC、RMSE、及格准确率等学术标准指标
- 🔍 **偏差分析**：按写作策略、文体、难度分组分析评分偏差
- 🔌 **可扩展**：只需实现 Scorer 接口即可接入新评分系统
- 📈 **可视化**：自动生成偏差分析图表和报告

### 数据集说明

> ⚠️ **重要声明**：本项目附带的 48 篇测试作文由 AI 生成，配套的参考评分（data/manual_scores_batch*.json）同样由 AI 模拟生成，**仅供框架演示和参考，不代表真实人工评分**。
>
> 如需严肃的学术评测，请替换为真实人工评分数据（如 CET 阅卷教师评分）。
> 框架本身与数据来源无关——换上你自己的数据集即可使用。

当前数据集覆盖 7 种写作策略：

| 策略 | 含义 | AI vs 参考评分偏差 |
|------|------|-------------------|
| natural | 自然写作 | -0.5（基本一致） |
| template | 模板写作 | +1.9（轻微偏好） |
| poor | 差文 | -24.7（严重低估） |
| barely_pass | 勉强通过 | -10.0（低估） |
| chenglish | 中英混合 | -19.5（低估） |

---

## 快速开始

`ash
# 克隆仓库
git clone https://github.com/Risaner/aes-bench.git
cd aes-bench

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/ -v

# 运行偏差分析（使用附带的示例数据）
python cli.py bench

# 用 LLM 评分器对作文评分
python cli.py score --provider deepseek

# 分析已有评分结果
python cli.py analyze
`

### 编程式使用

`python
from core.dataset import Dataset
from core.evaluator import Evaluator
from core.scorers import LLMScorer
from core.base import Scorer

# 加载数据集
ds = Dataset('data')
essays = ds.load_all()
print(ds.get_summary())

# 用 LLM 评分
scorer = LLMScorer('deepseek')
for essay in essays:
    result = scorer.score(essay)
    print(f'{essay.id}: {result["overall"]}/100')

# 评估指标
evaluator = Evaluator()
qwk = evaluator.quadratic_weighted_kappa(predicted, actual)
pcc = evaluator.pearson_correlation(predicted, actual)
rmse = evaluator.rmse(predicted, actual)
`

### 接入你自己的评分系统

只需继承 Scorer 基类：

`python
from core.base import Scorer, Essay
from typing import Dict

class MyScorer(Scorer):
    def __init__(self):
        super().__init__('MySystem')

    def score(self, essay: Essay) -> Dict:
        # 调用你的评分 API
        your_score = call_your_api(essay.content)
        return {
            'language': your_score.lang,
            'content': your_score.cont,
            'structure': your_score.struc,
            'technical': your_score.tech,
            'overall': your_score.total,
            'feedback': your_score.comment,
        }
`

注册后即可通过 CLI 使用：

`python
from core.scorer_registry import SCORER_REGISTRY
SCORER_REGISTRY['my_system'] = lambda: MyScorer()
`

---

## 评分标准（CET-4/6）

四个维度各 0-25 分，满分 100：

| 维度 | 权重 | 含义 |
|------|------|------|
| **语言** | 25 | 语法准确性、词汇范围、句式多样性 |
| **内容** | 25 | 切题度、论证深度、例证使用 |
| **结构** | 25 | 段落组织、过渡词、头尾完整 |
| **技术** | 25 | 拼写、标点、格式、字数合规 |

---

## 项目结构

`
aes-bench/
├── core/                      # 核心模块
│   ├── base.py                # Essay 数据类 + Scorer 抽象基类
│   ├── dataset.py             # 数据集加载器
│   ├── scorers.py             # LLM 评分器（DeepSeek/Qwen/OpenAI）
│   ├── scorer_registry.py     # 评分器注册表
│   └── evaluator.py           # QWK、PCC、RMSE 指标计算
├── scorers/                   # 评分器实现
│   ├── agent_scorer.py        # Agent 评分器（hermes chat）
│   ├── llm_scorer.py          # LLM 评分器
│   ├── iwrite_scorer.py       # iWrite 浏览器自动化
│   ├── pigai_scorer.py        # 批改网 API
│   └── data_manager.py        # 数据加载/保存工具
├── scripts/
│   ├── agent_batch_runner.py  # Agent 批量评分
│   └── run_gap_analysis.py    # 偏差分析
├── tests/
│   └── test_core.py           # 测试用例
├── data/
│   ├── essays/                # 测试作文（JSON + TXT）
│   ├── results/               # 评分结果
│   ├── analysis/              # 偏差分析报告
│   └── manual_scores_*.json   # 参考评分（AI 生成）
├── cli.py                     # 命令行工具
├── config.yaml                # 配置文件
└── pyproject.toml             # 项目配置
`

---

## 已内置的评分器

| 评分器 | 类型 | 说明 |
|--------|------|------|
| deepseek | LLM API | DeepSeek Chat |
| qwen | LLM API | 通义千问 |
| openai | LLM API | GPT-4o-mini |
| gent | CLI 调用 | Hermes Agent 评分 |
| pigai | API | 批改网快速体验接口 |
| iwrite | 浏览器自动化 | iWrite 平台（需登录） |

---

## 许可证

MIT 许可证。详见 [LICENSE](LICENSE)。