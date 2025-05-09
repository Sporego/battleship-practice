import sys
import random
from enum import Enum

# Constants:
class CellState(Enum):
    WATER = "~"
    SHIP = "S"
    HIT = "X"
    MISS = "O"

class Ship:
    def __init__(self, config = None):
        config = config or {}
        self.origin = config.get("origin", (0,0))
        self.length = config.get("length", 3)
        self.orientation = config.get("orientation", 'H')
        self.hit_cells = set()
        self.cells = self.calculate_cells()

        if None in (self.origin, self.length, self.orientation):
            raise ValueError("Ship must have origin, length, and orientation")
    
    def calculate_cells(self):
        delta_row, delta_col = (0,1) if self.orientation == 'H' else (1,0)
        return [(self.origin[0] + i * delta_row, self.origin[1] + i * delta_col) for i in range(self.length)]
    
    def register_hit(self,pos):
        if pos in self.cells:
            self.hit_cells.add(pos)

    def is_sunk(self):
        return set(self.cells) == self.hit_cells


class Board:
    def __init__(self, config=None):
        config = config or {}
        self.length = config.get("length", 10)
        self.grid = [[CellState.WATER for _ in range(self.length)] for _ in range(self.length)]
        self.ships = []
        self.cell_to_ship = {}
    
    def place_ship(self, ship):
        for r, c in ship.cells:
            if not (0 <= r < self.length and 0 <= c < self.length):
                raise ValueError("Ship goes out of bounds.")
            if self.grid[r][c] != CellState.WATER:
                raise ValueError(f"Cell ({r}, {c}) is already occupied.")
        for r, c in ship.cells:
            self.grid[r][c] = CellState.SHIP
            self.cell_to_ship[(r, c)] = ship

        self.ships.append(ship)
    
    def attack(self, r, c):
        current = self.grid[r][c]
        if current == CellState.WATER:
            self.grid[r][c] = CellState.MISS
            return "Miss"
        elif current == CellState.SHIP:
            self.grid[r][c] = CellState.HIT
            ship = self.cell_to_ship[(r, c)]
            ship.register_hit((r, c))
            return "Hit and sunk!" if ship.is_sunk() else "Hit"
        else:
            return "Already tried"

class Player:
    def __init__(self, config=None):
        config = config or {}
        self.is_human = config.get("is_human", True)
        self.board = config.get("board", Board())

class GameController:
    def __init__(self, config=None):
        config = config or {}
        self.player1 = config.get("player1", Player())
        self.player2 = config.get("player2", Player())

    def cpu_attack(self, opponent):
        board = opponent.board
        while True:
            r = random.randint(0, board.length - 1)
            c = random.randint(0, board.length - 1)
            if board.grid[r][c] not in [CellState.HIT, CellState.MISS]:
                result = board.attack(r, c)
                print(f"CPU attacks ({r}, {c}) → {result}")
                return

    def run(self):
        print("Starting game!\n")
        self.player1.board.place_ship(Ship())
        self.player2.board.place_ship(Ship())

        def print_board(board, hide_ships=True):
            for row in board.grid:
                display = [
                    CellState.WATER.value if hide_ships and cell == CellState.SHIP else cell.value
                    for cell in row
                ]
                print(" ".join(display))
            print()

        while True:
            print("\nYour view of the enemy board:")
            print_board(self.player2.board, hide_ships=True)

            print("Your board:")
            print_board(self.player1.board, hide_ships=False)

            try:
                coords = input("Enter attack coordinates (row col): ")
                row, col = map(int, coords.strip().split())
                result = self.player2.board.attack(row, col)
                print(result)

                if all(s.is_sunk() for s in self.player2.board.ships):
                    print("You won!")
                    break

                self.cpu_attack(self.player1)

                if all(s.is_sunk() for s in self.player1.board.ships):
                    print("CPU won!")
                    break

            except Exception as e:
                print(f"Invalid input: {e}")

def main():
    controller = GameController()
    controller.run()

if __name__ == "__main__":
    main()