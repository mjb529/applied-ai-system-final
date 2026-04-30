import random
import streamlit as st
# FIX: Refactored all core game logic out of app.py into logic_utils.py using Claude Code Agent
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score, get_attempt_limit, is_in_range, load_high_score, save_high_score
from investigator import GameGlitchInvestigator

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("A repaired guessing game plus an AI bug investigator.")

with st.expander("AI Bug Investigator", expanded=True):
    st.write(
        "Describe a bug in the game. The investigator retrieves project knowledge, "
        "classifies the issue, creates a patch plan, and assigns confidence."
    )
    bug_report = st.text_area(
        "Bug report",
        value="The hint says go higher even when my guess is above the secret number.",
    )
    if st.button("Investigate bug"):
        result = GameGlitchInvestigator().investigate(bug_report)
        st.markdown(result.to_markdown())

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = get_attempt_limit(difficulty)  # FIX: replaced inline dict lookup with logic_utils function using Claude Code Agent

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FEATURE: Load and display the all-time high score in the sidebar;
# implemented via Claude Code Agent Mode
st.sidebar.divider()
st.sidebar.metric("🏆 High Score", load_high_score())

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0  # FIX: was initialized to 1, causing one attempt to be lost on start; corrected with Claude Code

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "last_hint" not in st.session_state:
    st.session_state.last_hint = None

# FIX: track active difficulty so switching it resets the game with a valid secret; identified and fixed with Claude Code
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = difficulty

if st.session_state.current_difficulty != difficulty:
    st.session_state.current_difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.last_hint = None

st.subheader("Make a guess")

# FIX: use st.empty() placeholder so the display updates correctly after the submit increment
# on the same render pass; identified and fixed with Claude Code
attempts_info = st.empty()
attempts_info.info(
    f"Guess a number between {low} and {high}. "  # FIX: was hardcoded to "1 and 100" regardless of difficulty; corrected with Claude Code
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

# FIX: expander stays here (original position) to preserve open/closed state across reruns;
# st.empty() placeholders inside are filled after the submit handler so values stay current; fixed with Claude Code
with st.expander("Developer Debug Info"):
    dbg_secret   = st.empty()
    dbg_attempts = st.empty()
    dbg_score    = st.empty()
    dbg_diff     = st.empty()
    dbg_history  = st.empty()

# FIX: wrapped input and submit in st.form so pressing Enter triggers submission; identified and fixed with Claude Code
with st.form("guess_form"):
    raw_guess = st.text_input(
        "Enter your guess:",
        key=f"guess_input_{difficulty}"
    )
    submit = st.form_submit_button("Submit Guess 🚀")

col1, col2 = st.columns(2)
with col1:
    new_game = st.button("New Game 🔁")
with col2:
    show_hint = st.checkbox("Show hint", value=True)

hint_slot = st.empty()

if new_game:
    st.session_state.attempts = 0
    st.session_state.status = "playing"  # FIX: status was never reset on new game so won/lost state persisted; fixed with Claude Code
    st.session_state.history = []
    st.session_state.last_hint = None
    st.session_state.secret = random.randint(low, high)  # FIX: was hardcoded to randint(1, 100), ignoring difficulty; corrected with Claude Code
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.error(err)
    elif not is_in_range(guess_int, low, high):  # FIX: out-of-range guesses were silently accepted; identified and fixed with Claude Code
        st.error(f"Please enter a number between {low} and {high}.")
    else:
        st.session_state.attempts += 1  # FIX: moved increment here so invalid/out-of-range guesses don't waste an attempt; fixed with Claude Code
        st.session_state.history.append(guess_int)

        # FIX: refresh the attempts display after incrementing so the correct count shows this run; fixed with Claude Code
        attempts_info.info(
            f"Guess a number between {low} and {high}. "
            f"Attempts left: {attempt_limit - st.session_state.attempts}"
        )

        secret = st.session_state.secret  # FIX: was cast to str on even attempts, breaking numeric comparison; corrected with Claude Code

        outcome, message = check_guess(guess_int, secret)
        st.session_state.last_hint = message

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            save_high_score(st.session_state.score)  # FEATURE: persist best score to file; implemented via Claude Code Agent Mode
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

if show_hint and st.session_state.last_hint:
    hint_slot.warning(st.session_state.last_hint)

dbg_secret.write("Secret: " + str(st.session_state.secret))
dbg_attempts.write("Attempts: " + str(st.session_state.attempts))
dbg_score.write("Score: " + str(st.session_state.score))
dbg_diff.write("Difficulty: " + difficulty)
dbg_history.write("History: " + str(st.session_state.history))

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
