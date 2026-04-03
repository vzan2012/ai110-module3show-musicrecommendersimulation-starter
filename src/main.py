"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs

DIVIDER = "-" * 52


def print_profile(user_prefs: dict) -> None:
    """Print the active user profile in a readable block."""
    print(f"\n{'[ USER PROFILE ]':^52}")
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
    """Load songs, score them against the user profile, and print results."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = {
        "genre":               "pop",
        "mood":                "happy",
        "target_energy":       0.80,
        "target_valence":      0.78,
        "target_acousticness": 0.20,
    }

    print_profile(user_prefs)
    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(recommendations)


if __name__ == "__main__":
    main()
