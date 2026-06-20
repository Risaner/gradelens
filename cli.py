"""
AES-Bench CLI工具
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def cmd_generate(args):
    """生成测试作文"""
    from scripts.generate_essays_full import generate_all
    output = args.output or str(Path(__file__).parent.parent / "data" / "essays")
    print(f"[generate] output={output}")
    generate_all(output)


def cmd_score(args):
    """用LLM批量评分"""
    from core.dataset import Dataset
    from core.scorers import LLMScorer

    data_dir = args.input or str(Path(__file__).parent.parent / "data" / "essays")
    provider = args.provider or "deepseek"
    out_file = args.output or str(Path(__file__).parent.parent / "data" / "scores.json")

    ds = Dataset(data_dir)
    essays = ds.load_all()
    if not essays:
        print("[score] 未找到作文，请先运行generate")
        return

    scorer = LLMScorer(provider)
    results = []

    for i, essay in enumerate(essays):
        print(f"[{i+1}/{len(essays)}] scoring {essay.id}...", end=" ")
        score = scorer.score(
            content=essay.content,
            prompt=essay.prompt,
            difficulty=essay.difficulty,
            strategy=essay.strategy,
        )
        results.append({
            "essay_id": essay.id,
            "title": essay.title,
            "strategy": essay.strategy,
            "difficulty": essay.difficulty,
            "category": essay.category,
            **score,
        })
        print(f"overall={score.get('overall', 'N/A')}")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[score] Saved {len(results)} scores to {out_file}")


def cmd_analyze(args):
    """分析结果"""
    from core.evaluator import Evaluator

    scores_file = args.input or str(Path(__file__).parent.parent / "data" / "scores.json")
    if not os.path.exists(scores_file):
        print(f"[analyze] 评分文件不存在: {scores_file}")
        return

    with open(scores_file, "r", encoding="utf-8") as f:
        scores = json.load(f)

    # 按策略分组统计
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
        lang_scores = [i["language"] for i in items if "language" in i]
        cont_scores = [i["content"] for i in items if "content"]
        str_scores = [i["structure"] for i in items if "structure" in i]
        tech_scores = [i["technical"] for i in items if "technical" in i]

        print(f"\n[{strat}] n={len(items)}")
        if overall_scores:
            print(f"  Overall:     avg={sum(overall_scores)/len(overall_scores):.1f}  min={min(overall_scores)}  max={max(overall_scores)}")
        if lang_scores:
            print(f"  Language:    avg={sum(lang_scores)/len(lang_scores):.1f}")
        if cont_scores:
            print(f"  Content:     avg={sum(cont_scores)/len(cont_scores):.1f}")
        if str_scores:
            print(f"  Structure:   avg={sum(str_scores)/len(str_scores):.1f}")
        if tech_scores:
            print(f"  Technical:   avg={sum(tech_scores)/len(tech_scores):.1f}")

    # 偏差分析
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
    parser = argparse.ArgumentParser(description="AES-Bench CLI")
    sub = parser.add_subparsers(dest="command")

    # generate
    gen_p = sub.add_parser("generate", help="Generate test essays")
    gen_p.add_argument("--output", "-o", help="Output directory")

    # score
    score_p = sub.add_parser("score", help="Score essays with LLM")
    score_p.add_argument("--input", "-i", help="Input essays directory")
    score_p.add_argument("--provider", "-p", choices=["deepseek", "qwen", "openai"])
    score_p.add_argument("--output", "-o", help="Output scores JSON")

    # analyze
    ana_p = sub.add_parser("analyze", help="Analyze scores")
    ana_p.add_argument("--input", "-i", help="Input scores JSON")

    args = parser.parse_args()
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
