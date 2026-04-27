"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs, MODEL_NAME

# Three distinct user profiles for simulation
USER_PROFILES = [
    {
        "name": "High-Energy Pop",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "target_bpm": 128,
        "likes_acoustic": False,
    },
    {
        "name": "Chill Lofi",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "target_bpm": 75,
        "likes_acoustic": True,
    },
    {
        "name": "Deep Intense Rock",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "target_bpm": 150,
        "likes_acoustic": False,
    },
]

# Edge case / adversarial profiles for robustness testing
EDGE_CASE_PROFILES = [
    # No genre or mood match — tests scoring with zero categorical matches
    {
        "name": "No Match Profile",
        "genre": "classical",
        "mood": "sad",
        "energy": 0.5,
        "target_bpm": 100,
        "likes_acoustic": False,
    },
    # Ultra low intensity — tests lower bound of intensity scoring
    {
        "name": "Ultra Chill",
        "genre": "ambient",
        "mood": "chill",
        "energy": 0.1,
        "target_bpm": 60,
        "likes_acoustic": True,
    },
    # Conflicting signals — high energy but acoustic (no song satisfies both)
    {
        "name": "Acoustic Workout",
        "genre": "pop",
        "mood": "intense",
        "energy": 0.9,
        "target_bpm": 140,
        "likes_acoustic": True,
    },
    # Nearly identical profiles — tests stable ranking with small preference deltas
    {
        "name": "Lofi A",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "target_bpm": 78,
        "likes_acoustic": True,
    },
    {
        "name": "Lofi B",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.42,
        "target_bpm": 80,
        "likes_acoustic": True,
    },
]


def _print_recommendations(profile: dict, recommendations: list) -> None:
    print("\n" + "=" * 40)
    print(f"  Profile: {profile['name']}")
    print("=" * 40)
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{i} {song['title']} by {song['artist']}")
        print(f"    Score : {score:.2f} / 10")
        print(f"    Why   :")
        for reason in explanation.split(", "):
            print(f"            - {reason}")
    print("\n" + "=" * 40)


def main() -> None:
    songs = load_songs("data/songs.csv")
    all_profiles = USER_PROFILES + EDGE_CASE_PROFILES

    print(f"\nPowered by {MODEL_NAME}")
    print("\nAvailable Profiles:")
    for i, profile in enumerate(all_profiles, start=1):
        print(f"  {i}. {profile['name']}")

    while True:
        try:
            choice = input("\nSelect a profile (enter number): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(all_profiles):
                break
            print(f"Please enter a number between 1 and {len(all_profiles)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    selected = all_profiles[index]
    k = 20 if selected["name"] == "No Match Profile" else 5
    recommendations = recommend_songs(selected, songs, k=k)
    _print_recommendations(selected, recommendations)


if __name__ == "__main__":
    main()
