from z3 import *


class ConveyorLogic:
    def __init__(self, width, height, input_pos, output_pos, dir_type, directions):
        # Conveyor variable for each cell of enumerated type "dir_type"
        self.conveyor = [[Const(f"S_CONV_{i}_{j}", dir_type) for i in range(width)] for j in range(height)]

        self.n_dir = 5

        # Width and height of the blueprint
        self.width = width
        self.height = height

        # Each of the values the enumerated type "dir_type" can take
        self.direction = directions

        # Start and end positions of each route
        self.input_pos = input_pos
        self.output_pos = output_pos

        # Encoded directions and the relative offset they represent
        self.dir_shift = {
            1: (-1, 0),  # North
            2: (0, 1),  # East
            3: (1, 0),  # South
            4: (0, -1)  # West
        }

        # Returns the opposite direction of the direction key
        self.opposite_dir = {
            1: self.direction[3],  # North -> South
            2: self.direction[4],  # East  -> West
            3: self.direction[1],  # South -> North
            4: self.direction[2]  # West  -> East
        }

    def conveyor_input(self):
        conveyor_input = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            direction_clauses.append(If(self.conveyor[i][j] != self.direction[direction],
                                                        Or(self.conveyor[x][y] == self.opposite_dir[direction], self.inserter[x][y] == self.opposite_dir[direction]),
                                                        False))
                    conveyor_input.append(If(self.conveyor[i][j] != self.direction[0], Or(direction_clauses), True))

        return conveyor_input

    def conveyor_output(self):
        conveyor_output = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_output(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            direction_clauses.append(If(self.conveyor[i][j] == self.direction[direction],
                                                        And(self.conveyor[x][y] != self.direction[0],
                                                            self.conveyor[x][y] != self.opposite_dir[direction]),
                                                        False))
                    conveyor_output.append(If(self.conveyor[i][j] != self.direction[0], Or(direction_clauses), True))

        return conveyor_output

    def end_of_route(self):
        # An output cell cant carry the items to any other cell (end of route)
        end_of_route = []
        for pos in self.output_pos:
            i = pos[0]
            j = pos[1]
            direction_clauses = []
            for direction in range(1, self.n_dir):
                x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                if 0 <= x < self.height and 0 <= y < self.width:
                    direction_clauses.append(If(self.conveyor[i][j] == self.direction[direction],
                                                self.conveyor[x][y] == self.direction[0], True))
            end_of_route.append(And(direction_clauses))

        return end_of_route

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

    def constraints(self):
        return self.conveyor_input() + self.conveyor_output() + self.end_of_route()

    def set_inserter(self, inserter):
        self.inserter = inserter
