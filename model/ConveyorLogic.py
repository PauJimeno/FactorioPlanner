from z3 import *


class ConveyorLogic:
    def __init__(self, blueprint_width, blueprint_height, route_start_end):
        # Width and height of the blueprint
        self.width = blueprint_width
        self.height = blueprint_height

        # Start and end positions of each route
        self.route_pos = route_start_end

        # Domain of values conveyor variables can be assigned to (0, 1, 2, 3, 4)
        self.domain = 5
        self.n_bits = math.ceil(math.log2(self.domain))

        # Encoded directions and the relative offset they represent
        self.directions = {
            1: (-1, 0),  # North
            2: (0, 1),   # East
            3: (1, 0),   # South
            4: (0, -1)   # West
        }

        # Returns the oposite direction of the direction key
        self.opposite_dir = {
            1: 3,  # North -> South
            2: 4,  # East  -> West
            3: 1,  # South -> North
            4: 2   # West  -> East
        }

        # Z3 variable representing the positions a conveyors might be and the directions it is pointing
        # n_bits = 3, because 5 possible directions (N, S, E, W, None) need 3 bits to be encoded
        self.surface_conveyor = [[BitVec(f"S_CONV_{i}_{j}", self.n_bits) for i in range(self.width)] for j in
                                 range(self.height)]

        self.underground_conveyor = [[BitVec(f"U_CONV_{i}_{j}", self.n_bits) for i in range(self.width)] for j in
                                     range(self.height)]

    def domain_constraint(self):
        return [And(UGE(self.surface_conveyor[i][j], 0), ULE(self.surface_conveyor[i][j], len(self.directions)))
                for i in range(self.height) for j in range(self.width)]

    def route_points_constraint(self):
        conveyor_at_start_end_pos = []
        for route in self.route_pos:
            for pos in route:
                conveyor_at_start_end_pos.append(UGT(self.surface_conveyor[pos[0]][pos[1]], 0))

        return conveyor_at_start_end_pos

    def precedence_constraint(self):
        precedent_conveyor = []
        for i in range(self.height):
            for j in range(self.width):
                for route in self.route_pos:
                    if i != route[0][0] or j != route[0][1]:
                        consequence = []
                        for direction in self.directions:
                            x, y = i + self.directions[direction][0], j + self.directions[direction][1]
                            if 0 <= x < self.height and 0 <= y < self.width:
                                consequence.append(
                                    And(self.surface_conveyor[x][y] == self.opposite_dir[direction],
                                        self.surface_conveyor[i][j] != direction))
                        precedent_conveyor.append(Implies(UGT(self.surface_conveyor[i][j], 0), Or(consequence)))

        return precedent_conveyor

    def successor_constraint(self):
        successor_conveyor = []
        for i in range(self.height):
            for j in range(self.width):
                for route in self.route_pos:
                    if i != route[1][0] or j != route[1][1]:
                        consequence = []
                        for direction in self.directions:
                            x, y = i + self.directions[direction][0], j + self.directions[direction][1]
                            if 0 <= x < self.height and 0 <= y < self.width:
                                consequence.append(
                                    And(self.surface_conveyor[i][j] == direction,
                                        self.surface_conveyor[x][y] != self.opposite_dir[direction],
                                        UGT(self.surface_conveyor[x][y], 0)))
                        successor_conveyor.append(Implies(UGT(self.surface_conveyor[i][j], 0), Or(consequence)))

        return successor_conveyor

    def constraints(self):
        return self.route_points_constraint() + self.precedence_constraint() + self.successor_constraint() + self.domain_constraint()
