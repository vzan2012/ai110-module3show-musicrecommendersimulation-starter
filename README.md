# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This simulation builds a content-based music recommender that scores songs from a small catalog against a user's taste profile. Unlike real-world platforms (Spotify, YouTube) that combine collaborative filtering — learning from millions of users' behavior — with audio analysis, this version focuses entirely on song attributes: genre, mood, energy, valence, and acousticness. Each song receives a weighted similarity score against the user's preferences, and the top-k highest-scoring songs are returned as recommendations with a plain-language explanation of why each one matched.

---

## How The System Works

Real-world recommenders like Spotify combine two strategies: **collaborative filtering** (finding users with similar taste and recommending what they loved) and **content-based filtering** (matching a song's audio attributes to a user's preference profile). Collaborative filtering is powerful but requires massive behavioral data and fails for new users or new songs. This simulation prioritizes the content-based approach — it is transparent, explainable, and works from song attributes alone, making it ideal for understanding the core mechanics of recommendation without needing user history.

This system scores every song in the catalog against the user's taste profile using a weighted formula, then ranks all songs by score and returns the top-k results.

### `Song` Features

| Feature | Type | Role in Scoring |
|---|---|---|
| `genre` | categorical | Primary taste signal — weighted 30% |
| `mood` | categorical | Listening context signal — weighted 25% |
| `energy` | float (0–1) | Proximity to user's target energy — weighted 20% |
| `valence` | float (0–1) | Emotional tone (happy vs. dark) — weighted 15% |
| `acousticness` | float (0–1) | Organic vs. electronic texture — weighted 10% |
| `tempo_bpm` | float (60–152) | Normalized and used as supporting signal |
| `danceability` | float (0–1) | Supporting signal for rhythm preference |
| `title`, `artist`, `id` | string/int | Display and identification only |

### `UserProfile` Fields

| Field | Type | What It Captures |
|---|---|---|
| `favorite_genre` | string | Hard preference — matched exactly against song genre |
| `favorite_mood` | string | Listening context — matched exactly against song mood |
| `target_energy` | float (0–1) | Desired intensity level — scored by proximity |
| `target_valence` | float (0–1) | Emotional brightness — scored by proximity |
| `target_acousticness` | float (0–1) | Texture preference — scored by proximity |

### Data Flow

```mermaid
flowchart TD
    A([User Preferences\ngenre · mood · target_energy\ntarget_valence · target_acousticness]) --> B

    B[load_songs\ndata/songs.csv] --> C[Song catalog\n18 songs as dicts]

    C --> D{For each song\nin catalog}

    D --> E[Score one song\n_score_song]

    E --> E1[genre match?\n+2.00 pts]
    E --> E2[mood match?\n+1.50 pts]
    E --> E3[energy proximity\n+up to 1.00 pt]
    E --> E4[valence proximity\n+up to 0.75 pt]
    E --> E5[acousticness proximity\n+up to 0.50 pt]

    E1 & E2 & E3 & E4 & E5 --> F[song score\n0.00 – 5.75 pts]

    F --> G[Build explanation\n_explain]
    G --> H[tuple: song · score · explanation]

    H --> D

    D -->|all songs scored| I[Sort descending\nby score]
    I --> J[Return top-k\nrecommendations]

    J --> K([Output\ntitle · score · explanation])
```

### Scoring Formula

```
score  =  2.00  ×  (genre == user.genre)
       +  1.50  ×  (mood  == user.mood)
       +  1.00  ×  (1 - |target_energy       - song.energy|)
       +  0.75  ×  (1 - |target_valence      - song.valence|)
       +  0.50  ×  (1 - |target_acousticness - song.acousticness|)

max possible score = 5.75
```

### Algorithm Recipe (Finalized)

The full decision process for producing a recommendation:

