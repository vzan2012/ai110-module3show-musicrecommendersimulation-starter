"""Music recommender simulation — scoring and ranking logic."""

import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float
    target_acousticness: float


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score one song against a user preference dict.

    Returns a tuple of:
      - score  : float, 0.00 – 5.75 (higher is better)
      - reasons: list of strings explaining each contributing factor

    Points breakdown (max 5.75):
      +2.00  genre match
      +1.50  mood match
      +1.00  energy proximity   (1 - |target - song|)
      +0.75  valence proximity
      +0.50  acousticness proximity
    """
    score = 0.0
    reasons = []

    # Categorical features — binary match
    if song["genre"] == user_prefs["genre"]:
        score += 2.00
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    if song["mood"] == user_prefs["mood"]:
        score += 1.50
        reasons.append(f"mood match: {song['mood']} (+1.5)")

    # Numeric features — proximity scoring (closer = more points)
    energy_pts = 1.00 * (1 - abs(user_prefs["target_energy"] - song["energy"]))
    score += energy_pts
    reasons.append(f"energy similarity: {energy_pts:.2f}/1.00")

    valence_pts = 0.75 * (
        1 - abs(user_prefs["target_valence"] - song["valence"])
    )
    score += valence_pts
    reasons.append(f"valence similarity: {valence_pts:.2f}/0.75")

    acoustic_pts = 0.50 * (
        1 - abs(user_prefs["target_acousticness"] - song["acousticness"])
    )
    score += acoustic_pts
    reasons.append(f"acousticness similarity: {acoustic_pts:.2f}/0.50")

    return round(score, 4), reasons


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return them as a list of dicts."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """
    Score and rank all songs against user_prefs.

    Returns the top-k songs as (song_dict, score, explanation) tuples,
    sorted by score descending.
    """
    def build_entry(song: Dict) -> Tuple[Dict, float, str]:
        """Score one song and pack it into a (song, score, reasons_string) tuple."""
        s, reasons = score_song(user_prefs, song)
        return song, s, " | ".join(reasons)

    return sorted(
        (build_entry(song) for song in songs),
        key=lambda entry: entry[1],
        reverse=True,
    )[:k]


class Recommender:
    """OOP interface around the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _song_to_dict(self, song: Song) -> Dict:
        """Convert a Song dataclass instance to a plain dict for scoring."""
        return {
            "id":           song.id,
            "title":        song.title,
            "artist":       song.artist,
            "genre":        song.genre,
            "mood":         song.mood,
            "energy":       song.energy,
            "tempo_bpm":    song.tempo_bpm,
            "valence":      song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }

    def _user_to_dict(self, user: UserProfile) -> Dict:
        """Convert a UserProfile dataclass instance to a plain dict for scoring."""
        return {
            "genre":               user.favorite_genre,
            "mood":                user.favorite_mood,
            "target_energy":       user.target_energy,
            "target_valence":      user.target_valence,
            "target_acousticness": user.target_acousticness,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for this user."""
        user_dict = self._user_to_dict(user)
        scored = sorted(
            self.songs,
            key=lambda s: score_song(user_dict, self._song_to_dict(s))[0],
            reverse=True,
        )
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a reasons string for why song suits user."""
        _, reasons = score_song(self._user_to_dict(user), self._song_to_dict(song))
        return " | ".join(reasons)
