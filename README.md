# ♟️ Python Chess AI

An advanced Chess Game built with **Python** and **Pygame**, featuring a smart AI opponent powered by the **Minimax Algorithm** with **Alpha-Beta Pruning**.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [How to Play](#-how-to-play)
- [Project Structure](#-project-structure)
- [Technical Details](#-technical-details)
- [Author](#-author)

---

## 🧐 Overview

This project is a fully functional chess engine that allows a human player to compete against an Artificial Intelligence. The game includes a graphical user interface (GUI), move validation, and game state management (Check, Checkmate, Stalemate). The AI runs on a separate process using `multiprocessing` to ensure smooth UI performance while thinking.

---

## ✨ Features

- **🤖 Intelligent AI:**
  - Uses **Minimax Algorithm** with **Alpha-Beta Pruning** for efficiency.
  - **Move Ordering** optimization (prioritizes captures) to prune trees faster.
  - Adjustable difficulty levels (Search Depth).
- **🎮 Interactive GUI:**
  - Start Menu to select difficulty (**Easy**, **Medium**, **Hard**).
  - Move highlighting (valid moves, last move, check alerts).
  - Smooth piece animations.
- **⚙️ Complete Chess Logic:**
  - Valid move generation including pins and checks.
  - **Castling** (King-side & Queen-side).
  - **En Passant** captures.
  - **Pawn Promotion** (GUI selector for Human, Auto-Queen for AI).
  - Endgame detection (Checkmate & Stalemate).
- **🛠️ Tools:**
  - **Undo Move:** Press `Z` to undo the last move.
  - **Reset Game:** Press `R` to restart.

---

## 📥 Installation

1.  **Clone the repository (or download the files):**

    ```bash
    git clone [https://github.com/noran66/Chess_game.git](https://github.com/noran66/Chess_game.git)
    cd Chess_game
    ```

2.  **Install dependencies:**
    This project requires `pygame`.

    ```bash
    pip install pygame
    ```

3.  **Run the Game:**
    ```bash
    python main.py
    ```

---

## 🎮 How to Play

1.  **Start Screen:** Click on a difficulty level (**Easy**, **Medium**, or **Hard**) to begin.
2.  **Gameplay:**
    - Click on a white piece to select it (valid moves will be highlighted).
    - Click on a destination square to move.
3.  **Controls:**
    - **`Z` Key:** Undo the last move.
    - **`R` Key:** Reset the board and go back to the starting position.

---

## 📂 Project Structure

The project follows a modular architecture separating Logic, AI, and UI.

```text
Chess_Project/
│
├── main.py                # Entry point, Game Loop, GUI & Input handling
├── config.py              # Global constants (Screen size, Colors, Difficulty settings)
│
├── Engine/                # Game Logic Module
│   ├── gameState.py       # Stores board state, logs moves, checks rules
│   └── move.py            # Move class & Chess notation conversion
│
├── AI/                    # Artificial Intelligence Module
│   ├── moveFinder.py      # Minimax algorithm & Alpha-Beta Pruning implementation
│   └── evaluation.py      # Heuristic evaluation (Piece scores & Position tables)
│
└── images/                # Folder containing piece assets (.png files)

Technical Details:
--The Engine
Board Representation: 8x8 2D List.

Move Generation: Pseudo-legal moves are generated first, then filtered to remove moves that leave the King in check.

--The AI
Algorithm: NegaMax variant of Minimax.

Optimization:

Alpha-Beta Pruning: Cuts off search branches that are mathematically worse than previously found moves.

Move Ordering: Evaluates captures first (MVV-LVA logic) to maximize pruning.

Evaluation Function:

Calculates material difference.

Uses Piece-Square Tables to evaluate positional advantages (e.g., Knights in the center, Rooks on open files).

👤 Author
Developed by Noran

Language: Python 3.9.13

Year: 2025
```
