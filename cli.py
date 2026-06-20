"""
GradeLens CLI
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_score(args):
    """用 LLM 批量评分"""
    from core.dataset import Dataset
    from core.scorers import LLMScorer
    data_dir = args.input or str(Path(__file__).parent / "data" / "essays")
    provider = args.provider or "deepseek"
    out_file = args.output or str(Path(__file__).parent / "data" / "scores.json")
    ds = Dataset(data_dir)
    essays = ds.load_all()
    if not essays:
        print("[score] no essays found")
        return
    scorer = LLMScorer(provider)
    results = []
    for i, essay in enumerate(essays):
        print(f"[{i+1}/{len(essays)}] scoring {essay.id}...", end=" ")
        score = scorer.score_raw(content=essay.content, prompt=essay.prompt, difficulty=essay.difficulty, strategy=essay.strategy)
        results.append({"essay_id": essay.id, "title": essay.title, "strategy": essay.strategy, "difficulty": essay.difficulty, "category": essay.category, **score})
        print(f"overall={score.get('overall', 'N/A')}")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(results)} scores to {out_file}")


def cmd_analyze(args):
    """分析结果"""
    scores_file = args.input or str(Path(__file__).parent / "data" / "scores.json")
    if not os.path.exists(scores_file):
        print(f"[analyze] scores file not found: {scores_file}")
        return
    with open(scores_file, "r", encoding="utf-8") as f:
        scores = json.load(f)
    groups = {}
    for s in scores:
        strat = s["strategy"]
        if strat not in groups:
            groups[strat] = []
        if "error" in s:
            continue
        groups[strat].append(s)
    print("\n" + "=" * 50)
    print("Analysis by Strategy")
    print("=" * 50)
    for strat, items in sorted(groups.items()):
        if not items:
            continue
        overall_scores = [i["overall"] for i in items if "overall" in i]
        print(f"\n[{strat}] n={len(items)}")
        if overall_scores:
            print(f"  Overall: avg={sum(overall_scores)/len(overall_scores):.1f}  min={min(overall_scores)}  max={max(overall_scores)}")
    print("\n" + "=" * 50)
    print("Bias: template vs natural")
    print("=" * 50)
    template_scores = [s["overall"] for s in scores if s["strategy"] == "template" and "overall" in s]
    natural_scores = [s["overall"] for s in scores if s["strategy"] == "natural" and "overall" in s]
    if template_scores and natural_scores:
        t_avg = sum(template_scores) / len(template_scores)
        n_avg = sum(natural_scores) / len(natural_scores)
        print(f"  template avg: {t_avg:.1f} ({len(template_scores)} essays)")
        print(f"  natural avg:  {n_avg:.1f} ({len(natural_scores)} essays)")
        print(f"  bias:         {t_avg - n_avg:+.1f}")


def main():
    parser = argparse.ArgumentParser(description="GradeLens CLI")
    sub = parser.add_subparsers(dest="command")
    score_p = sub.add_parser("score", help="Score essays with LLM")
    score_p.add_argument("--input", "-i", help="Input essays directory")
    score_p.add_argument("--provider", "-p", choices=["deepseek", "qwen", "openai"])
    score_p.add_argument("--output", "-o", help="Output scores JSON")
    ana_p = sub.add_parser("analyze", help="Analyze scores")
    ana_p.add_argument("--input", "-i", help="Input scores JSON")
    bench_p = sub.add_parser("bench", help="Run full benchmark")
    args = parser.parse_args()
    if args.command == "score":
        cmd_score(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "bench":
        from scripts.run_gap_analysis import run_gap_analysis
        run_gap_analysis()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()