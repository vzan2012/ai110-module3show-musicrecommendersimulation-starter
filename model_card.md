# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0** — a simple music recommender that scores songs based on how well they match what you tell it you like.

---

## 2. Intended Use  

VibeFinder is built for classroom use only. It is designed to suggest songs from a small catalog to a single user based on five stated preferences: genre, mood, energy, valence, and acousticness. It assumes the user can describe their taste upfront. It is not designed for real users, live streaming, or any situation where the catalog has more than a few dozen songs.

**Not intended for:** real-world music apps, production deployments, users who cannot or do not want to describe their preferences, or any catalog larger than ~50 songs.

---

## 3. How the Model Works  

Think of VibeFinder like a judge at a talent show scoring each act on five categories. Every song in the catalog gets judged against what the user says they want. Genre is worth the most points — if the song's genre matches yours, it starts with a big advantage. Mood is worth the second most. Then energy, valence (how happy or dark the song sounds), and acousticness (how organic vs electronic it feels) are each scored based on how close the song is to your target — the closer, the more points. Once every song has a total score out of 5.75, the five highest-scoring songs are returned as recommendations, each with a breakdown showing exactly where the points came from.

---

## 4. Data  

The catalog has 18 songs stored in a CSV file. It covers 13 genres — pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, classical, country, edm, reggae, metal, and folk — and 12 mood labels. Eight songs were added beyond the original 10 to improve genre diversity. Each song has five scored attributes (energy, valence, danceability, acousticness, tempo) plus a genre and mood label. The dataset is entirely fictional and reflects a Western, English-language bias. Most genres have only one song, so the catalog is wide but very thin.

---

## 5. Strengths  

The system works well when the user's preferred genre has at least two songs in the catalog and their mood preference is clearly represented. For profiles like "chill lofi" or "intense rock," the top recommendation is genuinely the best fit and the score gap confirms it. The per-song reasons output makes it easy to understand exactly why each song ranked where it did, which is a transparency advantage most real recommenders do not offer. It also handles numeric features gracefully — a song does not need to be a perfect energy match to score well, just close.

---

## 6. Limitations and Bias 

**Primary weakness: Genre dominance creates a filter bubble for most users.**

Genre carries 35% of the total possible score (2.0 out of 5.75) and is evaluated as a strict all-or-nothing match — "indie pop" scores the same as "metal" against a "pop" user (zero points for both), even though indie pop is musically far closer. This means the system almost always returns same-genre songs at the top, effectively trapping users inside their stated genre regardless of how well other songs match their energy, mood, or valence. A user who lists "pop" as their favourite genre will rarely discover a hip-hop or r&b track that fits their vibe perfectly, because no amount of numeric similarity can overcome the 2.0-point genre gap without a matching genre entry in the catalog. This bias was confirmed experimentally: halving the genre weight from 2.0 to 1.0 caused Rooftop Lights (indie pop, mood: happy) to correctly overtake Gym Hero (pop, mood: intense) for a happy-pop user, showing that the original weight suppresses mood-compatible cross-genre results. In a real recommender system this kind of filter bubble would cause users to hear the same narrow slice of the catalog repeatedly, reducing discovery and reinforcing existing taste rather than expanding it.

**Additional limitations discovered:**

- **Conflicting preferences are invisible.** Features are scored independently with no interaction terms. A user requesting high energy (0.92) and melancholic mood simultaneously gets Wooden Maps — a quiet folk track with energy 0.31 — ranked #2 purely because its mood label matches. The system cannot detect or penalise contradictory preference combinations.
- **Cold start collapses confidence.** When a user's genre does not exist in the catalog (e.g. "bossa nova"), all 18 songs score zero on the genre dimension and the top four results cluster within 0.16 points. Rankings in this state are effectively arbitrary — small floating-point differences in energy proximity decide the order.
- **Thin catalog amplifies all biases.** With only one song per genre for 13 of 18 genres, the #1 result is predetermined for most genre searches before any scoring begins. The system produces a ranked list of 5 results, but only the top position carries any real information.

---

## 7. Evaluation  

