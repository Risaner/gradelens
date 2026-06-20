"""Tests for core modules"""
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base import Essay, Scorer
from core.dataset import Dataset
from core.evaluator import Evaluator
from core.scorers import LLMScorer


class TestEssay:
    def test_create_essay(self):
        e = Essay(id="test_001", title="Test", prompt="Write about X",
                  content="Hello world this is a test essay with enough words.",
                  category="argumentative", difficulty="high", strategy="natural", word_count=0)
        assert e.id == "test_001"
        assert e.tags == []
        assert e.word_count > 0

    def test_word_count_auto(self):
        e = Essay(id="t", title="t", prompt="p", content="one two three four five",
                  category="c", difficulty="d", strategy="s", word_count=0)
        assert e.word_count == 5

    def test_tags_default_factory(self):
        e1 = Essay(id="a", title="t", prompt="p", content="c", category="c", difficulty="d", strategy="s", word_count=1)
        e2 = Essay(id="b", title="t", prompt="p", content="c", category="c", difficulty="d", strategy="s", word_count=1)
        e1.tags.append("test")
        assert "test" not in e2.tags


class TestDataset:
    @pytest.mark.skipif(not os.path.exists("data/essays"), reason="Essay data not present")
    def test_load_all(self):
        ds = Dataset("data")
        essays = ds.load_all()
        assert len(essays) == 48, f"Expected 48, got {len(essays)}"

    @pytest.mark.skipif(not os.path.exists("data/essays"), reason="Essay data not present")
    def test_load_by_category(self):
        ds = Dataset("data")
        arg_essays = ds.load_by_category("argumentative")
        assert len(arg_essays) > 0
        for e in arg_essays:
            assert e.category == "argumentative"

    @pytest.mark.skipif(not os.path.exists("data/essays"), reason="Essay data not present")
    def test_load_by_strategy(self):
        ds = Dataset("data")
        natural = ds.load_by_strategy("natural")
        assert len(natural) > 0
        for e in natural:
            assert e.strategy == "natural"

    @pytest.mark.skipif(not os.path.exists("data/essays"), reason="Essay data not present")
    def test_summary(self):
        ds = Dataset("data")
        summary = ds.get_summary()
        assert summary["total"] == 48
        assert "by_category" in summary
        assert "by_strategy" in summary


class TestEvaluator:
    def test_qwk_perfect(self):
        scores = [1.0, 2.0, 3.0, 4.0, 5.0]
        qwk = Evaluator.quadratic_weighted_kappa(scores, scores)
        assert qwk >= 0.99

    def test_pearson_perfect(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        pcc = Evaluator.pearson_correlation(x, x)
        assert abs(pcc - 1.0) < 0.01

    def test_rmse_zero(self):
        x = [1.0, 2.0, 3.0]
        rmse = Evaluator.rmse(x, x)
        assert rmse == 0.0

    def test_pass_fail(self):
        pred = [65.0, 55.0, 70.0, 40.0]
        actual = [62.0, 58.0, 75.0, 35.0]
        acc = Evaluator.pass_fail_accuracy(pred, actual, threshold=60.0)
        assert acc == 1.0

    def test_empty(self):
        assert Evaluator.quadratic_weighted_kappa([], []) == 0.0
        assert Evaluator.pearson_correlation([], []) == 0.0
        assert Evaluator.rmse([], []) == 0.0


class TestScorerInheritance:
    def test_llm_scorer_is_scorer(self):
        assert issubclass(LLMScorer, Scorer)

    def test_scorer_registry(self):
        from core.scorer_registry import SCORER_REGISTRY
        assert "deepseek" in SCORER_REGISTRY
        assert "agent" in SCORER_REGISTRY
        assert "pigai" in SCORER_REGISTRY
        assert "iwrite" in SCORER_REGISTRY


class TestManualScores:
    @pytest.mark.skipif(not os.path.exists("data/manual_scores_batch1.json"), reason="Manual scores not present")
    def test_load_with_bom(self):
        from scorers.data_manager import load_manual_scores
        scores = load_manual_scores("data")
        assert len(scores) == 48


class TestGapAnalysis:
    @pytest.mark.skipif(
        not os.path.exists("data/results/agent_scores.json") or not os.path.exists("data/manual_scores_batch1.json"),
        reason="Score data not present"
    )
    def test_gap_analysis_runs(self):
        from scripts.run_gap_analysis import run_gap_analysis
        run_gap_analysis()