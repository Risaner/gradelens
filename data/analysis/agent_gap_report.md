# GradeLens Agent Scoring Gap Analysis Report
## Overview
- Total essays analyzed: 48
- Average gap (Agent - Manual): -2.0
- Positive gap means Agent scores higher than Manual

## Gap by Writing Strategy
| Strategy | Avg Gap | Count |
|----------|---------|-------|
| barely_pass | -10.0 | 2 |
| chenglish | -19.5 | 2 |
| chinese_writing | 5.0 | 1 |
| natural | -0.5 | 11 |
| over_optimized | -16.0 | 1 |
| poor | -24.7 | 3 |
| template | 1.9 | 28 |

## Gap by Category
| Category | Avg Gap | Count |
|----------|---------|-------|
| argumentative | -5.7 | 23 |
| chart | 5.3 | 10 |
| mixed | -11.7 | 6 |
| news | 5.9 | 9 |

## Key Findings
1. **Agent OVER-SCORES most on**: chinese_writing (avg gap +5.0)
2. **Agent UNDER-SCORES most on**: poor (avg gap -24.7)
3. **Template strategy gap**: +1.9

## Conclusion
The agent-based scoring system shows lower average scores than manual (avg gap -2.0).
This differs from how AI scoring systems (iWrite, Pigai) behave, challenging our hypothesis.

## Score Comparison
- Agent scores: min=5, max=92, avg=72.0
- Manual scores: min=0, max=88, avg=74.0