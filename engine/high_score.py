import json
from pathlib import Path


class HighScoreStore:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> int:
        if not self.file_path.exists():
            return 0

        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
            return int(raw.get("high_score", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            return 0

    def save_if_higher(self, score: int) -> int:
        current = self.load()
        if score <= current:
            return current

        payload = {"high_score": int(score)}
        self.file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return int(score)
