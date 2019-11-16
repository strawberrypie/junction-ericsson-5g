from abc import ABC
from typing import NoReturn

from client import add_team_and_get_token, get_world


class Agent(ABC):
    def __init__(self, team_name=None):
        self.team_name, self.token = add_team_and_get_token(team_name)

    @property
    def world(self):
        return get_world()

    def move(self) -> NoReturn:
        """Send commands for each car to move."""
        raise NotImplementedError
