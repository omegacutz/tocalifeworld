from dataclasses import dataclass


@dataclass
class PlayerModel:
    x: int
    y: int
    color: tuple[int, int, int] = (43, 88, 191)

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

    def move_to(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@dataclass(frozen=True)
class NpcModel:
    x: int
    y: int
    color: tuple[int, int, int] = (240, 198, 74)

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y
