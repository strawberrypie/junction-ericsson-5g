import logging
from typing import NoReturn

import networkx as nx

from client import (
    get_cars,
    get_possible_directions, index_to_coordinates, get_position_after_move,
    coordinates_to_index
)
from .agent import Agent


def make_graph(world):
    grid = world['grid']
    height, width = world['height'], world['width']

    graph: nx.Graph = nx.grid_2d_graph(width, height)
    for position, status in enumerate(grid):
        if status is False:
            x, y = index_to_coordinates(position, width)
            neighbors = list(graph.neighbors((x, y)))
            for neighbor in neighbors:
                graph.remove_edge((x, y), neighbor)
    return graph


class AgentStateMachine(Agent):
    def __init__(self, team_name=None, token=None):
        super().__init__(team_name=team_name, token=token)
        self.graph = None

        self.cars_state = None

    def get_next_state(self, world, car_id, car):
        previous_state = self.cars_state[car_id]['state']
        next_state = None
        if previous_state == 'searching':
            next_state = previous_state
        elif previous_state == 'getting_customer':
            if self.cars_state[car_id]['prev_capacity'] < car['used_capacity']:
                print('Car ' + str(car_id) + ' has grabbed a client')
                self.cars_state[car_id]['customers'].append(self.cars_state[car_id]['curr_customer'])
                self.cars_state[car_id]['curr_customer'] = None
                self.cars_state[car_id]['prev_capacity'] += 1
                if self.cars_state[car_id]['prev_capacity'] == car['capacity']:
                    next_state = 'switch_delivering'
                else:
                    next_state = 'searching'
            else:
                car_x, car_y = index_to_coordinates(car['position'], world['width'])
                closest_customer_id = self.get_closest_waiting_customer((car_x, car_y), world)
                closest_customer_pos = world['customers'][closest_customer_id]['origin']

                if closest_customer_pos == self.cars_state[car_id]['curr_customer']['origin']:
                    next_state = 'getting_customer'
                else:
                    next_state = 'searching'
        elif previous_state == 'delivering':
            if self.cars_state[car_id]['prev_capacity'] > car['used_capacity']:
                self.cars_state[car_id]['customers'].remove(self.cars_state[car_id]['curr_customer'])
                self.cars_state[car_id]['prev_capacity'] = car['used_capacity']
                if car['used_capacity'] > 0:
                    next_state = 'switch_delivering'
                else:
                    next_state = 'searching'
            else:
                next_state = 'delivering'

        return next_state

    def get_next_direction(self, world, car_id, car):
        car_x, car_y = index_to_coordinates(car['position'], world['width'])

        possible_directions = get_possible_directions(world, car['position'])
        if possible_directions:
            # Case: no waiting customers — we don't move
            if not len(self.get_waiting_customers(world)):
                return None

            target_pos = None
            # Case: car is empty — move to closest customer
            state = self.get_next_state(world, car_id, car)
            self.cars_state[car_id][state] = state
            print('Car ' + str(car_id) + ' state: ' + state + '; capacity : ' + str(car['used_capacity']) +
                  ' ; max: ' + str(car['capacity']))
            print(self.cars_state[car_id]['customers'])
            if state == 'searching':
                closest_customer_id = self.get_closest_waiting_customer((car_x, car_y), world)
                closest_customer_pos = world['customers'][closest_customer_id]['origin']
                target_pos = closest_customer_pos

                self.cars_state[car_id]['curr_customer'] = world['customers'][closest_customer_id]
                self.cars_state[car_id]['state'] = 'getting_customer'
            elif state == 'getting_customer':
                target_pos = self.cars_state[car_id]['curr_customer']['origin']
            elif state == 'delivering':
                target_pos = self.cars_state[car_id]['curr_customer']['destination']
            elif state == 'switch_delivering':
                self.cars_state[car_id]['curr_customer'] = self.get_closest_delivering_customer((car_x, car_y), car_id, world) #self.cars_state[car_id]['customers'][-1]
                target_pos = self.cars_state[car_id]['curr_customer']['destination']
                self.cars_state[car_id]['state'] = 'delivering'

            if target_pos is not None:
                target_coord = index_to_coordinates(target_pos, world['width'])
                return self.get_best_direction(world, car_x, car_y, target_coord)
        return None

    def get_best_direction(self, world, car_x, car_y, target_coord):
        possible_directions = get_possible_directions(world, coordinates_to_index(car_x, car_y, world['width']))

        target_distance = self.get_path_length((car_x, car_y), target_coord)

        best_delta = 0
        best_direction = None
        for direction in possible_directions:
            new_pos = get_position_after_move(car_x, car_y, direction)
            delta = target_distance - self.get_path_length(new_pos, target_coord)
            if delta > best_delta:
                best_delta = delta
                best_direction = direction
        if best_direction is None:
            logging.info('All directions are bad!')
        return best_direction

    def get_closest_waiting_customer(self, position, world):
        return min(
            self.get_waiting_customers(world),
            key=lambda cust_id: self.get_path_length(
                position,
                index_to_coordinates(
                    world['customers'][cust_id]['origin'],
                    world['width'])
            )
        )

    def get_closest_delivering_customer(self, position, car_id, world):
        return min(
            self.cars_state[car_id]['customers'],
            key=lambda cust_id: self.get_path_length(
                position,
                index_to_coordinates(
                    self.cars_state[car_id]['customers'][cust_id]['destination'],
                    world['width'])
            )
        )

    def get_closest_destination(self, current_coord, car_id, world):
        destination_positions = [
            customer['destination']
            for customer in world['customers'].values()
            if customer['status'] == 'in_car' and str(customer['car_id']) == car_id
        ]

        return self.get_closest_target(current_coord, destination_positions, world)

    def get_closest_target(self, current_coord, target_positions, world):
        target_positions = [pos for pos in target_positions if pos is not None]
        if not target_positions:
            return None
        if len(target_positions) == 1:
            return target_positions[0]
        if len(target_positions) > 1:
            return min(
                target_positions,
                key=lambda position: self.get_path_length(
                    current_coord,
                    index_to_coordinates(position, world['width'])
                )
            )

    def get_path_length(self, source, target):
        try:
            return nx.shortest_path_length(self.graph, source, target)
        except nx.exception.NetworkXNoPath:
            return float('+inf')

    def move(self, world) -> NoReturn:
        current_team_id = int([
            team_id
            for team_id, team_info in world['teams'].items()
            if team_info['name'] == self.team_name
        ][0])

        cars = get_cars(world)
        current_player_cars = {
            car_id: car
            for car_id, car in cars.items()
            if car['team_id'] == current_team_id
        }

        self.graph = make_graph(world)
        if self.cars_state is None:
            self.cars_state = {}
            for car_id, car in current_player_cars.items():
                self.cars_state[car_id] = {
                    'state': 'searching',
                    'customers': [],
                    'curr_customer': None,
                    'prev_capacity': 0
                }

        for car_id, car in current_player_cars.items():
            new_direction = self.get_next_direction(world, car_id, car)
            self.move_car(world, car_id, car, new_direction)