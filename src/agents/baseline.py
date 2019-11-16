from typing import NoReturn

from client import move_cars
from .agent import Agent


class BaselineAgent(Agent):
    def __init__(self, team_name=None):
        super().__init__(team_name=team_name)
        self.previous_car_directions = {}

    def move(self) -> NoReturn:
        world = self.world
        new_car_directions = move_cars(self.token, world, self.previous_car_directions)
        self.previous_car_directions = new_car_directions
