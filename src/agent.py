"""
BeatHive Agentic Workflow — conversational music preference builder.

Interviews the user one question at a time, builds a profile,
then runs the recommender and prints results.

Usage (from assets/ directory):
    python -m src.agent
    python -m src.agent --songs data/songs.csv
"""

import sys, os
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs, MODEL_NAME

GENRES = ["pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie pop"]
MOODS  = ["happy", "chill", "intense", "relaxed", "focused", "moody"]

_ENERGY_OPTIONS = [
    ("Low  — quiet and calm",       0.25),
    ("Medium — balanced energy",    0.55),
    ("High  — pumped and intense",  0.85),
]

_BPM_OPTIONS = [
    ("Slow   (60–80 BPM)",   70),
    ("Medium (80–110 BPM)",  95),
    ("Fast   (110–160 BPM)", 135),
]


def _ask_choice(question: str, options: list) -> str:
    print(f"\n{question}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = input("Your choice: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"Please enter a number between 1 and {len(options)}.")


def _ask_mapped(question: str, options: list) -> float:
    labels = [label for label, _ in options]
    label = _ask_choice(question, labels)
    return next(val for lbl, val in options if lbl == label)


def _ask_yes_no(question: str) -> bool:
    print(f"\n{question}")
    print("  1. Yes\n  2. No")
    while True:
        raw = input("Your choice: ").strip()
        if raw == "1":
            return True
        if raw == "2":
            return False
        print("Please enter 1 or 2.")


def _print_recommendations(profile: dict, recommendations: list) -> None:
    print(f"\n{'=' * 50}")
    print(f"  Your BeatHive Picks")
    print(f"  {profile['genre'].title()} / {profile['mood']} / energy {profile['energy']:.0%}")
    print(f"{'=' * 50}")
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n  #{i}  {song['title']}  —  {song['artist']}")
        print(f"       Score : {score:.2f} / 10")
        print(f"       Why   :")
        for reason in explanation.split(", "):
            print(f"               • {reason}")
    print(f"\n{'=' * 50}\n")


def run_agent(songs_path: str = "data/songs.csv") -> None:
    songs = load_songs(songs_path)

    print(f"\nBeatHive Music Assistant  (powered by {MODEL_NAME})")
    print("─" * 40)
    print("Answer a few questions and I'll find your perfect tracks.\n")

    genre       = _ask_choice("What genre are you in the mood for?", GENRES)
    mood        = _ask_choice("What's your current mood?", MOODS)
    energy      = _ask_mapped("How energetic should the music feel?", _ENERGY_OPTIONS)
    target_bpm  = _ask_mapped("What tempo do you prefer?", _BPM_OPTIONS)
    likes_acoustic = _ask_yes_no("Do you prefer acoustic / organic sounds over electronic?")

    profile = {
        "name":          f"{genre.title()} / {mood}",
        "genre":         genre,
        "mood":          mood,
        "energy":        energy,
        "target_bpm":    target_bpm,
        "likes_acoustic": likes_acoustic,
    }

    print("\nFinding your tracks...")
    recommendations = recommend_songs(profile, songs, k=5)
    _print_recommendations(profile, recommendations)


def main() -> None:
    parser = argparse.ArgumentParser(description="BeatHive conversational music recommender")
    parser.add_argument(
        "--songs", default="data/songs.csv",
        help="Path to songs CSV (default: data/songs.csv)",
    )
    args = parser.parse_args()
    run_agent(songs_path=args.songs)


if __name__ == "__main__":
    main()
