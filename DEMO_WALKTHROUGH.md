# Loom Walkthrough Script

Target length: 5-7 minutes.

## Before Recording

Open two terminal tabs in the project folder:

```bash
cd /Users/matthewbark/CodePath/applied-ai-system-final
```

Start the app:

```bash
python -m streamlit run app.py
```

Keep these commands ready for the reliability section:

```bash
python investigator_cli.py --demo
python evaluate_system.py
pytest
```

Open the app at `http://localhost:8501`.

## Video Script

### 1. Intro, 30-45 seconds

Say:

```text
Hi, this is my final applied AI system project: Game Glitch Investigator.
It started as my Module 1 Streamlit number guessing game, where the goal was to debug AI-generated game logic.
For the final project, I extended it into a more complete AI system with retrieval, an observable agent workflow, guardrails, logging, confidence scoring, and an evaluation harness.
```

Show:

- The GitHub repo or local file tree.
- `README.md`, briefly pointing to the architecture diagram and setup.

### 2. Base App Demo, 45-60 seconds

Say:

```text
The original user-facing app is still here: a number guessing game with difficulty settings, attempt limits, scoring, hints, and high-score persistence.
The final project does not leave the game broken; the AI layer is a debugging and reliability assistant around the game.
```

Show:

- Streamlit app title.
- Difficulty selector in the sidebar.
- Developer Debug Info.
- Enter one guess and show that the app gives a higher/lower hint.

Good demo move:

- Open Developer Debug Info.
- If the secret is `50`, enter `40` and show `Go HIGHER`; if the secret is lower than your guess, point out it correctly says `Go LOWER`.
- Do not spend too long trying to win; the point is functionality, not gameplay.

### 3. AI Feature Demo, 2-3 minutes

Say:

```text
The main AI feature is the investigator panel.
It uses a local custom knowledge base instead of a hosted API so the project is reproducible.
When I enter a bug report, the system retrieves relevant project knowledge, classifies the failure mode, creates a patch plan, assigns confidence, and shows its intermediate steps.
```

Copy/paste input 1:

```text
When I click submit, the secret number changes and I can never win.
```

Point out:

- Diagnosis should be `streamlit_state`.
- Retrieved evidence should mention Streamlit reruns/session state.
- Agent steps should show validation, retrieval, classification, and plan generation.

Copy/paste input 2:

```text
The hint says go higher even when my guess is above the secret number.
```

Point out:

- Diagnosis should be `hint_logic`.
- Patch plan should mention `check_guess` and tests for too-high/too-low behavior.
- This demonstrates that retrieval changes the answer, not just generic text.

Copy/paste input 3:

```text
Hard mode says it is hard, but the range seems easier than normal.
```

Point out:

- Diagnosis should be `difficulty_range`.
- This shows a different retrieved source and a different patch plan.

### 4. Guardrail Demo, 45-60 seconds

Say:

```text
A reliability requirement for this project is that the AI should not pretend to know something when the input is too vague.
Here is the guardrail behavior.
```

Copy/paste:

```text
bad
```

Point out:

- Diagnosis should be `needs_more_context`.
- Confidence should be low.
- The system asks for visible behavior, expected behavior, and an example input instead of inventing a fix.

### 5. Evaluation Harness, 60-90 seconds

Switch to terminal.

Run:

```bash
python evaluate_system.py
```

Say:

```text
This is the reliability harness.
It runs predefined bug reports and checks that the investigator returns the expected category with enough confidence.
```

Expected result:

```text
Summary: 6/6 cases passed (100%).
```

Optional if time:

```bash
pytest
```

Say:

```text
The unit tests cover both the original game logic and the new investigator layer.
```

Expected result:

```text
34 passed
```

### 6. Architecture and Reflection, 60-90 seconds

Show `assets/system_architecture.svg` or the README diagram.

Say:

```text
The data flow is: a human enters a game issue, the interface sends it to the investigator, the retriever searches custom project knowledge, the agent validates and classifies the report, then it outputs a diagnosis, patch plan, confidence, sources, and reliability checks.
The evaluator and tests are separate human-checkable reliability tools.
```

Then say:

```text
The main limitation is that this system is specialized to this game and its known bug patterns.
That is intentional: a narrow system is easier to test and safer than a generic chatbot.
The main misuse risk is over-trusting a diagnosis without reproducing the bug, so the system shows sources, confidence, intermediate steps, and recommended tests.
```

### 7. Closing, 20-30 seconds

Say:

```text
This project shows what I learned about applied AI systems: useful AI is not just output generation.
It also needs retrieval, transparency, guardrails, testing, and honest limits.
```

End on the README or the evaluation summary.

## Recording Checklist

- Show the app running end-to-end.
- Show at least 2-3 investigator inputs.
- Show retrieved evidence and intermediate agent steps.
- Show one guardrail case.
- Show `python evaluate_system.py`.
- If time allows, show `pytest`.
- Paste the Loom link into `README.md` after recording.
