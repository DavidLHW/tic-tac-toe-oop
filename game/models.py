from enum import Enum
from typing import List, Optional, Any

import config as settings
from game.errors import PositionAlreadyTaken, PositionDoesNotExist, GameOver, GameError


class GameState(str, Enum):
    """Object representing state of the game"""

    LIVE = "live"
    DRAW = "draw"
    WIN = "win"


class PlayerEnum(str, Enum):
    """Object representing number of players.

    To add more players, simply append to the object attribute.
    """

    first = {"index": 1, "mark": "X"}
    second = {"index": 2, "mark": "O"}

    @classmethod
    def list_marks(cls):
        """Returns a list of player marks."""
        return list(map(lambda c: eval(c)["mark"], cls))

    @classmethod
    def list_indices(cls):
        """Returns a list of player indices."""
        return list(map(lambda c: eval(c)["index"], cls))

    @classmethod
    def list_values(cls):
        """Returns a list of player enum values."""
        return list(map(lambda c: eval(c), cls))

    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))


class Player:
    name: str = ""
    mark: str = ""

    def __init__(self, name: str, mark: str) -> None:
        self.name = name
        self.mark = mark

    def ask_for_input(self):
        player_input = input(
            settings.ASK_INPUT_TEXT.format(current_player=self.name, mark=self.mark)
        )
        return player_input

    def retry_input(self, error: GameError, **kwargs: Any) -> str:
        player_input = None
        if isinstance(error, PositionAlreadyTaken):
            previous_player = kwargs["previous_player"]
            player_input = input(
                error.message.format(
                    current_player=self.name,
                    previous_player=previous_player.name,
                    mark=previous_player.mark,
                )
            )
        elif isinstance(error, PositionDoesNotExist):
            player_input = input(error.message.format(current_player=self.name))
        return player_input

    @staticmethod
    def rotate_players(players: List["Player"]) -> List["Player"]:
        "Moves the first player to the back of the turn queue."
        return players[1:] + [players[0]]


class Board:
    """Represents a tic-tac-toe game board.

    Attributes:
        `state`: current state of the game, starts with player 1.
        `size`: length and breadth of the game board.
        `grid`: nested array representing the current state of the game board.
        `current_player`: current player of this turn.
    """

    state: GameState = GameState.LIVE
    size: int = 0
    grid: List[List[str]] = [[]]
    current_player: Player = None

    def __init__(self, size: int) -> None:
        self._validate_size(size)
        self.size = size
        print(f"Prepare a {size}x{size} board …")
        # setting up initial board
        self.grid = [[settings.BLANK] * size for _ in range(size)]
        self.print_grid()

    @classmethod
    def setup_board(cls):
        size = input("Enter the board size: ")
        return cls(int(size))

    def make_move(self, row: int, col: int) -> None:
        self.set_grid(row, col)
        self.print_grid()
        return

    def set_grid(self, row: int, col: int) -> None:
        """Updates `grid` whenever a player moves.

        Args:
        row: x-coordinate of the new position to mark. This value is always int and > 0.
        col: y-coordinate of the new position to mark. This value is always int and > 0.
        """
        i = row - 1
        j = col - 1
        if i < 0 or j < 0:
            raise PositionDoesNotExist

        if i >= self.size or j >= self.size:
            raise PositionDoesNotExist

        if self.grid[i][j] != settings.BLANK:
            raise PositionAlreadyTaken

        self.grid[i][j] = self.current_player.mark
        return

    def evaluate_board(self) -> None:
        """Checks board state to see if there are any winners.

        Raises `GameError` if board is unplayable and returns None otherwise.
        """
        if self._has_winner():
            self.state = GameState.WIN
            raise GameOver
        elif not self._can_move():
            self.state = GameState.DRAW
            raise GameOver
        return

    def print_grid(self) -> Optional[List[List[str]]]:
        """Prints Grid into terminal."""
        for row in self.grid:
            print(" ".join(row))
        # add empty line
        print()

    def _can_move(self) -> bool:
        """Checks if `board` has empty spaces."""
        return any(settings.BLANK in row for row in self.grid)

    def _has_winner(self) -> bool:
        """Checks if `board` has `win_length`-in-a-row of any player's mark."""
        if self._has_win_length_horizontal():
            return True
        if self._has_win_length_vertical():
            return True
        if self._has_win_length_diagonal():
            return True

    def _has_win_length_horizontal(self) -> bool:
        """Checks if `board` has any winning position horizontally."""
        for row in self.grid:
            if self._has_consecutive_win_length(row):
                return True
        return False

    def _has_win_length_vertical(self) -> bool:
        """Checks if `board` has any winning position vertically."""
        for col in zip(*self.grid):
            if self._has_consecutive_win_length(col):
                return True
        return False

    def _has_win_length_diagonal(self) -> bool:
        """Checks if `board` has any winning position diagonally."""
        forward_diagonals = self._get_forward_diagonals()
        backward_diagonals = self._get_backward_diagonals()
        diagonals = forward_diagonals + backward_diagonals
        for diagonal in diagonals:
            if len(diagonal) < settings.WIN_LENGTH:
                continue
            if self._has_consecutive_win_length(diagonal):
                return True
        return False

    def _has_consecutive_win_length(self, target: List[str]) -> bool:
        """Checks if `target` has `WIN_LENGTH`-in-a-row of the same player mark."""
        # `count_arr` keeps track of consecutive count of each player's mark
        marks = PlayerEnum.list_marks()
        count_arr = [0] * len(marks)
        for elem in target:
            if elem == settings.BLANK:
                # reset count for all players
                count_arr = [0] * len(marks)
                continue
            elif elem in marks:
                current_player_count = count_arr[marks.index(elem)] + 1
                # reset count for other players
                count_arr = [0] * len(marks)
                count_arr[marks.index(elem)] = current_player_count

            if max(count_arr) >= settings.WIN_LENGTH:
                return True
        return False

    def _get_forward_diagonals(self) -> List[str]:
        """Transform `board` grid to nested array representing forward diagonals.
        https://stackoverflow.com/a/31373955/190597
        >>> L = [[ 0,  1,  2],
                [ 3,  4,  5],
                [ 6,  7,  8]]

        >>> _get_forward_diagonals(L)
        [[0], [3, 1], [6, 4, 2], [7, 5], [8]]
        """
        L = self.grid
        h, w = len(L), len(L[0])
        return [
            [L[p - q][q] for q in range(max(p - h + 1, 0), min(p + 1, w))]
            for p in range(h + w - 1)
        ]

    def _get_backward_diagonals(self) -> List[str]:
        """Transform `board` grid to nested array representing backward diagonals.
        >>> L = [[ 0,  1,  2],
                [ 3,  4,  5],
                [ 6,  7,  8]]

        >>> _get_backward_diagonals(L)
        [[6], [3, 7], [0, 4, 8], [1, 5], [2]]
        """
        L = self.grid
        h, w = len(L), len(L[0])
        return [
            [L[h - p + q - 1][q] for q in range(max(p - h + 1, 0), min(p + 1, w))]
            for p in range(h + w - 1)
        ]

    @staticmethod
    def _validate_size(size: int) -> None:
        """Validates board size"""
        if (size not in settings.ALLOWED_SIZE) or (type(size) is not int):
            raise GameError(message="Board size invalid!")
