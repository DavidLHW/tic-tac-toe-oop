from typing import Union

import config as settings


class GameError(Exception):
    message: str = "Unknown error encountered"

    def __init__(self, *args: Union[int, str], **kwargs: Union[int, str]) -> None:
        key = "message"
        value = kwargs.pop(key, None)
        if value:
            setattr(self, key, value)
        super().__init__(*args)


class PositionAlreadyTaken(GameError):
    message: str = (
        "{current_player}, {previous_player} has already put {mark} in this position, "
        "please enter a new coordinate: "
    )


class PositionDoesNotExist(GameError):
    message: str = (
        "{current_player}, the coordinate cannot be identified, "
        "please enter a new coordinate: "
    )


class GameOver(GameError):
    message: str = settings.END_GAME_TEXT
