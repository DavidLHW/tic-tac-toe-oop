from unittest import mock
from typing import List

import config as settings
from app import main, assign_players, get_row_col_from_input
from game.models import Player
from game.errors import PositionDoesNotExist, PositionAlreadyTaken
from tests.test_base import BaseTestCase


class TestUtils(BaseTestCase):
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_assign_players(
        self, mock_input: mock.MagicMock, mock_print: mock.MagicMock
    ):
        mock_players = [
            Player(name="A", mark="X"),
            Player(name="B", mark="O"),
        ]
        mock_input.side_effect = [
            mock_players[i].name for i in range(len(mock_players))
        ]
        expected_print = [
            mock.call(f"Player {i + 1} is {mock_players[i].name} !!!\n")
            for i in range(len(mock_players))
        ]
        players = assign_players([])
        self.assertEqual(mock_print.mock_calls, expected_print)
        for i in range(len(players)):
            self.assertEqual(players[i].name, mock_players[i].name)
            self.assertEqual(players[i].mark, mock_players[i].mark)

    def test_get_row_col_from_input(self):
        mock_input = "1,2"
        row, col = get_row_col_from_input(mock_input)
        self.assertEqual(row, 1)
        self.assertEqual(col, 2)

        expected_err_msg = PositionDoesNotExist.message

        mock_input = "1"
        with self.assertRaises(PositionDoesNotExist) as cm:
            get_row_col_from_input(mock_input)
        err = cm.exception
        self.assertEqual(err.message, expected_err_msg)

        mock_input = "1,v"
        with self.assertRaises(PositionDoesNotExist) as cm:
            get_row_col_from_input(mock_input)
        err = cm.exception
        self.assertEqual(err.message, expected_err_msg)


