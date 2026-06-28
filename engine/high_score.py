import json
from pathlib import Path


class HighScoreStore:
    """Persist and retrieve the best score across game sessions.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self, file_path: str):
        """Store the filesystem path used for high-score reads and writes.

        Args:
            file_path: Target path for persistent high score JSON data.

        Returns:
            None.
        """
        self.file_path = Path(file_path)

    def load(self) -> int:
        """Load current high score from disk, returning zero when unavailable.

        Args:
            None.

        Returns:
            int: Stored high score, or 0 when file is missing/invalid.
        """
        if not self.file_path.exists():
            return 0

        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
            return int(raw.get("high_score", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            return 0

    def save_if_higher(self, score: int) -> int:
        """Persist a new score only when it beats the stored high score.

        Args:
            score: Newly achieved score for the current run.

        Returns:
            int: The resulting high score after conditional persistence.
        """
        current = self.load()
        if score <= current:
            return current

        payload = {"high_score": int(score)}
        self.file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return int(score)
