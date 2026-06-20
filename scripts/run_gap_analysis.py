import json
from collections import defaultdict

# Load agent scores
agent_data = json.load(open("data/results/agent_scores.json", "r", encoding="utf-8"))
agent_map = {e["essay_id"]: e for e in agent_data["essays"]}

# Load manual scores
manual_scores = {}
for fname in ["data/manual_scores_batch1.json", "data/manual_scores_batch2.json", "data/manual_scores_batch3.json",
              "data/manual_scores_batch4.json", "data/manual_scores_batch5.json", "data/manual_scores_batch6.json",
              "data/manual_scores_batch7.json"]:
    try:
        data = json.load(open(fname, "r", encoding="utf-8"))
        for entry in data["essays"]:
            manual_scores[entry["id"]] = entry
    except:
        pass

# Calculate gaps
gaps_by_strategy = defaultdict(list)
gaps_by_category = defaultdict(list)
gaps_by_difficulty = defaultdict(list)
total_gap = 0
count = 0

for eid, agent in agent_map.items():
    if eid not in manual_scores:
        print(f"  Missing manual score for: {eid}")
        continue
    
    manual = manual_scores[eid]
    agent_score = agent["overall"]
    manual_score = manual.get("score", manual.get("overall", 0))
    gap = agent_score - manual_score
    total_gap += gap
    count += 1
    
    strat = agent.get("strategy", "unknown")
    cat = agent.get("category", "unknown")
    diff = agent.get("difficulty", "unknown")
    
    gaps_by_strategy[strat].append(gap)
    gaps_by_category[cat].append(gap)
    gaps_by_difficulty[diff].append(gap)

avg_gap = total_gap / count if count > 0 else 0

print("=" * 60)
print("AES-Bench Agent Scoring Gap Analysis Report")
print("=" * 60)
print(f"\nTotal essays analyzed: {count}")
print(f"Average gap (Agent - Manual): {avg_gap:.1f}")
print(f"Positive gap = Agent scores higher than Manual")

print(f"\n--- Gap by Writing Strategy ---")
for strat in sorted(gaps_by_strategy.keys()):
    gaps = gaps_by_strategy[strat]
    avg = sum(gaps) / len(gaps)
    print(f"  {strat:20s}: Avg Gap={avg:6.1f}, Count={len(gaps)}")

print(f"\n--- Gap by Category ---")
for cat in sorted(gaps_by_category.keys()):
    gaps = gaps_by_category[cat]
    avg = sum(gaps) / len(gaps)
    print(f"  {cat:20s}: Avg Gap={avg:6.1f}, Count={len(gaps)}")

print(f"\n--- Gap by Difficulty ---")
for diff in sorted(gaps_by_difficulty.keys()):
    gaps = gaps_by_difficulty[diff]
    avg = sum(gaps) / len(gaps)
    print(f"  {diff:20s}: Avg Gap={avg:6.1f}, Count={len(gaps)}")

print(f"\n--- Key Findings ---")
# By strategy
best_strat = max(gaps_by_strategy.items(), key=lambda x: sum(x[1])/len(x[1]))
worst_strat = min(gaps_by_strategy.items(), key=lambda x: sum(x[1])/len(x[1]))
print(f"1. Agent OVER-SCORES most on: {best_strat[0]} (gap={sum(best_strat[1])/len(best_strat[1]):.1f})")
print(f"2. Agent UNDER-SCORES most on: {worst_strat[0]} (gap={sum(worst_strat[1])/len(worst_strat[1]):.1f})")
print(f"3. Template strategy gap: {sum(gaps_by_strategy.get('template', [0]))/max(len(gaps_by_strategy.get('template', [1])), 1):.1f}")

print(f"\n--- Conclusion ---")
if avg_gap > 0:
    print(f"Agent tends to score HIGHER than manual overall (avg gap +{avg_gap:.1f})")
    print("This mirrors AI scoring system behavior (iWrite, Pigai) — validating our hypothesis.")
elif avg_gap < 0:
    print(f"Agent tends to score LOWER than manual overall (avg gap {avg_gap:.1f})")
else:
    print("Agent scores match manual scores closely")

# Save report
report = f"""# AES-Bench Agent Scoring Gap Analysis Report
## Overview
- Total essays analyzed: {count}
- Average gap (Agent - Manual): {avg_gap:.1f}
- Positive gap means Agent scores higher than Manual

## Gap by Writing Strategy
| Strategy | Avg Gap | Count |
|----------|---------|-------|
"""
for strat in sorted(gaps_by_strategy.keys()):
    gaps = gaps_by_strategy[strat]
    avg = sum(gaps) / len(gaps)
    report += f"| {strat} | {avg:.1f} | {len(gaps)} |\n"

report += f"""
## Gap by Category
| Category | Avg Gap | Count |
|----------|---------|-------|
"""
for cat in sorted(gaps_by_category.keys()):
    gaps = gaps_by_category[cat]
    avg = sum(gaps) / len(gaps)
    report += f"| {cat} | {avg:.1f} | {len(gaps)} |\n"

report += f"""
## Key Findings
1. **Over-scored strategy**: {best_strat[0]} (avg gap +{sum(best_strat[1])/len(best_strat[1]):.1f})
2. **Under-scored strategy**: {worst_strat[0]} (avg gap {sum(worst_strat[1])/len(worst_strat[1]):.1f})
3. **Template strategy**: agent {'scores higher' if sum(gaps_by_strategy.get('template', [0]))/max(len(gaps_by_strategy.get('template', [1])), 1) > 0 else 'scores lower'} than manual

## Conclusion
The agent-based scoring system shows {'higher' if avg_gap > 0 else 'lower'} average scores than manual.
It {'mirrors' if avg_gap > 0 else 'differs from'} how AI scoring systems (iWrite, Pigai) behave, {'validating' if avg_gap > 0 else 'challenging'} our hypothesis.
"""

with open("data/analysis/agent_gap_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print(f"\nSaved report to data/analysis/agent_gap_report.md")
