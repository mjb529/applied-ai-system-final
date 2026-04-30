# Rubric Checklist

## Required Features

- Base project identified: `ai110-module1show-gameglitchinvestigator-starter`, summarized in `README.md`.
- Substantial AI feature: retrieval-augmented investigator with an observable agent workflow in `retrieval.py` and `investigator.py`.
- Architecture diagram: `assets/system_architecture.svg`, embedded in `README.md`.
- End-to-end demo: `app.py` includes the playable game and integrated AI investigator; `investigator_cli.py --demo` provides three sample runs.
- Reliability component: unit tests, confidence scoring, guardrails, audit logging, and `evaluate_system.py`.
- Documentation: `README.md` includes setup, run/test commands, sample inputs and outputs, design decisions, testing summary, reflection, and portfolio artifact.
- Reflection and ethics: `README.md` and `model_card.md` cover limitations, misuse risks, reliability surprise, helpful AI collaboration, and flawed AI collaboration.

## Stretch Features

- RAG enhancement: custom multi-document knowledge base in `knowledge_base/`, split into sections and retrieved before diagnosis.
- Agentic workflow enhancement: output shows validation, retrieval, classification, planning, confidence, and reliability checks.
- Test harness: `evaluate_system.py` evaluates six predefined cases and prints pass/fail results with confidence.

## Latest Verification

```text
pytest: 34 passed
python evaluate_system.py: 6/6 cases passed (100%)
python investigator_cli.py --demo: passed
python -m py_compile app.py logic_utils.py retrieval.py investigator.py investigator_cli.py evaluate_system.py: passed
```

## Submission Blocker

The required Loom walkthrough still needs to be recorded and pasted into `README.md`. The code and documentation include the exact demo path to show: Streamlit app, 2-3 investigator inputs, one guardrail case, and `python evaluate_system.py`.
