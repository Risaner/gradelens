"""
Agent Batch Runner
批量调用 AgentScorer 对作文评分
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.dataset import Dataset
from scorers.agent_scorer import AgentScorer


def run():
    scorer = AgentScorer(timeout=120)
    ds = Dataset("data")
    essays = ds.load_all()
    
    output_path = "data/results/agent_scores.json"
    if os.path.exists(output_path):
        existing = json.load(open(output_path, "r", encoding="utf-8"))
        already_done = {e["essay_id"] for e in existing.get("essays", [])}
    else:
        existing = {"essays": []}
        already_done = set()
    
    # Essay is a dataclass - use .id and .essay dict
    to_score = []
    for e in essays:
        eid = e.id if hasattr(e, "id") else e["id"]
        if eid not in already_done:
            # Build full essay dict with metadata
            meta = {k: getattr(e, k) if hasattr(e, k) else e[k] for k in ["id", "prompt", "category", "difficulty", "strategy", "word_count", "content", "title"]}
            to_score.append(meta)
    
    print(f"Scored: {len(already_done)}, Remaining: {len(to_score)}")
    
    if not to_score:
        print("All essays already scored. Nothing to do.")
        return
    
    for i, essay in enumerate(to_score):
        print(f"[{i+1}/{len(to_score)}] Scoring: {essay['id']} ({essay['strategy']})")
        score = scorer.score(essay)
        if score:
            existing["essays"].append(score)
            print(f"  Score: {score.get('overall', '?')}")
        else:
            print(f"  FAILED - no valid score returned")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    
    from collections import Counter
    scores = [e.get("overall", 0) for e in existing["essays"] if e.get("overall") is not None]
    if not scores:
        print("\nDone! No valid scores.")
        return
    strats = Counter(e.get("strategy", "unknown") for e in existing["essays"])
    print(f"\nDone! Total: {len(existing['essays'])}")
    print(f"Score range: {min(scores)}-{max(scores)}, avg: {sum(scores)/len(scores):.1f}")
    print(f"By strategy: {dict(strats)}")


if __name__ == "__main__":
    run()