1. **Load** — Read `data/songs.csv` into a list of 18 song dicts, casting all numeric fields to `float`.
2. **Profile** — Accept a `user_prefs` dict with five keys: `genre`, `mood`, `target_energy`, `target_valence`, `target_acousticness`.
3. **Score every song** — For each song, compute a score out of 5.75 using the formula above. Categorical fields (genre, mood) use exact string matching for binary points. Numeric fields use inverse absolute difference so closeness — not raw magnitude — is rewarded.
4. **Explain** — For each song, generate a plain-language sentence identifying which features drove the match (e.g., genre/mood hit, energy proximity).
5. **Rank** — Sort all `(song, score, explanation)` tuples by score descending. Ties are broken by catalog order (`song["id"]`).
6. **Return** — Slice the sorted list to the top-k results and print them.

### Potential Biases to Watch For

- **Genre dominance** — Genre carries 2.00 of 5.75 possible points (35%). A song with a perfect genre match but mediocre numeric features will almost always outrank a song with no genre match but excellent energy, valence, and acousticness alignment. Great songs in unexpected genres are systematically buried.

- **Mood lock-in** — Mood adds another 1.50 points (26%). Together, genre + mood account for 61% of the maximum score. Any user profile whose genre or mood has fewer than 2–3 catalog entries will see those features dominate the results regardless of audio similarity.

- **Catalog representation gap** — The 18-song catalog has 13 genres but uneven depth: pop has 2 entries, lofi has 3, while metal, reggae, classical, and country each have only 1. A user who prefers metal can only ever get 1 genre-match point across the entire catalog, while a pop user can earn it on 2 songs.

- **Cold-start user problem** — The system has no fallback for a user whose stated genre or mood does not appear in the catalog at all (e.g., `genre = "bossa nova"`). Both categorical scores collapse to 0.00 and the system degrades to ranking purely by numeric similarity — which it will do silently, with no warning.

- **Binary categorical scoring** — Genre and mood are all-or-nothing. There is no partial credit for related genres (e.g., "indie pop" vs "pop" scores the same as "metal" vs "pop" — both 0). A more sophisticated system would use genre-similarity embeddings to award partial points for close genres.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Sample Terminal Output

```
Loaded songs: 18

                  [ USER PROFILE ]                  
----------------------------------------------------
  Genre      : pop
  Mood       : happy
  Energy     : 0.8
  Valence    : 0.78
  Acousticness: 0.2
----------------------------------------------------

              [ TOP RECOMMENDATIONS ]               
----------------------------------------------------
  #1  Sunrise City  -  Neon Echo
       Genre: pop  |  Mood: happy
       Score: 5.67 / 5.75
       Why  : genre match: pop (+2.0) | mood match: happy (+1.5) | energy similarity: 0.98/1.00 | valence similarity: 0.71/0.75 | acousticness similarity: 0.49/0.50

  #2  Gym Hero  -  Max Pulse
       Genre: pop  |  Mood: intense
       Score: 4.04 / 5.75
       Why  : genre match: pop (+2.0) | energy similarity: 0.87/1.00 | valence similarity: 0.74/0.75 | acousticness similarity: 0.42/0.50

  #3  Rooftop Lights  -  Indigo Parade
       Genre: indie pop  |  Mood: happy
       Score: 3.61 / 5.75
       Why  : mood match: happy (+1.5) | energy similarity: 0.96/1.00 | valence similarity: 0.73/0.75 | acousticness similarity: 0.43/0.50

  #4  Crown the Moment  -  Verse Capital
       Genre: hip-hop  |  Mood: uplifting
       Score: 2.15 / 5.75
       Why  : energy similarity: 0.98/1.00 | valence similarity: 0.73/0.75 | acousticness similarity: 0.44/0.50

  #5  Night Drive Loop  -  Neon Echo
       Genre: synthwave  |  Mood: moody
       Score: 1.97 / 5.75
       Why  : energy similarity: 0.95/1.00 | valence similarity: 0.53/0.75 | acousticness similarity: 0.49/0.50

----------------------------------------------------
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

