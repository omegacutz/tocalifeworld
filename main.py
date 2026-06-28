from engine import GameEngine


def main() -> None:
    """Start the game application.

    Args:
        None.

    Returns:
        None.
    """
    game = GameEngine()
    game.run()


if __name__ == "__main__":
    main()
