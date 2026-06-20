from typing import List, Dict
class Evaluator:
    """评估指标计算"""

    @staticmethod
    def quadratic_weighted_kappa(predicted: List[float], actual: List[float],
                                  num_ratings: int = 5) -> float:
        """Standard QWK: kappa = 1 - sum(w*O) / sum(w*E)"""
        n = len(predicted)
        if n == 0:
            return 0.0

        # Discretize scores into rating bins
        all_scores = predicted + actual
        min_s, max_s = min(all_scores), max(all_scores)
        if max_s == min_s:
            return 1.0

        def to_bins(scores):
            return [min(num_ratings - 1, max(0, int((s - min_s) / (max_s - min_s) * num_ratings)))
                    for s in scores]

        pred_bins = to_bins(predicted)
        actual_bins = to_bins(actual)

        # Build confusion matrix
        confusion = [[0] * num_ratings for _ in range(num_ratings)]
        for p, a in zip(pred_bins, actual_bins):
            confusion[p][a] += 1

        # Weight matrix: w_ij = (i - j)^2
        weight = [[(i - j) ** 2 for j in range(num_ratings)] for i in range(num_ratings)]

        # Row and column totals
        row_totals = [sum(row) for row in confusion]
        col_totals = [sum(confusion[i][j] for i in range(num_ratings)) for j in range(num_ratings)]

        # Expected matrix: E_ij = row_total_i * col_total_j / n
        expected = [[row_totals[i] * col_totals[j] / n for j in range(num_ratings)]
                    for i in range(num_ratings)]

        # QWK = 1 - sum(w*O) / sum(w*E)
        observed_weight = sum(weight[i][j] * confusion[i][j]
                              for i in range(num_ratings) for j in range(num_ratings))
        expected_weight = sum(weight[i][j] * expected[i][j]
                              for i in range(num_ratings) for j in range(num_ratings))

        if expected_weight == 0:
            return 1.0 if observed_weight == 0 else 0.0

        kappa = 1.0 - observed_weight / expected_weight
        return round(max(-1.0, min(1.0, kappa)), 4)

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
