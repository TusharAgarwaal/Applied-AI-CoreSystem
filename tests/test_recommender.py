import pytest
from src.recommender import Song, UserProfile, Recommender, score_song


# ─── fixtures ──────────────────────────────────────────────────────────────

def make_pop_song(valence=0.7, acousticness=0.2, energy=0.8, tempo_bpm=128) -> Song:
    return Song(id=1, title="Pop Track", artist="Artist A", genre="pop", mood="happy",
                energy=energy, tempo_bpm=tempo_bpm, valence=valence,
                danceability=0.8, acousticness=acousticness)


def make_lofi_song() -> Song:
    return Song(id=2, title="Lofi Loop", artist="Artist B", genre="lofi", mood="chill",
                energy=0.4, tempo_bpm=78, valence=0.6, danceability=0.5, acousticness=0.9)


def make_pop_user(likes_acoustic=False) -> UserProfile:
    return UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, target_bpm=128, likes_acoustic=likes_acoustic)


def make_catalog() -> list:
    return [make_pop_song(), make_lofi_song()]


# ─── score bounds ──────────────────────────────────────────────────────────

def test_score_never_exceeds_10():
    score, _ = score_song(make_pop_song(), make_pop_user())
    assert score <= 10.0


def test_score_never_below_zero():
    # No genre/mood match, max intensity gap, max acoustic penalty, lowest valence
    song = Song(id=99, title="Mismatch", artist="X", genre="jazz", mood="sad",
                energy=1.0, tempo_bpm=160, valence=0.0, danceability=0.5, acousticness=1.0)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.0, target_bpm=60, likes_acoustic=False)
    score, _ = score_song(song, user)
    assert score >= 0.0


def test_perfect_match_scores_near_max():
    # acousticness=0 → full 1.0 point for a user who dislikes acoustic
    song = make_pop_song(valence=0.7, acousticness=0.0, energy=0.8, tempo_bpm=128)
    user = make_pop_user(likes_acoustic=False)
    score, _ = score_song(song, user)
    assert score >= 9.5


def test_score_is_deterministic():
    song, user = make_pop_song(), make_pop_user()
    score1, _ = score_song(song, user)
    score2, _ = score_song(song, user)
    assert score1 == score2


# ─── component scoring ─────────────────────────────────────────────────────

def test_genre_match_adds_three_points():
    user = make_pop_user()
    # Two songs identical in every way except genre
    song_match = Song(id=1, title="A", artist="X", genre="pop", mood="sad",
                      energy=0.5, tempo_bpm=100, valence=0.7, danceability=0.5, acousticness=0.5)
    song_no_match = Song(id=2, title="B", artist="X", genre="rock", mood="sad",
                         energy=0.5, tempo_bpm=100, valence=0.7, danceability=0.5, acousticness=0.5)
    score_match, _ = score_song(song_match, user)
    score_no_match, _ = score_song(song_no_match, user)
    assert score_match - score_no_match == pytest.approx(3.0, abs=0.01)


def test_mood_match_adds_two_points():
    user = make_pop_user()
    # Two songs identical in every way except mood
    song_match = Song(id=1, title="A", artist="X", genre="rock", mood="happy",
                      energy=0.5, tempo_bpm=100, valence=0.7, danceability=0.5, acousticness=0.5)
    song_no_match = Song(id=2, title="B", artist="X", genre="rock", mood="chill",
                         energy=0.5, tempo_bpm=100, valence=0.7, danceability=0.5, acousticness=0.5)
    score_match, _ = score_song(song_match, user)
    score_no_match, _ = score_song(song_no_match, user)
    assert score_match - score_no_match == pytest.approx(2.0, abs=0.01)


def test_intensity_perfect_match_adds_three():
    song = make_pop_song(energy=0.8, tempo_bpm=128)
    user = make_pop_user()  # target_energy=0.8, target_bpm=128
    _, reasons = score_song(song, user)
    intensity_reason = next(r for r in reasons if "intensity" in r)
    assert "+3.0" in intensity_reason


def test_intensity_large_mismatch_adds_less_than_one():
    # user wants max intensity, song has near-min intensity
    song = Song(id=5, title="Slow", artist="X", genre="jazz", mood="relaxed",
                energy=0.0, tempo_bpm=60, valence=0.7, danceability=0.5, acousticness=0.5)
    user = UserProfile(favorite_genre="jazz", favorite_mood="relaxed",
                       target_energy=1.0, target_bpm=160, likes_acoustic=False)
    _, reasons = score_song(song, user)
    intensity_reason = next(r for r in reasons if "intensity" in r)
    pts = float(intensity_reason.split("+")[-1].rstrip(")"))
    assert pts < 1.0


def test_acousticness_likes_acoustic_rewards_high_acousticness():
    song_acoustic = make_pop_song(acousticness=0.9)
    song_electric = make_pop_song(acousticness=0.1)
    user_acoustic = make_pop_user(likes_acoustic=True)
    score_a, _ = score_song(song_acoustic, user_acoustic)
    score_e, _ = score_song(song_electric, user_acoustic)
    assert score_a > score_e


