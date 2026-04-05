# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0** - a simple music recommender that scores songs based on how well they match what the user likes.

---

## 2. Intended Use

VibeFinder is built and suggests songs from a small catalog based on five user preferences: genre, mood, energy, valence, and acousticness. It is not intended for real-world music apps, production deployments, or catalogs larger than 50 songs.

---

## 3. How the Model Works

Every song gets scored against the user's preferences across five categories. Genre is worth the most points - a genre match gives a big head start. Mood is second. Energy, valence (happy vs dark), and acousticness (organic vs electronic) are scored by proximity - the closer to the user's target, the more points. Every song gets a total out of 5.75, and the top five are returned with a breakdown of where the points came from.

---

## 4. Data

18 songs across 13 genres and 12 moods, stored in a CSV file. Eight songs were added to the original 10 to improve diversity.

---

## 5. Strengths

Works well when the user's genre has at least two songs in the catalog and their mood is clearly represented. For profiles like "chill lofi" or "intense rock," the top result is a genuine best fit.

---

## 6. Limitations and Bias

Genre carries 35% of the total score (2.0 out of 5.75) as a strict all-or-nothing match - "indie pop" and "metal" both score zero against a "pop" user, even though indie pop is much closer. This traps users inside their stated genre and was confirmed by experiment: halving the genre weight caused a mood-matched cross-genre song to correctly outrank a same-genre but wrong-mood song.

Other limitations:

- **Conflicting preferences are invisible.** A user wanting high energy + melancholic mood got a quiet folk ballad at #2 - the mood matched but the energy was completely wrong. Features are scored independently with no way to detect contradictions.
- **Cold start collapses confidence.** When the genre is not in the catalog, the top four results cluster within 0.16 points - rankings become near-arbitrary.
- **Thin catalog.** 13 of 18 genres have one song each, so #1 is usually predetermined before scoring begins.

---

## 7. Evaluation

Six profiles were tested - three normal and three adversarial edge cases:

| Profile                                | Genre      | Mood        | Energy | Type        |
| -------------------------------------- | ---------- | ----------- | ------ | ----------- |
| High-Energy Pop                        | pop        | happy       | 0.90   | Normal      |
| Chill Lofi                             | lofi       | chill       | 0.38   | Normal      |
| Deep Intense Rock                      | rock       | intense     | 0.92   | Normal      |
| Conflicting: High Energy + Melancholic | metal      | melancholic | 0.92   | Adversarial |
| Unknown Genre (Cold Start)             | bossa nova | romantic    | 0.48   | Adversarial |
| All-Middle / Neutral                   | jazz       | relaxed     | 0.50   | Adversarial |

The normal profiles all returned sensible top results. The adversarial profiles exposed the three limitations above. A weight-shift experiment (genre ÷2, energy ×2) showed that #1 never changed - only #2 and #3 shuffled, confirming that catalog depth locks the top spot regardless of weights.

---

## 8. Future Work

1. Replace binary genre matching with a similarity score - "indie pop" should earn partial credit against "pop," not zero.
2. Add conflict detection - flag when mood and energy preferences point in opposite directions and reduce the weight of the contradicting feature.
3. Expand the catalog to at least 5 songs per genre so rankings below #1 carry real information.

---

## 9. Personal Reflection

The biggest learning moment was when Wooden Maps - a quiet folk ballad - ranked #2 for a user who wanted intense, heavy metal music. The code was correct, the math was right, but the result was completely wrong by any human standard. That gap between "technically correct" and "actually useful" is something I had read about but never really felt until I saw it in my own output.

Using AI tools sped up the work but required constant verification. The weight suggestions I received were confident but generic - the genre dominance bias only became visible once I ran the experiments myself. The tools helped me build faster; the judgment had to come from me.

The most surprising thing was how quickly five ranked songs felt like a real recommendation even though the system has never heard any music. It is just arithmetic on a spreadsheet. That gap between the feeling of intelligence and the reality of the mechanism will change how I think about Spotify and YouTube recommendations going forward. Every weight in their system is also an opinion - just learned from millions of users instead of chosen by hand.
