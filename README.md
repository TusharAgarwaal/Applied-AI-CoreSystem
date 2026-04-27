# BeatHive — Conversational Music Recommender


## Video Explanation

If the readme seems not for you, then this video will:
https://www.loom.com/share/cae339bb8fad48d4adf12ecc32837bc5

> Tell me your vibe. I'll find your track.

BeatHive is a command-line music recommender that interviews you in natural language, builds a taste profile from your answers, scores every song in its catalog against that profile using a weighted formula, and returns your top 5 picks with a breakdown of exactly why each song made the cut.

---

## Original Project

This project began as the **Music Recommender Simulation** from Modules 1–3, where the goal was to model how streaming platforms turn user taste data into ranked recommendations. The original system represented songs as structured data (genre, mood, energy, BPM, valence, acousticness, danceability) and implemented a weighted scoring formula — called the **Algorithm Recipe** — that assigned points to each feature based on how closely a song matched a static user profile. The focus was on understanding the mechanics of collaborative and content-based filtering in a small, transparent system before scaling to real-world complexity.

---

## Why It Matters

Real recommenders are black boxes. BeatHive is not. Every score is explainable: you can see exactly how many points a song earned for genre, mood, intensity, acousticness, and valence — and why. The conversational front-end makes the system accessible to anyone, while the transparent scoring makes it educational for anyone learning how AI recommendations work under the hood.

---

## System Architecture

```
User
 │
 ▼
[ agent.py ] — asks 5 questions one at a time
 │               genre → mood → energy → tempo → acoustic preference
 │
 ▼
[ UserProfile dict ] — structured taste profile built from answers
 │
 ▼
[ recommender.py ] — scores every song in the catalog
 │   for each song:
 │     genre match      → +3.0 pts
 │     mood match       → +2.0 pts
 │     intensity delta  → up to +3.0 pts  (energy + BPM combined)
 │     acousticness fit → up to +1.0 pts
 │     valence fit      → up to +1.0 pts
 │                         ──────────────
 │                         max score: 10.0
 │
 ▼
[ Ranked Top-K Songs ] — printed with score and per-feature breakdown
```

Two entry points:
| Command | Mode |
|---|---|
| `python -m src.agent` | Conversational — asks you questions, then recommends |
| `python -m src.main`  | Simulation — pick from preset profiles, then recommends |

![UML Diagram](<Song Recommender UML.png>)

---

## Setup

**Requirements:** Python 3.8+ and either `uv` or `pip`.

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd assets

# 2a. Install with uv (recommended)
uv pip install -r requirements.txt

# 2b. Or install with pip
pip install -r requirements.txt

# 3. Run the conversational agent
uv run python -m src.agent

# 4. Or run the simulation mode
uv run python -m src.main
```

> All commands must be run from the `assets/` directory so that `data/songs.csv` resolves correctly.

---

## Sample Interactions

### Example 1 — Rock Fan

```
BeatHive Music Assistant  (powered by BeatHive 1.0)
────────────────────────────────────────
Answer a few questions and I'll find your perfect tracks.

What genre are you in the mood for?
  1. pop   2. lofi   3. rock   4. ambient   5. jazz   6. synthwave   7. indie pop
Your choice: 3

What's your current mood?
  1. happy   2. chill   3. intense   4. relaxed   5. focused   6. moody
Your choice: 3

How energetic should the music feel?
  1. Low  — quiet and calm
  2. Medium — balanced energy
  3. High  — pumped and intense
Your choice: 3

What tempo do you prefer?
  1. Slow   (60–80 BPM)
  2. Medium (80–110 BPM)
  3. Fast   (110–160 BPM)
Your choice: 3

Do you prefer acoustic / organic sounds over electronic?
  1. Yes
  2. No
Your choice: 2

Finding your tracks...

==================================================
  Your BeatHive Picks
  Rock / intense / energy 85%
==================================================

  #1  Thunderstruck  —  AC/DC
       Score : 9.73 / 10
       Why   :
               • genre match (+3.0)
               • mood match (+2.0)
               • intensity (0.89) match (+2.87)
               • acousticness match (+0.99)
               • valence match (+0.87)

  #2  Enter Sandman  —  Metallica
       Score : 9.56 / 10
       Why   :
               • genre match (+3.0)
               • mood match (+2.0)
               • intensity (0.85) match (+2.99)
               • acousticness match (+0.99)
               • valence match (+0.58)

  #3  Sweet Child O' Mine  —  Guns N' Roses
       Score : 7.82 / 10
       Why   :
               • genre match (+3.0)
               • intensity (0.86) match (+2.96)
               • acousticness match (+0.97)
               • valence match (+0.89)
==================================================
```

---

### Example 2 — Late-Night Lofi Session

```
What genre are you in the mood for?
Your choice: 2   (lofi)

What's your current mood?
Your choice: 2   (chill)

How energetic should the music feel?
Your choice: 1   (Low — quiet and calm)

What tempo do you prefer?
Your choice: 1   (Slow, 60–80 BPM)

Do you prefer acoustic / organic sounds over electronic?
Your choice: 1   (Yes)

Finding your tracks...

==================================================
  Your BeatHive Picks
  Lofi / chill / energy 25%
==================================================

  #1  Snowfall  —  Øneheart
       Score : 9.43 / 10
       Why   :
               • genre match (+3.0)
               • mood match (+2.0)
               • intensity (0.39) match (+2.85)
               • acousticness match (+0.80)
               • valence match (+0.78)

  #2  Feather  —  Nujabes
       Score : 9.30 / 10
       Why   :
               • genre match (+3.0)
               • mood match (+2.0)
               • intensity (0.46) match (+2.66)
               • acousticness match (+0.72)
               • valence match (+0.92)

  #3  Coffee  —  beabadoobee
       Score : 8.93 / 10
       Why   :
               • genre match (+3.0)
               • intensity (0.44) match (+2.70)
               • acousticness match (+0.75)
               • valence match (+0.94)
