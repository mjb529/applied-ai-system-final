# Game Logic Knowledge

## Hint comparison rules
Tags: hint_logic

The guessing game compares a numeric guess to a numeric secret. If guess equals secret, the result is Win. If guess is greater than secret, the player guessed too high and should go lower. If guess is less than secret, the player guessed too low and should go higher.

## Scoring rules
Tags: scoring

Winning should add points based on how early the player guessed correctly. Wrong guesses should subtract a consistent penalty whether the guess was too high or too low. High score persistence should only overwrite the saved value when the new score is higher than the old value.

## Difficulty ranges
Tags: difficulty_range

Easy uses a small range and more forgiving play. Normal uses a middle range. Hard should be meaningfully harder than Normal, with a larger range and fewer attempts. The visible instructions, generated secret, out-of-range validation, and attempt limit should all use the same difficulty source of truth.

## Input validation
Tags: input_guardrail

Input handling should reject blank text and non-numeric text before changing game state. Numeric guesses outside the current range should show a clear error and should not spend an attempt. Parsing and range checking are separate steps so each can be tested directly.
