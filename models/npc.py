from dataclasses import dataclass


@dataclass
class NpcModel:
    """Logical non-player actor stored in tile-space coordinates.

    Args:
        x: Initial tile x position.
        y: Initial tile y position.
        color: RGB color used for rendering.
        hat_color: Optional RGB hat color.

    Returns:
        None.
    """

    x: int
    y: int
    color: tuple[int, int, int] = (165, 105, 189)
    hat_color: tuple[int, int, int] | None = None

    @property
    def position(self) -> tuple[int, int]:
        """Expose current tile coordinate as an `(x, y)` tuple.

        Args:
            None.

        Returns:
            tuple[int, int]: Current NPC tile position.
        """
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        """Move this NPC immediately to a new tile coordinate.

        Args:
            x: Destination tile x position.
            y: Destination tile y position.

        Returns:
            None.
        """
        self.x = x
        self.y = y
