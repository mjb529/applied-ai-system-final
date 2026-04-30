# Streamlit Debugging Knowledge

## Streamlit reruns and session state
Tags: streamlit_state, render_order

Streamlit reruns the Python script from top to bottom after widget interactions. Values such as the secret number, current score, attempt count, status, and history should be saved in st.session_state so they survive reruns. Initialize a value only when its key is missing, then mutate it in response to user actions.

## Render order and stale display values
Tags: render_order, streamlit_state

If a page displays attempts, score, or history before the submit handler mutates state, the visible value can lag by one interaction. A safe fix is to create st.empty placeholders near the desired layout position and fill them after the state update. Keep widgets such as forms and expanders in stable positions so user interactions do not collapse or reset them.

## New game and difficulty reset
Tags: streamlit_state, difficulty_range

New Game should reset attempts, status, history, hint text, and the secret number at the same time. Difficulty changes should also regenerate the secret using the active range, because a secret from Hard mode may be invalid in Easy mode.
