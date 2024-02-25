from z3 import *


class RouteLogic:
    def __init__(self, blueprint_width, blueprint_height, route_start_end, conveyor, inserter, direction):
        # Width and height of the blueprint
        self.width = blueprint_width
        self.height = blueprint_height

        # Start and end positions of each route
        self.route_pos = route_start_end

        self.n_dir = 5

        # Domain of values route variables can be assigned to (width*height)
        self.domain = blueprint_width * blueprint_height
        self.n_bits = math.ceil(math.log2(self.domain))

        # Reference to the conveyor variable
        self.conveyor = conveyor

        # Reference to the inserter variable
        self.inserter = inserter

        # Values of the finite domain "directions"
        self.direction = direction

        # Encoded directions and the relative offset they represent
        self.dir_shift = {
            1: (-1, 0),  # North
            2: (0, 1),   # East
            3: (1, 0),   # South
            4: (0, -1)   # West
        }

        # Returns the opposite direction of the direction key
        self.opposite_dir = {
            1: self.direction[3],  # North -> South
            2: self.direction[4],  # East  -> West
            3: self.direction[1],  # South -> North
            4: self.direction[2]   # West  -> East
        }

        # Z3 variable representing the path of a route
        self.route = [[BitVec(f"R_{i}_{j}", self.n_bits) for i in range(self.width)] for j in range(self.height)]

    def domain_constraint(self):
        return[ULE(self.route[i][j], self.domain - 1)
               for i in range(self.height) for j in range(self.width)]

    def part_of_route(self):
        # If a cell is part of route, then a conveyor or an inserter must be there
        return [(UGT(self.route[i][j], 0)) == (self.conveyor[i][j] != self.direction[0])
                for i in range(self.height) for j in range(self.width)]

    def route_start(self):
        # Each input cell is the start of route, and it must be a conveyor
        return [And(self.route[pos[0][0]][pos[0][1]] == 1,
                    self.conveyor[pos[0][0]][pos[0][1]] != self.direction[0])
                for pos in self.route_pos]

    def route_end(self):
        # Each output cell must have a larger value than 1, and it must be a conveyor
        return [And(UGT(self.route[pos[1][0]][pos[1][1]], 1),
                    self.conveyor[pos[1][0]][pos[1][1]] != self.direction[0])
                for pos in self.route_pos]

    def conveyor_incremental_route(self):
        increment_route = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_output(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            direction_clauses.append(If(self.conveyor[i][j] == self.direction[direction],
                                                        And(UGT(self.route[x][y], self.route[i][j]),
                                                            self.conveyor[x][y] != self.opposite_dir[direction]), False))
                    increment_route.append(If(self.conveyor[i][j] != self.direction[0], Or(direction_clauses), True))

        return increment_route

    def conveyor_decremental_route(self):
        increment_route = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            direction_clauses.append(If(self.conveyor[i][j] != self.direction[direction],
                                                        And(ULT(self.route[x][y], self.route[i][j]),
                                                            self.conveyor[x][y] == self.opposite_dir[direction]), False))
                    increment_route.append(If(self.conveyor[i][j] != self.direction[0], Or(direction_clauses), True))

        return increment_route

    def end_of_route(self):
        # An output cell cant carry the items to any other cell (end of route)
        end_of_route = []
        for pos in self.route_pos:
            i = pos[1][0]
            j = pos[1][1]
            direction_clauses = []
            for direction in range(1, self.n_dir):
                x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                if 0 <= x < self.height and 0 <= y < self.width:
                    direction_clauses.append(If(self.conveyor[i][j] == self.direction[direction],
                                                self.conveyor[x][y] == self.direction[0], True))
            end_of_route.append(And(direction_clauses))

        return end_of_route

    def constraints(self):
        return self.route_start() +\
            self.part_of_route() +\
            self.domain_constraint() +\
            self.route_end() +\
            self.conveyor_incremental_route() +\
            self.conveyor_decremental_route() + \
            self.end_of_route()

    def is_output(self, x, y):
        is_output = False
        for pos in self.route_pos:
            if x == pos[1][0] and y == pos[1][1]:
                is_output = True
        return is_output

    def is_input(self, x, y):
        is_output = False
        for pos in self.route_pos:
            if x == pos[0][0] and y == pos[0][1]:
                is_output = True
        return is_output

    def optimize_criteria(self):
        return sum([If(self.route[i][j] == 0, 1, 0) for i in range(self.height) for j in range(self.width)])

