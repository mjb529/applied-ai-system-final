"""Command-line demo for the Game Glitch Investigator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from investigator import GameGlitchInvestigator


DEMO_CASES_PATH = Path(__file__).parent / "demo_cases.json"
DEMO_REPORTS = [
    "When I click submit, the secret number changes and I can never win.",
    "The hint says go higher even when my guess is above the secret number.",
    "Hard mode says it is hard, but the range seems easier than normal.",
]


def load_demo_reports() -> list[str]:
    """Load camera-ready demo cases, with a code fallback for portability."""

    try:
        cases = json.loads(DEMO_CASES_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return DEMO_REPORTS

    reports = [case.get("report", "") for case in cases if case.get("include_in_video", True)]
    return reports or DEMO_REPORTS


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose Game Glitch Investigator bug reports.")
    parser.add_argument("--bug", help="Bug report to investigate.")
    parser.add_argument("--demo", action="store_true", help="Run three sample investigations.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    reports = load_demo_reports() if args.demo else [args.bug]
    if not reports or reports == [None]:
        parser.error("Provide --bug 'description' or use --demo.")

    investigator = GameGlitchInvestigator()

    for index, report in enumerate(reports, start=1):
        result = investigator.investigate(report or "")
        if args.json:
            print(json.dumps(result.__dict__, indent=2))
        else:
            print(f"\n=== Investigation {index} ===")
            print(result.to_markdown())


if __name__ == "__main__":
    main()
