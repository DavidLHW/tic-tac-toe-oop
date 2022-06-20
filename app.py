from typing import List, Optional

import config as settings
from game.models import Player, Board, GameState, PlayerEnum
from game.errors import GameOver, PositionDoesNotExist, PositionAlreadyTaken, GameError


def get_row_col_from_input(player_input: str):
    """Parse row and column values from player input"""
    if settings.DELIMITER not in player_input:
        raise PositionDoesNotExist

    values = player_input.split(settings.DELIMITER)
    if len(values) != 2:
        raise PositionDoesNotExist

    row, col = map(lambda x: int(x) if (x.isdigit() and int(x) > 0) else None, values)
    if (type(row) is not int) or (type(col) is not int):
        raise PositionDoesNotExist
    return row, col


def assign_players(players: list) -> List[Player]:
    """Initialize players"""
    for player_enum in PlayerEnum:
        name = input(f"Enter the {player_enum.name} player name: ")
        player_enum_dict = eval(player_enum.value)
        player = Player(name=name, mark=player_enum_dict["mark"])
        players.append(player)
        print(f"Player {player_enum_dict['index']} is {player.name} !!!\n")
    return players


def run_game_loop(board: Board, players: List[Player]) -> Optional[Player]:
    """Main game loop

    This loop will continue as long as there are still space to mark and no
    winners on the board.

    Args:
      board: current instance of the game.
      players: list of players in this game.

    Returns:
      The winner of the game, if any.
    """
    winner = None
    # set players
    current_player = players[0]
    previous_player = players[-1]
    board.current_player = current_player
    # get current player input
    player_input = current_player.ask_for_input()
    while board.state not in [GameState.DRAW, GameState.WIN]:
        try:
            row, col = get_row_col_from_input(player_input)
            # update & evaluate board
            board.make_move(row, col)
            board.evaluate_board()
        except (PositionAlreadyTaken, PositionDoesNotExist) as err:
            player_input = current_player.retry_input(
                error=err, previous_player=previous_player
            )
            continue
        except GameOver as err:
            if board.state == GameState.WIN:
                # only set winner if there is one
                winner = board.current_player
            break
        except:
            # exit if unexpected error is caught
            print(err.message)
            break
        else:
            # set players
            players = Player.rotate_players(players)
            current_player = players[0]
            previous_player = players[-1]
            board.current_player = current_player
            # get current player input
            player_input = current_player.ask_for_input()
    return winner


def main():
    while True:
        try:
            board = Board.setup_board()
            break
        except GameError as err:
            print(err.message)
            continue

    players: List[Player] = []
    players = assign_players(players)
    winner = run_game_loop(board, players)

    if winner is not None:
        print(settings.END_GAME_TEXT.format(winner=winner.name))
    else:
        print(settings.END_GAME_TEXT.format(winner="No one"))


if __name__ == "__main__":
    main()
