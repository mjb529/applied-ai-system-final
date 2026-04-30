def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200  # FIX: Hard was 1-50, easier than Normal's 1-100; corrected to 1-200 with Claude Code
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    # FIX: Refactored from app.py into logic_utils.py using Claude Code Agent
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: Refactored from app.py into logic_utils.py using Claude Code Agent
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"  # FIX: hint messages were swapped; corrected with Claude Code
        else:
            return "Too Low", "📈 Go HIGHER!"  # FIX: hint messages were swapped; corrected with Claude Code
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    # FIX: Refactored from app.py into logic_utils.py using Claude Code Agent
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5  # FIX: even attempts previously rewarded +5 instead of -5; corrected with Claude Code

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def get_attempt_limit(difficulty: str):
    """Return the number of allowed attempts for a given difficulty."""
    # FIX: Extracted inline dict from app.py into logic_utils.py using Claude Code Agent
    limits = {
        "Easy": 6,
        "Normal": 8,
        "Hard": 5,
    }
    return limits.get(difficulty, 8)


def is_in_range(guess: int, low: int, high: int):
    """Return True if guess falls within [low, high]."""
    # FIX: Extracted inline range check from app.py into logic_utils.py using Claude Code Agent
    return low <= guess <= high


# FEATURE: High score persistence — implemented via Claude Code Agent Mode.
# Stores the all-time best score in a plain text file so it survives page reruns
# and browser refreshes. Using a file (not session_state) means it persists
# across multiple game sessions.

HIGH_SCORE_FILE = "high_score.txt"


def load_high_score() -> int:
    """Read the saved high score from disk. Returns 0 if no file exists yet."""
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score: int) -> None:
    """Write score to disk only if it beats the current saved high score."""
    current = load_high_score()
    if score > current:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