==================================================
```

---

### Example 3 — Jazz Evening (No Exact Genre Match in Profiles)

```
What genre are you in the mood for?
Your choice: 5   (jazz)

What's your current mood?
Your choice: 4   (relaxed)

How energetic should the music feel?
Your choice: 1   (Low — quiet and calm)

What tempo do you prefer?
Your choice: 2   (Medium, 80–110 BPM)

Do you prefer acoustic / organic sounds over electronic?
Your choice: 1   (Yes)

Finding your tracks...

==================================================
  Your BeatHive Picks
  Jazz / relaxed / energy 25%
==================================================

  #1  Take Five  —  Dave Brubeck Quartet
       Score : 9.19 / 10
       Why   :
               • genre match (+3.0)
               • mood match (+2.0)
               • intensity (0.40) match (+2.83)
               • acousticness match (+0.87)
               • valence match (+0.82)

  #2  Fly Me to the Moon  —  Frank Sinatra
       Score : 8.97 / 10
       Why   :
               • genre match (+3.0)
               • mood match (+2.0)
               • intensity (0.55) match (+2.34)
               • acousticness match (+0.88)
               • valence match (+0.75)

  #3  Weightless  —  Marconi Union
       Score : 6.54 / 10
       Why   :
               • intensity (0.31) match (+2.94)
               • acousticness match (+0.95)
               • valence match (+0.54)
==================================================
```

---

## Design Decisions

### Why a weighted scoring formula instead of ML?

The formula is fully transparent: every point awarded has a named reason. A neural network would likely outperform it on a large catalog, but it would be impossible to explain *why* a song ranked #2 over #3. For an educational tool, explainability outweighs raw accuracy.

### Why a conversational agent for input?

The original simulation used hardcoded profiles. Real users don't think in floats — they think in feelings. The agent maps natural language choices (low / medium / high energy, slow / medium / fast tempo) to numeric values, making the system accessible without changing the scoring logic underneath.

### Trade-offs made

| Decision | Trade-off |
|---|---|
| Rule-based scoring | Transparent but limited — can't learn from feedback |
| Categorical genre/mood matching | Simple but brittle — "indie pop" and "pop" score as completely different |
| BPM mapped to 3 buckets | Easy for users but loses precision |
| 20-song catalog | Enough to test ranking behavior, too small for real use |

### Why intensity carries the most weight (up to 6 of 10 points)?

Genre and mood are categorical — a song either matches or it doesn't. Intensity (energy + BPM combined) is continuous, so it can partially match, making it the most nuanced signal and the best differentiator when genre and mood are already tied.

---

## Testing Summary

Tests live in `tests/test_recommender.py`. Run them with:

```bash
uv run pytest
```

### What the test suite covers

| Test group | What it checks |
|---|---|
| Score bounds | Score never exceeds 10 or drops below 0 |
| Component scoring | Genre adds exactly +3.0, mood adds exactly +2.0 |
| Intensity | Perfect match gives +3.0; large mismatch gives < 1.0 |
| Acousticness | Correctly rewards high acousticness for acoustic users and vice versa |
| Recommender output | Results sorted descending, k-limit respected, empty catalog returns empty |
| Explanation quality | Output is a non-empty string containing all 5 component names |
| Precision@K harness | Fraction of top-k results that match genre or mood |

### What worked

- The scoring formula is logically sound. Every test passed on the first implementation, which confirmed the math was right.
- Precision@K = 1.0 for clear-match profiles (e.g. pop/happy user on a pop-heavy catalog).

### What didn't work

- **Weight sensitivity**: Changing genre weight from 3.0 to 0.5 caused scores to exceed 10 — the formula assumes fixed maximums and breaks if weights shift.
- **Mid-range intensity gap**: Songs clustered at the extremes (very low or very high energy) meant medium-intensity users were always slightly penalized regardless of which song ranked first.

### What I learned

Scoring systems are easy to get right logically but hard to get right empirically. A formula that passes unit tests can still produce rankings that feel wrong for edge-case users — which is exactly why evaluation profiles and Precision@K matter.

---

## Reflection

Building BeatHive changed how I think about recommendation systems in two ways.

First, **categorical features do heavy lifting**. Genre and mood together account for up to 5 of 10 points, which mirrors how real platforms work — Spotify's genre clusters and mood playlists are not cosmetic, they are the core signal. When a user's genre isn't in the catalog at all, the entire ranking collapses into a narrow band of intensity scores, which shows how fragile a recommender becomes when its training data doesn't represent a user.

Second, **explainability is a design choice, not a freebie**. The reason BeatHive can print "genre match (+3.0)" is because the score was designed to be interpretable from the start. Most production models sacrifice this for accuracy. Understanding that trade-off — and when each side of it matters — is the most transferable lesson from this project.

---

## Project Structure

```
assets/
├── data/
│   └── songs.csv          # 20-song catalog with audio features
├── src/
│   ├── agent.py           # Conversational entry point (agentic workflow)
│   ├── main.py            # Simulation entry point (preset profiles)
│   └── recommender.py     # Scoring formula, data loader, Recommender class
├── tests/
│   └── test_recommender.py  # pytest suite + Precision@K harness
├── model_card.md
└── requirements.txt
```

---

## Requirements

```
pandas
pytest
streamlit
```

No API keys. No external services. Runs entirely offline.

---

## Model Card

See [model_card.md](model_card.md) for intended use, data, strengths, limitations, and evaluation.
