import os
import pytest
from logic_utils import check_guess, get_range_for_difficulty, update_score, parse_guess, is_in_range, get_attempt_limit, load_high_score, save_high_score
import logic_utils


# --- Existing tests (fixed: check_guess returns a tuple, not a bare string) ---

def test_winning_guess():
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Bug 1: Hard difficulty range was 1-50 (easier than Normal's 1-100) ---

def test_hard_range_is_harder_than_normal():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high

def test_hard_range_values():
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high == 200


# --- Bug 2: Hint messages were swapped ---

def test_too_high_message_says_lower():
    # guess > secret means player should go lower
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message.upper()

def test_too_low_message_says_higher():
    # guess < secret means player should go higher
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message.upper()


# --- Bug 3: "Too High" scoring was asymmetric (rewarded on even attempts) ---

def test_too_high_subtracts_on_even_attempt():
    # even attempt number should still subtract, not add
    score = update_score(100, "Too High", 2)
    assert score == 95

def test_too_high_subtracts_on_odd_attempt():
    score = update_score(100, "Too High", 3)
    assert score == 95

def test_too_high_and_too_low_penalized_equally():
    # both wrong-direction guesses should carry the same penalty
    score_high = update_score(100, "Too High", 2)
    score_low = update_score(100, "Too Low", 2)
    assert score_high == score_low


# --- Bug 6: Even attempts cast secret to str, breaking numeric comparison ---
# String comparison: "9" > "10" is True (wrong). Integer comparison: 9 < 10 (correct).

def test_check_guess_single_digit_vs_two_digit():
    # 9 < 10, so result must be Too Low — string comparison would give Too High
    outcome, _ = check_guess(9, 10)
    assert outcome == "Too Low"

def test_check_guess_large_numbers_compare_correctly():
    # 99 < 100, string comparison "99" > "100" is True (wrong)
    outcome, _ = check_guess(99, 100)
    assert outcome == "Too Low"


# --- Bug 8: parse_guess accepts out-of-range values (range check is app-level) ---
# These tests document that parse_guess itself does not enforce bounds.

def test_parse_guess_accepts_out_of_range_number():
    ok, value, err = parse_guess("500")
    assert ok is True
    assert value == 500
    assert err is None

def test_parse_guess_rejects_non_numeric():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert value is None

def test_parse_guess_rejects_empty():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None


# --- is_in_range: extracted from inline app.py check (refactor) ---

def test_in_range_returns_true_for_valid_guess():
    assert is_in_range(50, 1, 100) is True

def test_in_range_returns_false_below_low():
    assert is_in_range(0, 1, 100) is False

def test_in_range_returns_false_above_high():
    assert is_in_range(101, 1, 100) is False

def test_in_range_inclusive_boundaries():
    assert is_in_range(1, 1, 100) is True
    assert is_in_range(100, 1, 100) is True


# --- get_attempt_limit: extracted from inline dict in app.py (refactor) ---

def test_attempt_limit_easy():
    assert get_attempt_limit("Easy") == 6

def test_attempt_limit_normal():
    assert get_attempt_limit("Normal") == 8

def test_attempt_limit_hard():
    assert get_attempt_limit("Hard") == 5


# --- Bug: difficulty switch did not reset secret to a valid range ---
# The fix is app-level (session state), but the underlying logic is testable:
# a secret from Hard (1-200) can fall outside Easy's range (1-20).

def test_hard_secret_may_be_outside_easy_range():
    _, easy_high = get_range_for_difficulty("Easy")
    _, hard_high = get_range_for_difficulty("Hard")
    # Hard's upper bound exceeds Easy's — so a Hard secret can be out of Easy's range
    assert hard_high > easy_high

def test_is_in_range_catches_cross_difficulty_secret():
    # Simulates a secret of 100 (valid on Hard) being checked against Easy's range (1-20)
    easy_low, easy_high = get_range_for_difficulty("Easy")
    assert is_in_range(100, easy_low, easy_high) is False


# --- FEATURE: High score persistence (implemented via Claude Code Agent Mode) ---

@pytest.fixture(autouse=True)
def tmp_high_score_file(tmp_path, monkeypatch):
    """Redirect HIGH_SCORE_FILE to a temp path so tests don't touch the real file."""
    monkeypatch.setattr(logic_utils, "HIGH_SCORE_FILE", str(tmp_path / "high_score.txt"))

def test_load_high_score_returns_zero_when_no_file():
    assert load_high_score() == 0

def test_save_high_score_creates_file_with_score():
    save_high_score(42)
    assert load_high_score() == 42

def test_save_high_score_updates_when_new_score_is_higher():
    save_high_score(50)
    save_high_score(80)
    assert load_high_score() == 80

def test_save_high_score_does_not_update_when_new_score_is_lower():
    save_high_score(80)
    save_high_score(30)
    assert load_high_score() == 80

def test_save_high_score_does_not_update_on_equal_score():
    save_high_score(50)
    save_high_score(50)
    assert load_high_score() == 50
