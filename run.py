"""
端到端流程：生成→评分→分析
一键运行
"""
import sys
from pathlib import Path

# 确保能导入模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.dataset import Dataset
from core.scorers import LLMScorer
from core.evaluator import Evaluator


def run_all(output_dir=None, provider="deepseek"):
    """完整流程：生成→评分→分析"""
    
    # Phase 1: 加载/生成作文
    print("=" * 60)
    print("Phase 1: Loading Essays")
    print("=" * 60)
    
    data_dir = output_dir or str(Path(__file__).parent.parent / "data" / "essays")
    ds = Dataset(data_dir)
    essays = ds.load_all()
    
    if not essays:
        print("No essays found. Generating...")
        print("No essays found.")
        return []
    
    print(f"Loaded {len(essays)} essays")
    print(ds.get_summary())
    
    # Phase 2: 评分
    print("\n" + "=" * 60)
    print("Phase 2: Scoring")
    print("=" * 60)
    
    scorer = LLMScorer(provider)
    results = []
    
    for i, essay in enumerate(essays):
        print(f"[{i+1}/{len(essays)}] {essay.id} ({essay.strategy}/{essay.difficulty})...", end=" ")
        
        score = scorer.score_raw(
            content=essay.content,
            prompt=essay.prompt,
            difficulty=essay.difficulty,
            strategy=essay.strategy,
        )
        
        result = {
            "essay_id": essay.id,
            "title": essay.title,
            "strategy": essay.strategy,
            "difficulty": essay.difficulty,
            "category": essay.category,
            **score,
        }
        results.append(result)
        
        if score.get("error"):
            print(f"ERROR: {score.get('feedback', '')}")
        else:
            print(f"overall={score.get('overall', 'N/A')}")
    
    # 保存结果
    import json
    scores_file = str(Path(__file__).parent.parent / "data" / "scores.json")
    with open(scores_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(results)} scores to {scores_file}")
    
    # Phase 3: 分析
    print("\n" + "=" * 60)
    print("Phase 3: Analysis")
    print("=" * 60)
    
    # 按策略分组
    groups = {}
    for r in results:
        if "error" in r:
            continue
        s = r["strategy"]
        if s not in groups:
            groups[s] = []
        groups[s].append(r)
    
    print("\nScore Summary by Strategy:")
    for s, items in sorted(groups.items()):
        if not items:
            continue
        overall = [i["overall"] for i in items if "overall" in i]
        if overall:
            avg = sum(overall) / len(overall)
            print(f"  {s:20s}: avg={avg:6.1f}  n={len(overall)}")
    
    # 偏差分析
    print("\n" + "=" * 60)
    print("Bias Analysis")
    print("=" * 60)
    
    template_scores = [r["overall"] for r in results if r["strategy"] == "template" and "overall" in r]
    natural_scores = [r["overall"] for r in results if r["strategy"] == "natural" and "overall" in r]
    
    if template_scores and natural_scores:
        t_avg = sum(template_scores) / len(template_scores)
        n_avg = sum(natural_scores) / len(natural_scores)
        bias = t_avg - n_avg
        
        print(f"\nTemplate vs Natural Bias:")
        print(f"  Template avg: {t_avg:.1f} ({len(template_scores)} essays)")
        print(f"  Natural avg:  {n_avg:.1f} ({len(natural_scores)} essays)")
        print(f"  Bias:         {bias:+.1f}")
        
        if bias > 2:
            print("  ⚠ Template essays score HIGHER — possible template bias")
        elif bias < -2:
            print("  ⚠ Natural essays score HIGHER — possible natural bias")
        else:
            print("  ✓ No significant bias detected")
    
    # 难度相关性
    print("\n" + "=" * 60)
    print("Difficulty Correlation")
    print("=" * 60)
    
    for diff in ["low", "medium", "high"]:
        scores = [r["overall"] for r in results if r["difficulty"] == diff and "overall" in r]
        if scores:
            print(f"  {diff:10s}: avg={sum(scores)/len(scores):.1f}  n={len(scores)}")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run GradeLens full pipeline")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--provider", "-p", default="deepseek", choices=["deepseek", "qwen", "openai"])
    args = parser.parse_args()
    
    run_all(args.output, args.provider)
