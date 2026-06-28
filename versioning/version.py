from datetime import datetime
from pathlib import Path
import subprocess


class GameVersion:
    """Build a readable version string in the format major.date.iteration.

    Args:
        None.

    Returns:
        None.
    """

    MAJOR = 1

    @staticmethod
    def _today_stamp() -> str:
        """Return current date stamp as YYYYMMDD.

        Args:
            None.

        Returns:
            str: Date stamp suitable for version display.
        """
        return datetime.now().strftime("%Y%m%d")

    @staticmethod
    def _build_iteration() -> int:
        """Resolve build iteration from git commit count with a safe fallback.

        Args:
            None.

        Returns:
            int: Commit-count-based build iteration, or 1 when unavailable.
        """
        repo_root = Path(__file__).resolve().parent.parent
        try:
            completed = subprocess.run(
                ["git", "-C", str(repo_root), "rev-list", "--count", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            return max(1, int(completed.stdout.strip()))
        except Exception:
            return 1

    @classmethod
    def current(cls) -> str:
        """Return current game version string as 1.YYYYMMDD.BUILD.

        Args:
            None.

        Returns:
            str: Current version label for display and packaging.
        """
        return f"{cls.MAJOR}.{cls._today_stamp()}.{cls._build_iteration()}"
