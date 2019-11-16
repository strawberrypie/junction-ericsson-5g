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


class MoveClosestCustomerAgent(Agent):
    def __init__(self, team_name=None):
        super().__init__(team_name=team_name)
        self.graph = None

    def get_next_direction(self, world, car_id, car):
        car_x, car_y = index_to_coordinates(car['position'], world['width'])

        possible_directions = get_possible_directions(world, car['position'])
        if possible_directions:
            # Case: no waiting customers — we don't move
            if not len(self.get_waiting_customers(world)):
                return None

            target_pos = None
            # Case: car is empty — move to closest customer
            if car['used_capacity'] == 0:
                closest_customer_id = self.get_closest_waiting_customer((car_x, car_y), world)
                closest_customer_pos = world['customers'][closest_customer_id]['origin']
                target_pos = closest_customer_pos
            # Case: car has customers — move to closest customer or to closest destination
            elif car['used_capacity'] > 0:
                closest_customer_id = self.get_closest_waiting_customer((car_x, car_y), world)
                closest_customer_pos = world['customers'][closest_customer_id]['origin']

                closest_destination_pos = self.get_closest_destination((car_x, car_y), car_id, world)
                target_pos = self.get_closest_target(
                    (car_x, car_y),
                    [closest_customer_pos, closest_destination_pos],
                    world
                )
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

    def get_waiting_customers(self, world):
        return {c_id: c for c_id, c in world['customers'].items() if c['status'] == 'waiting'}

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

    def get_closest_destination(self, current_coord, car_id, world):
        destination_positions = [
            customer['destination']
            for customer in world['customers'].values()
            if customer['status'] == 'in_car' and customer['car_id'] == car_id
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

    def move(self) -> NoReturn:
        world = self.world
        cars = get_cars(world)

        self.graph = make_graph(world)

        for car_id, car in cars.items():
            new_direction = self.get_next_direction(world, car_id, car)
            self.move_car(world, car_id, car, new_direction)