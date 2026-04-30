"""Agentic bug investigator for the guessing game project."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from retrieval import KnowledgeRetriever, RetrievedEvidence


LOG_PATH = Path(__file__).parent / "logs" / "investigations.jsonl"


@dataclass(frozen=True)
class InvestigationResult:
    """Structured output from the bug investigation workflow."""

    report: str
    category: str
    diagnosis: str
    patch_plan: list[str]
    confidence: float
    guardrail_triggered: bool
    reliability_checks: list[str]
    retrieved_sources: list[dict[str, object]]
    intermediate_steps: list[str]

    def to_markdown(self) -> str:
        source_lines = [
            f"- {source['title']} ({source['source']}, score {source['score']})"
            for source in self.retrieved_sources
        ]
        plan_lines = [f"- {step}" for step in self.patch_plan]
        check_lines = [f"- {check}" for check in self.reliability_checks]
        step_lines = [f"- {step}" for step in self.intermediate_steps]

        return "\n".join(
            [
                f"### Diagnosis: {self.category}",
                self.diagnosis,
                "",
                f"Confidence: {self.confidence:.2f}",
                "",
                "Patch plan:",
                *plan_lines,
                "",
                "Reliability checks:",
                *check_lines,
                "",
                "Retrieved evidence:",
                *(source_lines or ["- No matching source retrieved."]),
                "",
                "Agent steps:",
                *step_lines,
            ]
        )


class GameGlitchInvestigator:
    """A small observable agent for diagnosing bugs in the game.

    The agent follows a fixed workflow: validate the report, retrieve supporting
    debugging knowledge, classify the failure mode, produce a patch plan, score
    confidence, and write a log entry.
    """

    CATEGORY_RULES = {
        "streamlit_state": {
            "keywords": {
                "reset",
                "rerun",
                "session",
                "state",
                "secret",
                "changes",
                "refresh",
                "click",
                "button",
            },
            "diagnosis": (
                "This looks like a Streamlit state-management bug. The app likely "
                "creates or mutates important game values during each rerun instead "
                "of preserving them in st.session_state."
            ),
            "patch_plan": [
                "Store the secret number, attempts, score, status, and history in st.session_state.",
                "Only initialize state when the key is missing.",
                "Reset related state together when New Game or difficulty changes.",
            ],
        },
        "hint_logic": {
            "keywords": {"hint", "higher", "lower", "too", "high", "low", "wrong", "backwards"},
            "diagnosis": (
                "This looks like comparison or hint logic is inverted. When the guess "
                "is above the secret, the player should be told to go lower; when it "
                "is below the secret, the player should be told to go higher."
            ),
            "patch_plan": [
                "Centralize guess comparison in check_guess.",
                "Add direct tests for too-high and too-low outcomes and messages.",
                "Avoid string comparisons between numeric values.",
            ],
        },
        "scoring": {
            "keywords": {"score", "points", "penalty", "reward", "negative", "high score"},
            "diagnosis": (
                "This looks like a scoring consistency issue. Wrong guesses should "
                "be penalized the same way regardless of direction, while winning "
                "should award points based on attempts used."
            ),
            "patch_plan": [
                "Keep all scoring rules inside update_score.",
                "Test too-high and too-low penalties on odd and even attempts.",
                "Persist high score only when the new score beats the saved score.",
            ],
        },
        "difficulty_range": {
            "keywords": {"difficulty", "easy", "normal", "hard", "range", "between", "200", "20"},
            "diagnosis": (
                "This looks like difficulty metadata is out of sync. The secret "
                "range, attempt limit, visible instructions, and reset behavior all "
                "need to come from the selected difficulty."
            ),
            "patch_plan": [
                "Use get_range_for_difficulty and get_attempt_limit everywhere.",
                "Regenerate the secret when difficulty changes.",
                "Reject guesses outside the active difficulty range.",
            ],
        },
        "input_guardrail": {
            "keywords": {"input", "blank", "empty", "decimal", "number", "letters", "range", "invalid"},
            "diagnosis": (
                "This looks like an input-validation gap. The app should distinguish "
                "between non-numeric input, empty input, and numeric guesses that are "
                "outside the allowed range."
            ),
            "patch_plan": [
                "Parse input with parse_guess before using it.",
                "Do not spend an attempt on invalid or out-of-range input.",
                "Show a clear error message that names the allowed range.",
            ],
        },
        "render_order": {
            "keywords": {"display", "lag", "history", "updates", "after", "rerender", "stale", "expander"},
            "diagnosis": (
                "This looks like a Streamlit render-order issue. A value displayed "
                "before the submit handler runs can appear one interaction behind."
            ),
            "patch_plan": [
                "Use st.empty placeholders for values that update during a submit.",
                "Fill placeholders after state mutation.",
                "Keep widgets in stable positions so expanders and forms do not reset unexpectedly.",
            ],
        },
    }

    def __init__(
        self,
        retriever: KnowledgeRetriever | None = None,
        log_path: Path | str = LOG_PATH,
    ) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.log_path = Path(log_path)

    def investigate(self, report: str) -> InvestigationResult:
        steps = ["Validated incoming report."]
        normalized_report = " ".join(report.strip().split())
        guardrail_triggered, guardrail_message = self._validate(normalized_report)

        if guardrail_triggered:
            result = InvestigationResult(
                report=normalized_report,
                category="needs_more_context",
                diagnosis=guardrail_message,
                patch_plan=[
                    "Describe the visible behavior.",
                    "Include what you expected to happen.",
                    "Add one concrete example input if possible.",
                ],
                confidence=0.2,
                guardrail_triggered=True,
                reliability_checks=[
                    "Input guardrail triggered before diagnosis.",
                    "No code-level recommendation made from insufficient context.",
                ],
                retrieved_sources=[],
                intermediate_steps=steps,
            )
            self._log(result)
            return result

        evidence = self.retriever.retrieve(normalized_report, top_k=3)
        steps.append(f"Retrieved {len(evidence)} knowledge chunk(s).")

        category, keyword_hits = self._classify(normalized_report, evidence)
        steps.append(f"Classified report as {category}.")

        rule = self.CATEGORY_RULES.get(category)
        if rule is None:
            diagnosis = (
                "The report is specific enough to investigate, but it does not match "
                "a known game-glitch pattern with high confidence."
            )
            patch_plan = [
                "Reproduce the bug manually with Developer Debug Info visible.",
                "Add a focused test that captures the observed failure.",
                "Inspect the smallest logic function connected to that behavior.",
            ]
        else:
            diagnosis = str(rule["diagnosis"])
            patch_plan = list(rule["patch_plan"])

        confidence = self._score_confidence(keyword_hits, evidence, category)
        checks = self._reliability_checks(category, confidence, evidence)
        steps.append("Generated diagnosis, patch plan, and reliability checks.")

        result = InvestigationResult(
            report=normalized_report,
            category=category,
            diagnosis=diagnosis,
            patch_plan=patch_plan,
            confidence=confidence,
            guardrail_triggered=False,
            reliability_checks=checks,
            retrieved_sources=[self._serialize_source(item) for item in evidence],
            intermediate_steps=steps,
        )
        self._log(result)
        return result

    @staticmethod
    def _validate(report: str) -> tuple[bool, str]:
        if len(report) < 12:
            return True, "The report is too short to diagnose responsibly."

        if not re.search(r"[a-zA-Z]", report):
            return True, "The report needs words, not only symbols or numbers."

        vague_reports = {"broken", "does not work", "bad", "buggy", "wrong"}
        if report.lower() in vague_reports:
            return True, "The report is too vague to diagnose responsibly."

        return False, ""

    def _classify(
        self,
        report: str,
        evidence: list[RetrievedEvidence],
    ) -> tuple[str, int]:
        terms = set(re.findall(r"[a-z0-9_]+", report.lower()))
        evidence_tags = {tag for item in evidence for tag in item.chunk.tags}
        best_category = "unknown"
        best_score = 0

        for category, rule in self.CATEGORY_RULES.items():
            keywords = set(rule["keywords"])
            keyword_score = len(terms.intersection(keywords))
            evidence_score = 2 if category in evidence_tags else 0
            score = keyword_score + evidence_score
            if score > best_score:
                best_category = category
                best_score = score

        return best_category, best_score

    @staticmethod
    def _score_confidence(
        keyword_hits: int,
        evidence: list[RetrievedEvidence],
        category: str,
    ) -> float:
        if category == "unknown":
            return 0.35

        evidence_bonus = min(sum(item.score for item in evidence) * 0.04, 0.25)
        confidence = 0.45 + min(keyword_hits * 0.08, 0.32) + evidence_bonus
        return round(min(confidence, 0.95), 2)

    @staticmethod
    def _reliability_checks(
        category: str,
        confidence: float,
        evidence: list[RetrievedEvidence],
    ) -> list[str]:
        checks = [
            "Diagnosis is grounded in retrieved project knowledge.",
            "Patch plan targets testable functions or Streamlit state boundaries.",
        ]

        if confidence < 0.6:
            checks.append("Low confidence: ask for a reproduction before changing code.")
        else:
            checks.append("Confidence is high enough to recommend a focused patch.")

        if not evidence:
            checks.append("No evidence retrieved: output should be treated as exploratory.")

        if category in {"hint_logic", "scoring", "difficulty_range", "input_guardrail"}:
            checks.append("Add or run pytest coverage for the affected logic path.")

        return checks

    @staticmethod
    def _serialize_source(item: RetrievedEvidence) -> dict[str, object]:
        return {
            "source": item.chunk.source,
            "title": item.chunk.title,
            "score": item.score,
            "matched_terms": list(item.matched_terms[:8]),
            "excerpt": item.chunk.content[:220],
        }

    def _log(self, result: InvestigationResult) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(result)
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
