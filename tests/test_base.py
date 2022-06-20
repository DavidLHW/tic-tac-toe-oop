from unittest import TestCase

from game.models import Player, PlayerEnum


class BaseTestCase(TestCase):
    size_test_cases = [2, 3, 4, 5, 6, "", "test", None]
    mock_players = [
        Player(f"Player {i}", PlayerEnum.list_marks()[i - 1])
        for i in PlayerEnum.list_indices()
    ]
