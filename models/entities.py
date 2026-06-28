from dataclasses import dataclass


@dataclass
class PlayerModel:
    """Logical player actor stored in tile-space coordinates.

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
    color: tuple[int, int, int] = (43, 88, 191)
    hat_color: tuple[int, int, int] | None = (52, 73, 94)

    @property
    def position(self) -> tuple[int, int]:
        """Expose current tile coordinate as an `(x, y)` tuple.

        Args:
            None.

        Returns:
            tuple[int, int]: Current player tile position.
        """
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        """Move the player immediately to a new tile coordinate.

        Args:
            x: Destination tile x position.
            y: Destination tile y position.

        Returns:
            None.
        """
        self.x = x
        self.y = y


@dataclass(frozen=True)
class CollectibleModel:
    """Immutable collectible item placed on a walkable tile.

    Args:
        x: Tile x position.
        y: Tile y position.
        color: RGB color used for rendering.

    Returns:
        None.
    """

    x: int
    y: int
    color: tuple[int, int, int] = (240, 198, 74)

    @property
    def position(self) -> tuple[int, int]:
        """Expose collectible tile position as an `(x, y)` tuple.

        Args:
            None.

        Returns:
            tuple[int, int]: Current collectible tile position.
        """
        return self.x, self.y
