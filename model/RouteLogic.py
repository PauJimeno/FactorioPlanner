from z3 import *


class RouteLogic:
    def __init__(self, blueprint_width, blueprint_height, input_pos, output_pos, conveyor, inserter, direction):
        # Width and height of the blueprint
        self.width = blueprint_width
        self.height = blueprint_height

        # Start and end positions of each route
        self.input_pos = input_pos
        self.output_pos = output_pos

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
        return [(UGT(self.route[i][j], 0)) == (Or(self.conveyor[i][j] != self.direction[0],
                                                  self.inserter[i][j] != self.direction[0]))
                for i in range(self.height) for j in range(self.width)]

    def route_start(self):
        # Each input cell is the start of route, and it must be a conveyor
        return [And(self.route[pos[0]][pos[1]] == 1,
                    self.conveyor[pos[0]][pos[1]] != self.direction[0])
                for pos in self.input_pos]

    def route_end(self):
        # Each output cell must have a larger value than 1, and it must be a conveyor
        return [And(UGT(self.route[pos[0]][pos[1]], 1),
                    self.conveyor[pos[0]][pos[1]] != self.direction[0])
                for pos in self.output_pos]

    def forward_consistency(self):
        forward_consistency = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_output(i, j):
                    output_connections = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            # A route cell must have at least one cell route greater than or equal to itself (Output)
                            output_connections.append(If(Or(self.conveyor[i][j] == self.direction[direction],
                                                            self.inserter[i][j] == self.direction[direction]),
                                                         UGT(self.route[x][y], self.route[i][j]), False))
                    forward_consistency.append(If(UGT(self.route[i][j], 0), Or(output_connections), True))
        return forward_consistency

    def backward_consistency(self):
        backward_consistency = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    input_connections = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            input_connections.append(If(Or(And(self.conveyor[i][j] != self.direction[direction], self.conveyor[i][j] != self.direction[0]),
                                                        self.inserter[i][j] == self.opposite_dir[direction])
                                                        , And(ULT(self.route[x][y], self.route[i][j]),
                                                        UGT(self.route[x][y], 0)), False))
                    backward_consistency.append(If(UGT(self.route[i][j], 0), Or(input_connections), True))
        return backward_consistency

    def constraints(self):
        return self.route_start() +\
            self.part_of_route() +\
            self.domain_constraint() +\
            self.route_end() +\
            self.forward_consistency() +\
            self.backward_consistency()

    def is_output(self, x, y):
        is_output = False
        for pos in self.output_pos:
            if x == pos[0] and y == pos[1]:
                is_output = True
        return is_output

    def is_input(self, x, y):
        is_output = False
        for pos in self.input_pos:
            if x == pos[0] and y == pos[1]:
                is_output = True
        return is_output

    def optimize_criteria(self):
        return sum([If(self.route[i][j] == 0, 0, 1) for i in range(self.height) for j in range(self.width)])

