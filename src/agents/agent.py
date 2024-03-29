import logging
from abc import ABC
from typing import NoReturn

from client import index_to_coordinates, get_position_after_move, move_car


class Agent(ABC):
    def __init__(self, team_name=None, token=None):
        self.team_name = team_name
        self.token = token

    def move_car(self, world, car_id, car, new_direction):
        if new_direction:
            old_coordinates = index_to_coordinates(car['position'], world['width'])

            old_x, old_y = old_coordinates
            new_coordinates = get_position_after_move(old_x, old_y, new_direction)

            team_name = world['teams'][str(car['team_id'])]['name']
            logging.info(
                'Moving car %s of team %s %s (from %s to %s). Score %s', car_id,
                team_name, new_direction.name, repr(old_coordinates),
                repr(new_coordinates), world['teams']['0']['score']
            )

            move_car(car_id, new_direction, self.token)
        else:
            # The car cannot be moved anywhere! A dynamic constraint must have
            # appeared. Just leave its previous direction as it was
            logging.info('Car %s cannot move anywhere. Score %s', car_id, world['teams']['0']['score'])

    def move(self, world) -> NoReturn:
        """Send commands for each car to move."""
        raise NotImplementedError

    def get_waiting_customers(self, world):
        return {c_id: c for c_id, c in world['customers'].items() if c['status'] == 'waiting'}