class TestGameFlow(BaseTestCase):
    def _merge_player_moves(self, player_1_move, player_2_move):
        result = [None] * (len(player_1_move) + len(player_2_move))
        result[::2] = player_1_move
        result[1::2] = player_2_move
        return result

    @mock.patch("game.models.print")
    @mock.patch("builtins.input")
    def test_board_size_input(
        self,
        mock_input: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        mock_input.side_effect = [board_size]
        input_calls: List[mock._Call] = mock_input.mock_calls
        expected_print_count_models = 5
        expected_input_count = 2
        with self.assertRaises(StopIteration) as _:
            main()
        self.assertEqual(len(input_calls), expected_input_count)
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("app.run_game_loop")
    @mock.patch("app.assign_players")
    @mock.patch("builtins.print")
    @mock.patch("builtins.input")
    def test_invalid_board_size(
        self,
        mock_input: mock.MagicMock,
        mock_print: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_run_game_loop: mock.MagicMock,
    ):
        mock_input.side_effect = [1, 3]
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        mock_run_game_loop.return_value = None
        expected_err_msg = "Board size invalid!"
        expected_win_msg = settings.END_GAME_TEXT.format(winner="No one")
        main()
        self.assertEqual(mock_print.mock_calls[-1], mock.call(expected_win_msg))

    @mock.patch("builtins.print")
    @mock.patch("builtins.input")
    def test_name_input(
        self,
        mock_input: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        inputs = [board_size, *[p.name for p in self.mock_players]]
        mock_input.side_effect = inputs
        input_calls: List[mock._Call] = mock_input.mock_calls
        expected_print_count_models = 7
        expected_input_count = 4
        with self.assertRaises(StopIteration) as _:
            main()
        self.assertEqual(len(input_calls), expected_input_count)
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("builtins.input")
    def test_coordinate_input(
        self,
        mock_input: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        mock_input.side_effect = [board_size, "1,1"]
        expected_input_count = 3
        expected_prints = [
            mock.call("Prepare a 3x3 board …"),
            mock.call("_ _ _"),
            mock.call("_ _ _"),
            mock.call("_ _ _"),
            mock.call(),
            mock.call("X _ _"),
            mock.call("_ _ _"),
            mock.call("_ _ _"),
            mock.call(),
        ]
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        with self.assertRaises(StopIteration) as _:
            main()
        self.assertEqual(len(mock_input.mock_calls), expected_input_count)
        self.assertEqual(mock_print_models.mock_calls, expected_prints)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("builtins.input")
    def test_invalid_coordinate(
        self,
        mock_input: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["1,1"]
        p2_moves = ["1,1"]
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.append("4,4")
        inputs.append("1")
        inputs.append("2,v")
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        input_calls: List[mock._Call] = mock_input.mock_calls
        expected_print_count_models = 9
        expected_input_count = 7
        expected_err_message_position_taken = PositionAlreadyTaken.message.format(
            current_player=self.mock_players[1].name,
            previous_player=self.mock_players[0].name,
            mark=self.mock_players[0].mark,
        )
        expected_err_message_does_not_exist = PositionDoesNotExist.message.format(
            current_player=self.mock_players[1].name,
        )
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        with self.assertRaises(StopIteration) as _:
            main()
        self.assertEqual(len(input_calls), expected_input_count)
        self.assertEqual(
            input_calls.count(mock.call(expected_err_message_position_taken)), 1
        )
        self.assertEqual(
            input_calls.count(mock.call(expected_err_message_does_not_exist)), 3
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_horizontal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["1,1", "1,2", "1,3"]
        p2_moves = ["2,2", "3,3"]
        expected_print_count_models = 25
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_vertical_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["1,1", "2,1", "3,1"]
        p2_moves = ["2,2", "3,3"]
        expected_print_count_models = 25
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_forward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["3,1", "2,2", "1,3"]
        p2_moves = ["1,1", "1,2"]
        expected_print_count_models = 25
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_backward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["1,1", "2,2", "3,3"]
        p2_moves = ["1,2", "1,3"]
        expected_print_count_models = 25
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_horizontal_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["2,2", "1,3", "2,3"]
        p2_moves = ["3,1", "3,2", "3,3"]
        expected_print_count_models = 29
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_vertical_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["2,2", "3,3", "2,3"]
        p2_moves = ["1,1", "2,1", "3,1"]
        expected_print_count_models = 29
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_forward_diagonal_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["1,1", "1,2", "2,1"]
        p2_moves = ["3,1", "2,2", "1,3"]
        expected_print_count_models = 29
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_3_grid_backward_diagonal_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 3
        p1_moves = ["1,2", "1,3", "2,1"]
        p2_moves = ["1,1", "2,2", "3,3"]
        expected_print_count_models = 29
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_horizontal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["4,2", "4,3", "4,4"]
        p2_moves = ["3,3", "2,4"]
        expected_print_count_models = 31
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_vertical_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["2,4", "3,4", "4,4"]
        p2_moves = ["3,3", "1,4"]
        expected_print_count_models = 31
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_forward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["4,1", "3,2", "2,3"]
        p2_moves = ["1,1", "1,2"]
        expected_print_count_models = 31
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_backward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["2,4", "3,3", "4,2"]
        p2_moves = ["1,1", "1,2"]
        expected_print_count_models = 31
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_horizontal_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["2,2", "1,3", "2,4"]
        p2_moves = ["4,1", "4,2", "4,3"]
        expected_print_count_models = 36
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_vertical_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["2,2", "1,3", "3,3"]
        p2_moves = ["1,4", "2,4", "3,4"]
        expected_print_count_models = 36
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_forward_diagonal_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["2,2", "1,3", "2,4"]
        p2_moves = ["4,1", "3,2", "2,3"]
        expected_print_count_models = 36
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_4_grid_backward_diagonal_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 4
        p1_moves = ["1,2", "1,4", "2,1"]
        p2_moves = ["4,4", "2,2", "3,3"]
        expected_print_count_models = 36
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_horizontal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["5,2", "5,3", "5,4"]
        p2_moves = ["3,3", "2,4"]
        expected_print_count_models = 37
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_vertical_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["2,5", "3,5", "4,5"]
        p2_moves = ["3,3", "2,4"]
        expected_print_count_models = 37
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_forward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["5,2", "4,3", "3,4"]
        p2_moves = ["3,3", "2,4"]
        expected_print_count_models = 37
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_backward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["2,3", "3,4", "4,5"]
        p2_moves = ["3,3", "2,4"]
        expected_print_count_models = 37
        expected_print_count_main = 1
        expected_final_message = "Player 1 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_horizontal_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["3,3", "2,4", "1,1"]
        p2_moves = ["5,2", "5,3", "5,4"]
        expected_print_count_models = 43
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_vertical_o_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["3,3", "2,4", "1,1"]
        p2_moves = ["2,5", "3,5", "4,5"]
        expected_print_count_models = 43
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_forward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["3,3", "2,4", "1,1"]
        p2_moves = ["5,2", "4,3", "3,4"]
        expected_print_count_models = 43
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_5_grid_backward_diagonal_x_win(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        board_size = 5
        p1_moves = ["3,3", "2,4", "1,1"]
        p2_moves = ["2,3", "3,4", "4,5"]
        expected_print_count_models = 43
        expected_print_count_main = 1
        expected_final_message = "Player 2 wins the game !!!!"
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)

    @mock.patch("game.models.print")
    @mock.patch("app.assign_players")
    @mock.patch("app.print")
    @mock.patch("builtins.input")
    def test_draw(
        self,
        mock_input: mock.MagicMock,
        mock_print_main: mock.MagicMock,
        mock_assign_players: mock.MagicMock,
        mock_print_models: mock.MagicMock,
    ):
        p1_moves = ["1,1", "1,2", "3,1", "2,3", "3,3"]
        p2_moves = ["2,2", "1,3", "2,1", "3,2"]
        expected_print_count_models = 41
        expected_print_count_main = 1
        expected_final_message = "No one wins the game !!!!"
        board_size = 3
        inputs = self._merge_player_moves(p1_moves, p2_moves)
        inputs.insert(0, board_size)
        mock_input.side_effect = inputs
        mock_assign_players.return_value = [
            self.mock_players[0],
            self.mock_players[1],
        ]
        main()
        self.assertEqual(len(mock_print_main.mock_calls), expected_print_count_main)
        self.assertEqual(
            mock_print_main.mock_calls[-1], mock.call(expected_final_message)
        )
        self.assertEqual(len(mock_print_models.mock_calls), expected_print_count_models)
