# Model Card: Game Glitch Investigator

## System Purpose

Game Glitch Investigator is a deterministic applied AI system for diagnosing bug reports from a Streamlit number guessing game. It uses custom retrieval over local project documentation, a rules-based agent workflow, confidence scoring, guardrails, and an evaluation harness.

## Intended Use

The system is intended for educational debugging support. A user describes a game bug, and the investigator returns a likely category, evidence, patch plan, confidence score, and reliability checks.

## Limitations and Biases

The system is biased toward the bugs represented in the original Module 1 project and the custom knowledge base. It may underperform on unrelated Streamlit issues, frontend styling problems, deployment errors, or bugs outside the guessing-game domain. Because it uses lexical retrieval, wording matters: reports that use very different vocabulary may receive lower confidence.

## Misuse Risks and Safeguards

A user could misuse the system by treating a diagnosis as guaranteed and changing code without reproducing the issue. The system reduces this risk by exposing confidence, retrieved sources, intermediate steps, and reliability checks. It also triggers a guardrail for vague reports rather than producing a confident but unsupported answer.

## Reliability Testing

Reliability is tested through unit tests and `evaluate_system.py`. The evaluation harness checks six predefined reports covering state reset, inverted hints, difficulty range, input validation, render order, and vague input. A passing run means the investigator returned the expected category and met the minimum confidence threshold for each case.

Latest local results: `pytest` passed 34 tests, and `python evaluate_system.py` passed 6 out of 6 reliability cases. The most surprising result was that the most responsible behavior for vague input is not a more elaborate answer; it is a guardrail that asks for more context before recommending a fix.

## AI Collaboration Reflection

I used AI as a development partner for debugging, architecture planning, and documentation. A helpful suggestion was to separate the original game logic from the new investigation workflow, which made the project easier to test and explain. A flawed suggestion was to fix Streamlit display lag by moving widgets around; that risked introducing layout-state bugs, so the final design uses stable widget placement and placeholders instead.

## Future Improvements

Future versions could add embeddings, richer retrieval over code comments and test failures, and a human feedback loop that stores reviewed diagnoses. Another improvement would be to compare the investigator's patch plan against actual failing tests before recommending code changes.
