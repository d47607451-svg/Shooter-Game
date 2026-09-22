# Shooter Game

A simple 2D shooter game built with **Pygame**.

## Features
- Player-controlled spaceship with keyboard and mouse shooting.
- Enemies spawn from the top and move downwards.
- Score tracking for hits and missed enemies.
- Background music and sound effects (optional).
- Basic win/lose conditions.

## Prerequisites
- Python 3.8+ installed on your system.
- **Pygame** library.

## Installation
```bash
# (Optional) Create a virtual environment
python -m venv venv
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Game
```bash
python shooter_game.py
```

The game will attempt to load the following assets from the project folder. If any are missing, the game will still run with placeholders:
- `galaxy.jpg` – background image
- `space.ogg` – background music
- `fire.ogg` – shooting sound
- `rocket.png` – player sprite
- `ufo.png` – enemy sprite

## License
This project is licensed under the MIT License – see the `LICENSE` file for details.

