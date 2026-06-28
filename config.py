from configparser import ConfigParser
from pathlib import Path

from engine.constants import (
    COLLECTIBLE_POINTS,
    COMBO_MULTIPLIER_CAP,
    COMBO_WINDOW_SECONDS,
    FINISH_BONUS_POINTS,
    FINISH_TIME_TARGET_SECONDS,
    NPC_MOVE_CHANCE,
    NPC_MOVE_INTERVAL_MS,
    SUB_TILE_STEPS,
)


class GameConfig:
    """Static config reader with file-change detection for runtime tuning.

    Args:
        None.

    Returns:
        None.
    """

    _config_path = Path(__file__).resolve().parent / "config.ini"
    _last_mtime_ns: int | None = None

    initial_difficulty = 55
    initial_wind_speed = 35
    collectible_points = COLLECTIBLE_POINTS
    combo_window_seconds = COMBO_WINDOW_SECONDS
    combo_multiplier_cap = COMBO_MULTIPLIER_CAP
    finish_time_target_seconds = FINISH_TIME_TARGET_SECONDS
    finish_bonus_points = FINISH_BONUS_POINTS

    sub_tile_steps = SUB_TILE_STEPS
    npc_move_interval_ms = NPC_MOVE_INTERVAL_MS
    npc_move_chance = NPC_MOVE_CHANCE
    avatar_idle_interval_ms = 280
    avatar_contact_slowdown_ms = 120
    hud_right_margin_px = 12
    hud_version_row_y = 36
    hud_win_row_y = 58

    @classmethod
    def initialize(cls) -> None:
        """Load config once at startup, creating defaults if missing.

        Args:
            None.

        Returns:
            None.
        """
        cls._ensure_file_exists()
        cls._load()

    @classmethod
    def reload_if_changed(cls) -> bool:
        """Reload config when file mtime changes and report whether reload happened.

        Args:
            None.

        Returns:
            bool: True when config values were reloaded; otherwise False.
        """
        cls._ensure_file_exists()

        try:
            mtime_ns = cls._config_path.stat().st_mtime_ns
        except OSError:
            return False

        if cls._last_mtime_ns is not None and mtime_ns == cls._last_mtime_ns:
            return False

        cls._load()
        return True

    @classmethod
    def _ensure_file_exists(cls) -> None:
        """Create a default ini file only when config is missing.

        Args:
            None.

        Returns:
            None.
        """
        if cls._config_path.exists():
            return

        default_ini = (
            "[display]\n"
            "hud_right_margin_px = 12\n"
            "hud_version_row_y = 36\n"
            "hud_win_row_y = 58\n\n"
            "[gameplay]\n"
            "initial_difficulty = 55\n"
            "initial_wind_speed = 35\n"
            "collectible_points = 10\n"
            "combo_window_seconds = 10\n"
            "combo_multiplier_cap = 5\n"
            "finish_time_target_seconds = 120\n"
            "finish_bonus_points = 100\n\n"
            "[movement]\n"
            "sub_tile_steps = 10\n"
            "npc_move_interval_ms = 420\n"
            "npc_move_chance = 0.65\n"
            "avatar_idle_interval_ms = 280\n"
            "avatar_contact_slowdown_ms = 120\n"
        )
        cls._config_path.write_text(default_ini, encoding="utf-8")

    @classmethod
    def _load(cls) -> None:
        """Parse ini values and keep safe defaults when entries are missing/invalid.

        Args:
            None.

        Returns:
            None.
        """
        parser = ConfigParser()

        try:
            parser.read(cls._config_path, encoding="utf-8")
            cls._last_mtime_ns = cls._config_path.stat().st_mtime_ns
        except OSError:
            return

        cls.initial_difficulty = cls._get_int(
            parser, "gameplay", "initial_difficulty", cls.initial_difficulty, 0, 100
        )
        cls.hud_right_margin_px = cls._get_int(
            parser,
            "display",
            "hud_right_margin_px",
            cls.hud_right_margin_px,
            0,
            300,
        )
        cls.hud_version_row_y = cls._get_int(
            parser,
            "display",
            "hud_version_row_y",
            cls.hud_version_row_y,
            0,
            300,
        )
        cls.hud_win_row_y = cls._get_int(
            parser,
            "display",
            "hud_win_row_y",
            cls.hud_win_row_y,
            0,
            300,
        )
        cls.initial_wind_speed = cls._get_int(
            parser, "gameplay", "initial_wind_speed", cls.initial_wind_speed, 0, 100
        )
        cls.collectible_points = cls._get_int(
            parser, "gameplay", "collectible_points", cls.collectible_points, 1, 1000
        )
        cls.combo_window_seconds = cls._get_float(
            parser,
            "gameplay",
            "combo_window_seconds",
            cls.combo_window_seconds,
            0.5,
            120.0,
        )
        cls.combo_multiplier_cap = cls._get_int(
            parser,
            "gameplay",
            "combo_multiplier_cap",
            cls.combo_multiplier_cap,
            1,
            50,
        )
        cls.finish_time_target_seconds = cls._get_float(
            parser,
            "gameplay",
            "finish_time_target_seconds",
            cls.finish_time_target_seconds,
            1.0,
            3600.0,
        )
        cls.finish_bonus_points = cls._get_int(
            parser,
            "gameplay",
            "finish_bonus_points",
            cls.finish_bonus_points,
            0,
            100000,
        )

        cls.sub_tile_steps = cls._get_int(
            parser, "movement", "sub_tile_steps", cls.sub_tile_steps, 1, 60
        )
        cls.npc_move_interval_ms = cls._get_int(
            parser,
            "movement",
            "npc_move_interval_ms",
            cls.npc_move_interval_ms,
            50,
            5000,
        )
        cls.npc_move_chance = cls._get_float(
            parser, "movement", "npc_move_chance", cls.npc_move_chance, 0.0, 1.0
        )
        cls.avatar_idle_interval_ms = cls._get_int(
            parser,
            "movement",
            "avatar_idle_interval_ms",
            cls.avatar_idle_interval_ms,
            50,
            5000,
        )
        cls.avatar_contact_slowdown_ms = cls._get_int(
            parser,
            "movement",
            "avatar_contact_slowdown_ms",
            cls.avatar_contact_slowdown_ms,
            0,
            2000,
        )

    @classmethod
    def _get_int(
        cls,
        parser: ConfigParser,
        section: str,
        key: str,
        default: int,
        minimum: int,
        maximum: int,
    ) -> int:
        """Read and clamp integer config values with fallback protection.

        Args:
            parser: Parsed ini document.
            section: Ini section name.
            key: Section key name.
            default: Fallback value when parse fails.
            minimum: Lower clamp bound.
            maximum: Upper clamp bound.

        Returns:
            int: Parsed and clamped integer value.
        """
        try:
            value = parser.getint(section, key)
        except Exception:
            return default
        return max(minimum, min(maximum, value))

    @classmethod
    def _get_float(
        cls,
        parser: ConfigParser,
        section: str,
        key: str,
        default: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Read and clamp float config values with fallback protection.

        Args:
            parser: Parsed ini document.
            section: Ini section name.
            key: Section key name.
            default: Fallback value when parse fails.
            minimum: Lower clamp bound.
            maximum: Upper clamp bound.

        Returns:
            float: Parsed and clamped float value.
        """
        try:
            value = parser.getfloat(section, key)
        except Exception:
            return default
        return max(minimum, min(maximum, value))
