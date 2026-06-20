import json, os, sys
from collections import defaultdict
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def _load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def run_gap_analysis():
    agent_path = os.path.join(project_root, "data", "results", "agent_scores.json")
    if not os.path.exists(agent_path):
        print(f"Agent scores not found: {agent_path}")
        return
    agent_data = _load_json(agent_path)
    agent_map = {e["essay_id"]: e for e in agent_data["essays"]}
    data_dir = Path(project_root) / "data"
    manual_scores = {}
    for fname in sorted(data_dir.glob("manual_scores_batch*.json")):
        try:
            data = _load_json(str(fname))
            for entry in data["essays"]:
                manual_scores[entry["id"]] = entry
        except Exception as e:
            print(f"  Warning: {fname}: {e}")
    if not manual_scores:
        print("No manual scores found.")
        return
    gaps_by_strategy = defaultdict(list)
    gaps_by_category = defaultdict(list)
    gaps_by_difficulty = defaultdict(list)
    total_gap = 0
    count = 0
    for eid, agent in agent_map.items():
        if eid not in manual_scores:
            print(f"  Missing manual: {eid}")
            continue
        manual = manual_scores[eid]
        agent_score = agent.get("overall", 0)
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
    if count == 0:
        print("No matching essays found.")
        return
    avg_gap = total_gap / count
    print("=" * 60)
    print("AES-Bench Gap Analysis Report")
    print("=" * 60)
    print(f"Total essays: {count}")
    print(f"Average gap: {avg_gap:.1f}")
    print("\n--- Gap by Strategy ---")
    for strat in sorted(gaps_by_strategy.keys()):
        gaps = gaps_by_strategy[strat]
        avg = sum(gaps) / len(gaps)
        print(f"  {strat:20s}: Gap={avg:6.1f}, N={len(gaps)}")
    print("\n--- Gap by Category ---")
    for cat in sorted(gaps_by_category.keys()):
        gaps = gaps_by_category[cat]
        avg = sum(gaps) / len(gaps)
        print(f"  {cat:20s}: Gap={avg:6.1f}, N={len(gaps)}")
    print("\n--- Key Findings ---")
    best = max(gaps_by_strategy.items(), key=lambda x: sum(x[1])/len(x[1]))
    worst = min(gaps_by_strategy.items(), key=lambda x: sum(x[1])/len(x[1]))
    print(f"Over-scored: {best[0]} (gap={sum(best[1])/len(best[1]):.1f})")
    print(f"Under-scored: {worst[0]} (gap={sum(worst[1])/len(worst[1]):.1f})")
    if avg_gap > 0:
        print(f"Agent scores HIGHER than manual (+{avg_gap:.1f})")
    elif avg_gap < 0:
        print(f"Agent scores LOWER than manual ({avg_gap:.1f})")
    else:
        print("No overall bias")


if __name__ == "__main__":
    run_gap_analysis()