Six user profiles were tested by running `python -m src.main` and examining the top 5 ranked songs for each. Three profiles were "normal" — designed to have clear, expected results — and three were adversarial edge cases designed to expose weaknesses.

**Profiles tested:**

| Profile | Genre | Mood | Energy | Purpose |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.90 | Normal — should surface upbeat pop songs |
| Chill Lofi | lofi | chill | 0.38 | Normal — should surface calm, acoustic-leaning songs |
| Deep Intense Rock | rock | intense | 0.92 | Normal — only one rock/intense song in catalog |
| Conflicting: High Energy + Melancholic | metal | melancholic | 0.92 | Adversarial — energy and mood point in opposite directions |
| Unknown Genre (Cold Start) | bossa nova | romantic | 0.48 | Adversarial — genre not in catalog at all |
| All-Middle / Neutral | jazz | relaxed | 0.50 | Adversarial — all numeric preferences at midpoint |

**What I looked for:** Whether the top-ranked song was the one a human would intuitively pick, whether the score gaps between #1 and #2 made sense, and whether any songs appeared unexpectedly across multiple profiles.

**What surprised me:**

- *Gym Hero kept appearing for profiles that should not want it.* It ranked #2 for both High-Energy Pop and Deep Intense Rock. For the pop user, it makes partial sense (same genre), but for the rock user it ranked #2 purely because its energy (0.93) is close to the target — even though it is a pop song and the user wanted rock. This happens because the scoring treats each feature as independent: a near-perfect energy score can compensate for a zero genre score, and the system has no way to say "this genre is simply wrong."

- *The weight-shift experiment changed who ranked #2 more than who ranked #1.* When genre weight was halved and energy weight doubled, every profile's #1 song stayed the same — the top spot is locked in by catalog depth (only one perfect match per genre). But #2 and #3 shuffled noticeably, revealing that the middle rankings are where the weights actually matter.

- *A song about a quiet rainy library (Library Rain) and a song about meditating in space (Spacewalk Thoughts) compete for the same user.* For the Chill Lofi profile, Library Rain and Spacewalk Thoughts are both valid picks — one matches by genre, one by mood. Whether genre or mood wins as the tiebreaker depends entirely on which weight is higher. This made it clear that weight choices are not neutral design decisions — they encode an opinion about what kind of similarity matters most.

---

## 8. Future Work  

1. Replace binary genre matching with a genre-similarity score — "indie pop" should earn partial points against a "pop" user, not zero. A simple genre-family lookup table would fix the biggest bias in the current system.
2. Add a conflict detection step — if a user's mood and energy preferences point in opposite directions (e.g. melancholic mood but 0.92 energy), flag the contradiction and weight the conflicting features less rather than scoring them independently.
3. Expand the catalog to at least 5 songs per genre so that ranking below #1 carries real information. Right now, for most genres, #1 is predetermined and positions 2–5 are just noise.

---

## 9. Personal Reflection  

**Profile pair comparisons — what changed and why:**

*High-Energy Pop vs Chill Lofi:*
These two profiles are almost perfect opposites, and the system handled both confidently. The pop user got Sunrise City at the top; the lofi user got Library Rain. What is interesting is that both #1 songs scored nearly identically — 5.62 and 5.67 out of 5.75 — which shows the system works best when a song exists in the catalog that matches all five preferences at once. When such a song exists, it wins by a landslide. The danger is that the second-place song in both cases scored roughly 1.4 to 1.5 points lower, meaning the system is very confident about #1 and very uncertain about everything below it.

*Chill Lofi vs Deep Intense Rock:*
The lofi user's top 3 were all either lofi-genre or chill-mood songs — calm, slow, acoustic-leaning. The rock user's top 3 were all high-energy, low-acousticness songs. The preferences literally pulled the catalog in opposite directions, and the system correctly separated them. However, both profiles suffer the same structural problem: there is only one "perfect" song in the catalog per profile, so the #1 result was never really a competition. A real recommender needs depth across the catalog, not just one representative per genre.

