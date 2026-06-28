from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """Shared lifecycle contract for pluggable game subsystems.

    Args:
        None.

    Returns:
        None.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Prepare runtime state for this engine.

        Args:
            None.

        Returns:
            None.
        """

    @abstractmethod
    def execute(self) -> None:
        """Run one tick/frame of engine work.

        Args:
            None.

        Returns:
            None.
        """
