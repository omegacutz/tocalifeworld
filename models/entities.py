from dataclasses import dataclass


@dataclass
class PlayerModel:
    x: int
    y: int
    color: tuple[int, int, int] = (43, 88, 191)
    hat_color: tuple[int, int, int] | None = (52, 73, 94)

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@dataclass
class NpcModel:
    x: int
    y: int
    color: tuple[int, int, int] = (165, 105, 189)
    hat_color: tuple[int, int, int] | None = None

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@dataclass(frozen=True)
class CollectibleModel:
    x: int
    y: int
    color: tuple[int, int, int] = (240, 198, 74)

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y
