"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs

DIVIDER = "-" * 52

# --- User profiles --------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre":               "pop",
        "mood":                "happy",
        "target_energy":       0.90,
        "target_valence":      0.82,
        "target_acousticness": 0.10,
    },
    "Chill Lofi": {
        "genre":               "lofi",
        "mood":                "chill",
        "target_energy":       0.38,
        "target_valence":      0.58,
        "target_acousticness": 0.80,
    },
    "Deep Intense Rock": {
        "genre":               "rock",
        "mood":                "intense",
        "target_energy":       0.92,
        "target_valence":      0.45,
        "target_acousticness": 0.08,
    },
    # --- Adversarial / edge-case profiles ---
    "Conflicting: High Energy + Melancholic": {
        # High energy (0.92) but dark/sad mood — tests whether energy
        # proximity pulls angry/metal songs up even though mood is wrong
        "genre":               "metal",
        "mood":                "melancholic",
        "target_energy":       0.92,
        "target_valence":      0.22,
        "target_acousticness": 0.15,
    },
    "Unknown Genre (Cold Start)": {
        # Genre 'bossa nova' is not in the catalog — both categorical
        # scores collapse to 0; system must rank on numerics alone
        "genre":               "bossa nova",
        "mood":                "romantic",
        "target_energy":       0.48,
        "target_valence":      0.74,
        "target_acousticness": 0.65,
    },
    "All-Middle / Neutral": {
        # Every numeric preference set to 0.5 — tests whether the system
        # produces a meaningful ranking or just returns arbitrary songs
        "genre":               "jazz",
        "mood":                "relaxed",
        "target_energy":       0.50,
        "target_valence":      0.50,
        "target_acousticness": 0.50,
    },
}

# --------------------------------------------------------------------------


def print_profile(label: str, user_prefs: dict) -> None:
    """Print the active user profile in a readable block."""
    print(f"\n{f'[ {label.upper()} ]':^52}")
    print(DIVIDER)
    print(f"  Genre      : {user_prefs['genre']}")
    print(f"  Mood       : {user_prefs['mood']}")
    print(f"  Energy     : {user_prefs['target_energy']}")
    print(f"  Valence    : {user_prefs['target_valence']}")
    print(f"  Acousticness: {user_prefs['target_acousticness']}")
    print(DIVIDER)


def print_recommendations(recommendations: list) -> None:
    """Print ranked recommendations with scores and reasons."""
    print(f"\n{'[ TOP RECOMMENDATIONS ]':^52}")
    print(DIVIDER)
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']}  -  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"       Score: {score:.2f} / 5.75")
        print(f"       Why  : {reasons}")
        print()
    print(DIVIDER)


def main() -> None:
    """Run all profiles and print ranked recommendations for each."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for label, user_prefs in PROFILES.items():
        print_profile(label, user_prefs)
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(recommendations)


if __name__ == "__main__":
    main()
