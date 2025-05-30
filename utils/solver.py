import os
import regex
from collections import Counter
from utils.custom_errors import WrongInputError,NoValidWordsError

def init_wordle(valid_words, initial_guess="adieu", max_attempts=6):
    """
    Initialize Wordle solver state.
    Returns a dict with:
      valid: set of candidate words,
      guess: current guess,
      greens: list of (pos, char),
      yellows: list of (pos, char),
      whites: set of chars,
      attempts: remaining attempts
    """
    return {
        "valid": set(valid_words),
        "guess": initial_guess,
        "greens": [],
        "yellows": [],
        "whites": set(),
        "attempts": max_attempts,
    }

def update_wordle(state, pattern):
    """
    Update the solver state using a feedback pattern string of 5 chars (0/1/2).
    Returns (new_state, next_guess) or (new_state, None) if no attempts remain or no words left.
    """
    if len(pattern) != 5 or any(ch not in "012" for ch in pattern):
        raise WrongInputError()
    
    from collections import Counter

    guess = state["guess"]
    greens = state["greens"]
    yellows = state["yellows"]
    whites = state["whites"]
    attempts = state["attempts"]

    # Process feedback pattern
    for pos, mark in enumerate(pattern):
        char = guess[pos]
        if mark == "2":
            greens.append((pos, char))
        elif mark == "1":
            yellows.append((pos, char))
        elif mark == "0":
            whites.add(char)

    # Deduplicate yellows
    seen = {}
    for i, c in yellows:
        seen.setdefault(c, set()).add(i)
    yellows = [(i, c) for c, positions in seen.items() for i in positions]

    # Remove any whites that became green/yellow
    confirmed = {c for _, c in greens + yellows}
    whites.difference_update(confirmed)

    # Filter valid words
    filtered = []
    for word in state["valid"]:
        if any(word[i] != c for i, c in greens):
            continue
        if not all(c in word and any(word[j] == c and j != i for j in range(5)) for i, c in yellows):
            continue
        if any(c in word for c in whites if c not in {yc for _, yc in yellows} and c not in {gc for _, gc in greens}):
            continue
        filtered.append(word)

    # Score and choose next guess
    letter_counts = Counter("".join(filtered))
    def score(w): return sum(letter_counts[ch] for ch in set(w))
    filtered.sort(key=score, reverse=True)

    attempts -= 1
    if not filtered or attempts <= 0:
        raise NoValidWordsError()

    next_guess = filtered[0]

    new_state = {
        "valid": set(filtered),
        "guess": next_guess,
        "greens": greens,
        "yellows": yellows,
        "whites": whites,
        "attempts": attempts,
    }
    return new_state, next_guess