*Deep Intense Rock vs Conflicting (High Energy + Melancholic):*
This comparison is the most revealing. The rock user wants intensity and energy — and they get Storm Runner cleanly. The conflicting user wants the same energy level but a sad, dark mood — and they get Iron Cathedral at #1 (correct on genre and energy and valence) but Wooden Maps at #2, which is a quiet folk song. Why does Wooden Maps appear? Because it is the only song in the catalog with the mood label "melancholic," so it earns the full 1.5 mood-match bonus — even though its energy is 0.31, completely opposite to the user's target of 0.92. In plain English: the system found a song that matched the user's feelings but completely ignored whether the song actually sounds like what the user described. A human DJ would never play a slow acoustic ballad for someone who asked for something intense and dark.

*Unknown Genre (Cold Start) vs All-Middle / Neutral:*
Both profiles are cases where the system loses confidence. The bossa nova user got Velvet Hours at #1 — a reasonable r&b choice — but the second through fifth results were nearly tied, separated by less than 0.20 points. The neutral user got Coffee Shop Stories at #1 by a large margin, but only because it was the sole jazz/relaxed song, not because it was genuinely the best match. In both cases the system produced a ranked list that looks authoritative but is actually quite uncertain. This is one of the most important things I learned: a score of 3.60 out of 5.75 looks meaningful, but if the next four songs all score between 2.00 and 2.20, the ranking is essentially a coin flip. Real recommender systems show a confidence level alongside the recommendation for exactly this reason.

**What this changed about how I think about Spotify and YouTube:**
Before building this, I assumed recommendation algorithms were mostly about finding songs that "sound similar." Building this system showed me that similarity is a design choice — you have to decide which features define similarity, how much weight each one carries, and what happens when they conflict. Every weight in the scoring formula is an opinion encoded as a number. When Spotify decides that your listening history matters more than the song's genre, that is a values decision as much as a technical one. The fact that their system learns those weights from millions of users does not make the choice neutral — it means the weights reflect the average preference, which will feel wrong to anyone whose taste is unusual or underrepresented in the training data.

---

**Personal Reflection**

The biggest learning moment for me was not a technical one — it was when Wooden Maps showed up at #2 for the high-energy metal user. I had spent time carefully designing the weights and was pretty confident the system made sense. Then I ran that edge case profile and a quiet folk ballad ended up second on a list meant for someone who wanted intense, heavy music. It was a genuinely humbling moment. The code was not broken. The math was correct. The system did exactly what I told it to do — it found the only melancholic song in the catalog and rewarded it. But the result was completely wrong by any human standard. That gap between "technically correct" and "actually useful" was something I had read about in the research but never really felt until I saw it in my own output.

Using AI tools throughout this project was genuinely helpful, but it required a lot of active involvement to stay honest. When I asked for suggestions on scoring logic or dataset ideas, the responses were fast and well-structured. But I noticed pretty quickly that the suggestions were confident even when they were generic. The weight values I was given as "a good starting point" turned out to favor genre so heavily that it created a filter bubble — which the AI did not flag as a problem, because it was not running the experiments. I had to actually test the system, observe the Gym Hero anomaly, run the weight-shift experiment, and then go back and question the original weights myself. The tools accelerated the work, but the judgment calls had to come from me. Any time I accepted a suggestion without testing it, I found a gap later.

What surprised me most was how quickly a list of five songs started to feel like a real recommendation, even though the algorithm underneath is just arithmetic. When the system returned Sunrise City, Gym Hero, and Rooftop Lights for a happy-pop user, it felt right — it felt like something a music app would actually suggest. I had to remind myself that the system has no idea what any of these songs actually sound like. It has never heard them. It is just comparing numbers in a spreadsheet. That gap between the feeling of intelligence and the reality of the mechanism is something I will probably think about every time I look at a Spotify recommendation from now on.

If I extended this project, the first thing I would try is adding a genre family map — a simple dictionary that groups related genres together so "indie pop" earns partial credit against "pop" rather than zero. That one change would fix the most visible bias without complicating the scoring logic. After that, I would want to let users rate the recommendations after seeing them, and use those ratings to adjust the weights over time. Even a basic version of that feedback loop would turn VibeFinder from a static formula into something that actually learns — and it would give me a much better sense of whether my weight choices were right or just lucky.
