"""Reliability harness for the applied AI system."""

from __future__ import annotations

from dataclasses import dataclass

from investigator import GameGlitchInvestigator


@dataclass(frozen=True)
class EvalCase:
    report: str
    expected_category: str
    min_confidence: float


EVAL_CASES = [
    EvalCase(
        report="The secret number changes every time I press submit.",
        expected_category="streamlit_state",
        min_confidence=0.65,
    ),
    EvalCase(
        report="The game tells me to go higher when my guess is already too high.",
        expected_category="hint_logic",
        min_confidence=0.65,
    ),
    EvalCase(
        report="Hard difficulty has the wrong range and feels easier than normal.",
        expected_category="difficulty_range",
        min_confidence=0.65,
    ),
    EvalCase(
        report="If I type letters or a number outside the range, it still spends an attempt.",
        expected_category="input_guardrail",
        min_confidence=0.65,
    ),
    EvalCase(
        report="The score and history display lag behind until the next interaction.",
        expected_category="render_order",
        min_confidence=0.6,
    ),
    EvalCase(
        report="bad",
        expected_category="needs_more_context",
        min_confidence=0.2,
    ),
]


def run_evaluation() -> int:
    investigator = GameGlitchInvestigator()
    passed = 0

    print("Game Glitch Investigator reliability evaluation")
    print("=" * 55)

    for index, case in enumerate(EVAL_CASES, start=1):
        result = investigator.investigate(case.report)
        category_ok = result.category == case.expected_category
        confidence_ok = result.confidence >= case.min_confidence
        ok = category_ok and confidence_ok
        passed += int(ok)
        status = "PASS" if ok else "FAIL"

        print(
            f"{index}. {status} | expected={case.expected_category} "
            f"actual={result.category} confidence={result.confidence:.2f}"
        )

    total = len(EVAL_CASES)
    print("=" * 55)
    print(f"Summary: {passed}/{total} cases passed ({passed / total:.0%}).")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(run_evaluation())