def test_acousticness_dislikes_acoustic_rewards_low_acousticness():
    song_acoustic = make_pop_song(acousticness=0.9)
    song_electric = make_pop_song(acousticness=0.1)
    user_electric = make_pop_user(likes_acoustic=False)
    score_a, _ = score_song(song_acoustic, user_electric)
    score_e, _ = score_song(song_electric, user_electric)
    assert score_e > score_a


# ─── recommender output ────────────────────────────────────────────────────

def test_recommendations_sorted_descending():
    rec = Recommender(make_catalog())
    user = make_pop_user()
    results = rec.recommend(user, k=2)
    scores = [score_song(s, user)[0] for s in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_k_equals_1_returns_one_song():
    rec = Recommender(make_catalog())
    results = rec.recommend(make_pop_user(), k=1)
    assert len(results) == 1


def test_recommend_k_exceeds_catalog_returns_all():
    catalog = make_catalog()
    rec = Recommender(catalog)
    results = rec.recommend(make_pop_user(), k=999)
    assert len(results) == len(catalog)


def test_recommend_empty_catalog_returns_empty():
    rec = Recommender([])
    results = rec.recommend(make_pop_user(), k=5)
    assert results == []


def test_best_match_ranked_first():
    rec = Recommender(make_catalog())
    results = rec.recommend(make_pop_user(), k=2)
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


# ─── explanation quality ───────────────────────────────────────────────────

def test_explanation_is_non_empty_string():
    rec = Recommender(make_catalog())
    explanation = rec.explain_recommendation(make_pop_user(), make_pop_song())
    assert isinstance(explanation, str) and explanation.strip()


def test_explanation_contains_all_scoring_components():
    # pop song + pop user → genre AND mood both match, so all 5 components appear
    rec = Recommender(make_catalog())
    explanation = rec.explain_recommendation(make_pop_user(), make_pop_song())
    assert "genre" in explanation
    assert "mood" in explanation
    assert "intensity" in explanation
    assert "acousticness" in explanation
    assert "valence" in explanation


# ─── Precision@K evaluation harness ───────────────────────────────────────

def precision_at_k(rec: Recommender, user: UserProfile, k: int) -> float:
    """Fraction of top-k results that match the user's genre OR mood."""
    results = rec.recommend(user, k=k)
    if not results:
        return 0.0
    relevant = sum(
        1 for s in results
        if s.genre == user.favorite_genre or s.mood == user.favorite_mood
    )
    return relevant / len(results)


def test_precision_at_k_clear_match_user():
    catalog = [
        Song(id=1, title="A", artist="X", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=128, valence=0.7, danceability=0.8, acousticness=0.2),
        Song(id=2, title="B", artist="X", genre="pop", mood="chill",
             energy=0.7, tempo_bpm=120, valence=0.6, danceability=0.7, acousticness=0.3),
        Song(id=3, title="C", artist="X", genre="lofi", mood="chill",
             energy=0.4, tempo_bpm=78, valence=0.6, danceability=0.5, acousticness=0.9),
    ]
    rec = Recommender(catalog)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, target_bpm=128, likes_acoustic=False)
    # Top-2 should both be pop → Precision@2 = 1.0
    assert precision_at_k(rec, user, k=2) == 1.0


def test_precision_at_k_no_catalog_match():
    catalog = [
        Song(id=1, title="A", artist="X", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=128, valence=0.7, danceability=0.8, acousticness=0.2),
        Song(id=2, title="B", artist="X", genre="lofi", mood="chill",
             energy=0.4, tempo_bpm=78, valence=0.6, danceability=0.5, acousticness=0.9),
    ]
    rec = Recommender(catalog)
    user = UserProfile(favorite_genre="classical", favorite_mood="sad",
                       target_energy=0.5, target_bpm=90, likes_acoustic=False)
    # Neither song matches classical or sad → Precision@2 = 0.0
    assert precision_at_k(rec, user, k=2) == 0.0


def test_precision_at_k_partial_match():
    catalog = [
        Song(id=1, title="A", artist="X", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=128, valence=0.7, danceability=0.8, acousticness=0.2),
        Song(id=2, title="B", artist="X", genre="lofi", mood="chill",
             energy=0.4, tempo_bpm=78, valence=0.6, danceability=0.5, acousticness=0.9),
        Song(id=3, title="C", artist="X", genre="pop", mood="chill",
             energy=0.7, tempo_bpm=110, valence=0.65, danceability=0.7, acousticness=0.25),
    ]
    rec = Recommender(catalog)
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, target_bpm=128, likes_acoustic=False)
    p = precision_at_k(rec, user, k=3)
    # Songs 1 and 3 are pop → at least 2/3 relevant
    assert p >= 2 / 3
