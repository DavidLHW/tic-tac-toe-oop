from unittest import mock
from typing import List

import config as settings
from tests.test_base import BaseTestCase
from game.models import Player, PlayerEnum, Board, GameState
from game.errors import PositionDoesNotExist, PositionAlreadyTaken, GameOver, GameError


class TestBoard(BaseTestCase):
    @mock.patch("game.models.print")
    @mock.patch("game.models.input")
    def test_setup_board(self, mock_input: mock.MagicMock, mock_print: mock.MagicMock):
        expected_total_print = 0
        count = 0
        for expected_size in self.size_test_cases:
            mock_input.return_value = expected_size
            if expected_size in settings.ALLOWED_SIZE:
                board = Board.setup_board()
                count += 1
                expected_total_print += expected_size + 2
                self.assertEqual(board.size, expected_size)
                self.assertEqual(
                    board.grid,
                    [[settings.BLANK] * expected_size for _ in range(expected_size)],
                )
                self.assertEqual(len(mock_print.mock_calls), expected_total_print)
                self.assertIn(
                    mock.call(f"Prepare a {expected_size}x{expected_size} board …"),
                    mock_print.mock_calls,
                )
                self.assertEqual(
                    mock_print.mock_calls.count(
                        mock.call(" ".join([settings.BLANK] * expected_size))
                    ),
                    expected_size,
                )
                self.assertEqual(mock_print.mock_calls.count(mock.call()), count)

    @mock.patch("game.models.Board._validate_size")
    @mock.patch("game.models.print")
    def test_set_grid_out_of_position(
        self,
        mock_print: mock.MagicMock,
        mock__validate_size: mock.MagicMock,
    ):
        board = Board(3)
        board.current_player = self.mock_players[0]
        expected_err_msg = PositionDoesNotExist.message
        with self.assertRaises(PositionDoesNotExist) as cm:
            board.set_grid(4, 4)
        err = cm.exception
        self.assertEqual(err.message, expected_err_msg)

    @mock.patch("game.models.Board._validate_size")
    @mock.patch("game.models.print")
    def test_set_grid_position_already_taken(
        self,
        mock_print: mock.MagicMock,
        mock__validate_size: mock.MagicMock,
    ):
        board = Board(3)
        board.current_player = self.mock_players[0]
        board.grid[0][0] = PlayerEnum.list_marks()[1]
        expected_err_msg = PositionAlreadyTaken.message
        with self.assertRaises(PositionAlreadyTaken) as cm:
            board.set_grid(1, 1)
        err = cm.exception
        self.assertEqual(err.message, expected_err_msg)

    @mock.patch("game.models.Board._validate_size")
    @mock.patch("game.models.print")
    def test_set_grid_empty_position(
        self,
        mock_print: mock.MagicMock,
        mock__validate_size: mock.MagicMock,
    ):
        board = Board(3)
        board.current_player = self.mock_players[0]
        board.set_grid(1, 1)
        self.assertEqual(board.grid[0][0], PlayerEnum.list_marks()[0])

    @mock.patch("game.models.Board._has_winner")
    @mock.patch("game.models.Board._can_move")
    @mock.patch("game.models.print")
    def test_evaluate_board_win(
        self,
        mock_print: mock.MagicMock,
        mock__can_move: mock.MagicMock,
        mock__has_winner: mock.MagicMock,
    ):
        mock__has_winner.return_value = True
        mock__can_move.return_value = True
        board = Board(3)
        expected_err_msg = GameOver.message
        with self.assertRaises(GameOver) as cm:
            board.evaluate_board()
        err = cm.exception
        self.assertEqual(err.message, expected_err_msg)
        self.assertEqual(board.state, GameState.WIN)

    @mock.patch("game.models.Board._has_winner")
    @mock.patch("game.models.Board._can_move")
    @mock.patch("game.models.print")
    def test_evaluate_board_continue(
        self,
        mock_print: mock.MagicMock,
        mock__can_move: mock.MagicMock,
        mock__has_winner: mock.MagicMock,
    ):
        mock__has_winner.return_value = False
        mock__can_move.return_value = True
        board = Board(3)
        board.evaluate_board()
        self.assertEqual(board.state, GameState.LIVE)

    @mock.patch("game.models.Board._has_winner")
    @mock.patch("game.models.Board._can_move")
    @mock.patch("game.models.print")
    def test_evaluate_board_draw(
        self,
        mock_print: mock.MagicMock,
        mock__can_move: mock.MagicMock,
        mock__has_winner: mock.MagicMock,
    ):
        mock__has_winner.return_value = True
        mock__can_move.return_value = False
        board = Board(3)
        expected_err_msg = GameOver.message
        with self.assertRaises(GameOver) as cm:
            board.evaluate_board()
        err = cm.exception
        self.assertEqual(err.message, expected_err_msg)
        self.assertEqual(board.state, GameState.WIN)

        mock__has_winner.return_value = False
        with self.assertRaises(GameOver) as cm:
            board.evaluate_board()
        err = cm.exception
        self.assertEqual(err.message, expected_err_msg)
        self.assertEqual(board.state, GameState.DRAW)

    @mock.patch("game.models.print")
    def test__can_move_is_moveable(self, mock_print: mock.MagicMock):
        board = Board(3)
        self.assertTrue(board._can_move())

    @mock.patch("game.models.print")
    def test__can_move_is_unmoveable(self, mock_print: mock.MagicMock):
        size = 3
        board = Board(size)
        board.grid = [[PlayerEnum.list_marks()[0]] * size for _ in range(size)]
        self.assertFalse(board._can_move())

    @mock.patch("game.models.print")
    def test__has_consecutive_win_length_is_passing(self, mock_print: mock.MagicMock):
        board = Board(3)
        len_win = settings.WIN_LENGTH
        consecutive_front = [[PlayerEnum.list_marks()[0]] * len_win][0] + [
            settings.BLANK
        ]
        consecutive_back = [settings.BLANK] + [[PlayerEnum.list_marks()[0]] * len_win][
            0
        ]
        consecutive_center = (
            [settings.BLANK]
            + [[PlayerEnum.list_marks()[0]] * len_win][0]
            + [settings.BLANK]
        )
        self.assertTrue(board._has_consecutive_win_length(consecutive_front))
        self.assertTrue(board._has_consecutive_win_length(consecutive_back))
        self.assertTrue(board._has_consecutive_win_length(consecutive_center))

    @mock.patch("game.models.print")
    def test__has_consecutive_win_length_is_failing(self, mock_print: mock.MagicMock):
        board = Board(3)
        less_than_len_win = (
            [settings.BLANK]
            + [[PlayerEnum.list_marks()[0]] * (settings.WIN_LENGTH - 1)][0]
            + [settings.BLANK]
        )
        alternating = (
            [settings.BLANK]
            + [PlayerEnum.list_marks()[0]]
            + [settings.BLANK]
            + [PlayerEnum.list_marks()[0]]
            + [settings.BLANK]
            + [PlayerEnum.list_marks()[0]]
        )
        consecutive_blanks = (
            [PlayerEnum.list_marks()[0]]
            + [[settings.BLANK] * settings.WIN_LENGTH][0]
            + [PlayerEnum.list_marks()[0]]
        )
        self.assertFalse(board._has_consecutive_win_length(less_than_len_win))
        self.assertFalse(board._has_consecutive_win_length(alternating))
        self.assertFalse(board._has_consecutive_win_length(consecutive_blanks))

    @mock.patch("game.models.print")
    def test__has_win_length_horizontal(self, mock_print: mock.MagicMock):
        board = Board(3)
        # fmt: off
        board.grid = [["X","X","X"],
                      ["_","_","_"],
                      ["_","_","_"]]
        # fmt: on
        self.assertTrue(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","_"],
                      ["X","X","X"],
                      ["_","_","_"]]
        # fmt: on
        self.assertTrue(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","_"],
                      ["_","_","_"],
                      ["X","X","X"]]
        # fmt: on
        self.assertTrue(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","_","_","_"],
                      ["_","_","_","_","_"],
                      ["_","X","X","X","_"],
                      ["_","_","_","_","_"],
                      ["_","_","_","_","_"]]
        # fmt: on
        self.assertTrue(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())

    @mock.patch("game.models.print")
    def test__has_win_length_vertical(self, mock_print: mock.MagicMock):
        board = Board(3)
        # fmt: off
        board.grid = [["X","_","_"],
                      ["X","_","_"],
                      ["X","_","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertTrue(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","X","_"],
                      ["_","X","_"],
                      ["_","X","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertTrue(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","X"],
                      ["_","_","X"],
                      ["_","_","X"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertTrue(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","_","_","_"],
                      ["_","_","X","_","_"],
                      ["_","_","X","_","_"],
                      ["_","_","X","_","_"],
                      ["_","_","_","_","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertTrue(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())

    @mock.patch("game.models.print")
    def test__has_win_length_diagonal(self, mock_print: mock.MagicMock):
        board = Board(3)
        # fmt: off
        board.grid = [["_","X","_"],
                      ["X","_","X"],
                      ["_","X","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","X","_"],
                      ["X","_","_"],
                      ["_","_","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","_"],
                      ["_","_","X"],
                      ["_","X","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","_"],
                      ["X","_","_"],
                      ["_","X","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","X","_"],
                      ["_","_","X"],
                      ["_","_","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertFalse(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["X","_","_"],
                      ["_","X","_"],
                      ["_","_","X"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertTrue(board._has_win_length_diagonal())
        # fmt: off
        board.grid = [["_","_","X"],
                      ["_","X","_"],
                      ["X","_","_"]]
        # fmt: on
        self.assertFalse(board._has_win_length_horizontal())
        self.assertFalse(board._has_win_length_vertical())
        self.assertTrue(board._has_win_length_diagonal())

    @mock.patch("game.models.print")
    def test__get_forward_diagonals(self, mock_print: mock.MagicMock):
        board = Board(3)
        # fmt: off
        board.grid = [[ 0,  1,  2],
                      [ 3,  4,  5],
                      [ 6,  7,  8]]
        # fmt: on
        expected_result = [[0], [3, 1], [6, 4, 2], [7, 5], [8]]
        forward_diagonals = board._get_forward_diagonals()
        self.assertEqual(forward_diagonals, expected_result)

    @mock.patch("game.models.print")
    def test__get_forward_diagonals(self, mock_print: mock.MagicMock):
        board = Board(3)
        # fmt: off
        board.grid = [[ 0,  1,  2],
                      [ 3,  4,  5],
                      [ 6,  7,  8]]
        # fmt: on
        expected_result = [[6], [3, 7], [0, 4, 8], [1, 5], [2]]
        backward_diagonals = board._get_backward_diagonals()
        self.assertEqual(backward_diagonals, expected_result)

    def test__validate_size(self):
        for test_size in self.size_test_cases:
            if test_size in settings.ALLOWED_SIZE:
                Board._validate_size(test_size)
                continue
            with self.assertRaises(GameError) as cm:
                Board._validate_size(test_size)
            err = cm.exception
            expected_err_msg = "Board size invalid!"
            self.assertEqual(err.message, expected_err_msg)


class TestPlayer(BaseTestCase):
    @mock.patch("game.models.input")
    def test_ask_for_input(self, mock_input: mock.MagicMock):
        current_player = self.mock_players[0]
        mock_input_str = "test"
        mock_input.return_value = mock_input_str
        mock_return = current_player.ask_for_input()
        self.assertEqual(mock_return, mock_input_str)

    @mock.patch("game.models.input")
    def test_retry_input_position_taken(self, mock_input: mock.MagicMock):
        current_player = self.mock_players[0]
        previous_player = self.mock_players[1]
        mock_input_str = "test"
        mock_input.return_value = mock_input_str
        input_calls: List[mock._Call] = mock_input.mock_calls
        expected_input_count = 1
        expected_err_message = PositionAlreadyTaken.message.format(
            current_player=current_player.name,
            previous_player=previous_player.name,
            mark=previous_player.mark,
        )
        mock_return_already_taken = current_player.retry_input(
            error=PositionAlreadyTaken(), previous_player=previous_player
        )
        self.assertEqual(mock_return_already_taken, mock_input_str)
        self.assertEqual(len(input_calls), expected_input_count)
        self.assertEqual(input_calls.count(mock.call(expected_err_message)), 1)

    @mock.patch("game.models.input")
    def test_retry_input_position_does_not_exist(self, mock_input: mock.MagicMock):
        current_player = self.mock_players[0]
        previous_player = self.mock_players[1]
        mock_input_str = "test"
        mock_input.return_value = mock_input_str
        input_calls: List[mock._Call] = mock_input.mock_calls
        expected_input_count = 1
        expected_err_message = PositionDoesNotExist.message.format(
            current_player=current_player.name
        )
        mock_return_does_not_exist = current_player.retry_input(
            error=PositionDoesNotExist(), previous_player=previous_player
        )
        self.assertEqual(mock_return_does_not_exist, mock_input_str)
        self.assertEqual(len(input_calls), expected_input_count)
        self.assertEqual(input_calls.count(mock.call(expected_err_message)), 1)

    @mock.patch("game.models.input")
    def test_rotate_players(self, mock_input: mock.MagicMock):
        players = [self.mock_players[0], self.mock_players[1]]
        expected_players = [self.mock_players[1], self.mock_players[0]]
        rotated_players = Player.rotate_players(players)
        self.assertEqual(rotated_players, expected_players)
