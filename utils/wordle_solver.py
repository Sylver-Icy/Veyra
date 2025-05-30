import os
import regex
from collections import Counter

def solve_wordle(valid_words, initial_guess="adieu", max_attempts=6):
    """
    Interactive Wordle solver function.
    valid_words: list of candidate words.
    initial_guess: starting guess word.
    max_attempts: maximum number of attempts.
    """
    # Initialize solver state
    guess = initial_guess
    green_letters = []
    white_letters = set()
    yellow_letters = []
    attempt = max_attempts

    while attempt > 0:
        print(guess)
        while True:
            result = input("Put a string of 0,1,2 where 0 mean white 1 mean yellow 2 mean green: ")
            if regex.fullmatch(r"[012]{5}", result):
                break
            print("Invalid input. Enter exactly 5 characters using 0, 1, or 2.")
        pos=0
        for i in result:
            if i == "0":
                white_letters.add(guess[pos])
            elif i == "1":
                yellow_letters.append((pos, guess[pos]))
            elif i == "2":
                green_letters.append((pos, guess[pos]))
            else:
                print("invalid input")
                break
            pos += 1

        # Deduplicate yellow letters by position and character
        seen = {}
        for i, c in yellow_letters:
            if c not in seen:
                seen[c] = set()
            seen[c].add(i)
        yellow_letters = [(i, c) for c in seen for i in seen[c]]

        # Remove white letters that turned out to be yellow or green
        confirmed_letters = {c for _, c in yellow_letters + green_letters}
        white_letters.difference_update(confirmed_letters)
        
        filtered = []
        for word in valid_words:
            # Green letter check
            if not all(word[i] == c for i, c in green_letters):
                continue
            # Yellow letter check
            if not all(
                c in word and any(word[j] == c and j != i for j in range(5))
                for i, c in yellow_letters
            ):
                continue
            # White letter check (improved)
            yellow_chars = set(c for _, c in yellow_letters)
            green_chars = set(c for _, c in green_letters)
            if any(c in word for c in white_letters if c not in yellow_chars and c not in green_chars):
                continue
            filtered.append(word)

        # Build letter frequency across all remaining words
        letter_counts = Counter("".join(filtered))

        # Score words by frequency of unique letters
        def score(word):
            return sum(letter_counts[c] for c in set(word))  # set() to avoid double-counting

        filtered.sort(key=score, reverse=True)

        if not filtered:
            print("No valid words remaining. Exiting.")
            break

        guess = filtered[0]
        attempt -= 1

    print("No attempts left. Failed to guess the word.")


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(__file__), "..", "wordle.txt")) as file:
        valid_words = [line.strip() for line in file]
    solve_wordle(valid_words)