# Matthew's Mini Town

A simple 2D procedural town game prototype.

## What it does

- Creates a random town map with roads, trees, buildings, and NPC people
- Starts player at A and goal at B
- Move with arrow keys or WASD
- Press R to generate a new town seed

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
