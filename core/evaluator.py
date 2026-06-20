from typing import List, Dict
class Evaluator:
    """评估指标计算"""

    @staticmethod
    def quadratic_weighted_kappa(predicted: List[float], actual: List[float],
                                  num_stars: int = 5) -> float:
        n = len(predicted)
        if n == 0:
            return 0.0

        def to_stars(scores, min_s, max_s):
            if max_s == min_s:
                return [0] * len(scores)
            return [max(0, min(num_stars - 1, int((s - min_s) / (max_s - min_s) * num_stars)))
                    for s in scores]

        pred_stars = to_stars(predicted, min(predicted), max(predicted))
        actual_stars = to_stars(actual, min(actual), max(actual))

        confusion = [[0] * num_stars for _ in range(num_stars)]
        for p, a in zip(pred_stars, actual_stars):
            confusion[p][a] += 1

        total = sum(sum(row) for row in confusion)
        if total == 0:
            return 0.0

        row_totals = [sum(row) for row in confusion]
        col_totals = [sum(confusion[i][j] for i in range(num_stars)) for j in range(num_stars)]

        expected_weight = 0
        for i in range(num_stars):
            for j in range(num_stars):
                expected_weight += (i - j) ** 2 * row_totals[i] * col_totals[j]

        observed_weight = 0
        for i in range(num_stars):
            for j in range(num_stars):
                observed_weight += (i - j) ** 2 * confusion[i][j]

        if expected_weight == 0:
            return 1.0 if observed_weight == 0 else 0.0

        return round(1 - (1 - observed_weight / total) / (1 - expected_weight / total), 4)

    @staticmethod
    def pearson_correlation(x: List[float], y: List[float]) -> float:
        n = len(x)
        if n == 0:
            return 0.0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        dx = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
        dy = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
        if dx == 0 or dy == 0:
            return 0.0
        return round(num / (dx * dy), 4)

    @staticmethod
    def rmse(predicted: List[float], actual: List[float]) -> float:
        n = len(predicted)
        if n == 0:
            return 0.0
        return round((sum((p - a) ** 2 for p, a in zip(predicted, actual)) / n) ** 0.5, 4)

    @staticmethod
    def pass_fail_accuracy(predicted: List[float], actual: List[float],
                           threshold: float = 60.0) -> float:
        n = len(predicted)
        if n == 0:
            return 0.0
        correct = sum(1 for p, a in zip(predicted, actual)
                      if (p >= threshold) == (a >= threshold))
        return round(correct / n, 4)

    @staticmethod
    def analyze_bias(essays, scores: List[Dict]) -> Dict:
        template_scores = [s["score"] for e, s in zip(essays, scores) if e.strategy == "template"]
        natural_scores = [s["score"] for e, s in zip(essays, scores) if e.strategy == "natural"]
        low_word = [s["score"] for e, s in zip(essays, scores) if e.word_count < 150]
        high_word = [s["score"] for e, s in zip(essays, scores) if e.word_count > 300]

        return {
            "template_avg_score": round(sum(template_scores) / len(template_scores), 2) if template_scores else None,
            "natural_avg_score": round(sum(natural_scores) / len(natural_scores), 2) if natural_scores else None,
            "template_bias": round(
                (sum(template_scores) / len(template_scores) - sum(natural_scores) / len(natural_scores))
                if template_scores and natural_scores else 0, 2),
            "low_word_avg": round(sum(low_word) / len(low_word), 2) if low_word else None,
            "high_word_avg": round(sum(high_word) / len(high_word), 2) if high_word else None,
        }
