# Matthew's Mini Town

A simple 2D procedural town game prototype.

## How to play (Kid version)

1. Press Space to start.
2. You are the blue character at A.
3. Walk to B to finish the round.
4. Pick up yellow diamonds for points.
5. Pick up diamonds quickly to build a combo.
6. Press Esc to go back to the welcome screen.
7. Press R any time to generate a new town.

Tip: If you reach B in under 120 seconds, you get a bonus.

## What it does

- Creates a random town map with roads, trees, buildings, and NPC people
- Starts player at A and goal at B
- Move with arrow keys or WASD
- Press R to generate a new town seed
- Press Space to start, Esc to return to welcome screen
- Shows score, combo timer, and saved high score
- Includes moving NPCs, collectible pickups, and a difficulty slider
- Includes a wind slider that affects tree sway animation

## Setup (Windows)

1. Install Python 3.11+ from python.org
2. Open terminal in this folder
3. Install dependency:
   - pip install -r requirements.txt
4. Run game:
   - python main.py

## Unit tests

1. Install dev dependencies:
   - pip install -r requirements-dev.txt
2. Run tests:
   - python -m pytest -q

### Datum-style test pattern

- Tests use scenario lists with `pytest.mark.parametrize`.
- Pattern: "for each scenario, run the same assertions".
- Includes a dedicated Rumsfeld test module in `tests/test_rumsfeld.py`.

## Notes

- If `python` command is not found, enable Python in PATH during install.
