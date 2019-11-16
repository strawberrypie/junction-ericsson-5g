from catalyst.rl.core import EnvironmentSpec
from catalyst.rl.utils import extend_space
from gym import Space
from gym.spaces import Tuple, Discrete

from .client import setup, add_team_and_get_token, get_world, start_game, get_cars, get_team_stats, move_car, stop_game


class CitySimulatorEnvironment(EnvironmentSpec):
    def __init__(self):
        super().__init__()
        setup()

        self.team_name, self.token = add_team_and_get_token()

        if not get_world():
            start_game()

        world = get_world()
        team_id, score = get_team_stats(self.team_name, world)

        self.cars = {
            car_id: car
            for car_id, car in get_cars(world).items()
            if car['team_id'] == team_id
        }

        self._prepare_spaces()

    @property
    def observation_space(self) -> Space:
        return Tuple([
            ...,  # TODO board state
            ...,  # TODO cars positions
            ...,  # TODO customers positions
        ])

    @property
    def state_space(self) -> Space:
        return self._state_space

    @property
    def action_space(self) -> Space:
        # TODO use a more suitable product of spaces
        return Tuple([
            Discrete(len(self.cars)),  # Cars that can move | TODO exclude full cars
            Discrete(4),  # Possible directions | TODO exclude impossible directions
        ])

    def _prepare_spaces(self):
        self._state_space = extend_space(
            self.observation_space, self.history_len
        )

    def reset(self):
        stop_game()

        self.team_name, self.token = add_team_and_get_token()

        if not get_world():
            start_game()

        return None  # TODO observation

    def step(self, action):
        car_id, direction_id = action
        car_id = list(self.cars.keys())[car_id]
        move_car(car_id, direction_id, self.token)

        return observation, reward, done, info





