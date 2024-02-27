from z3 import *


class InserterLogic:
    def __init__(self, width, height, conveyor, input_pos, output_pos, dir_type, directions):
        # Inserter variable for each cell of enumerated type "dir_type"
        self.inserter = [[Const(f"INS_{i}_{j}", dir_type) for i in range(width)] for j in range(height)]

        self.conveyor = conveyor

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

    def inserter_input(self):
        inserter_input = []

        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:

                            direction_clauses.append(If(self.inserter[i][j] == self.opposite_dir[direction],
                                                        self.conveyor[x][y] != self.direction[0],
                                                        False))
                    inserter_input.append(If(self.inserter[i][j] != self.direction[0], Or(direction_clauses), True))

        return inserter_input

    def inserter_output(self):
        inserter_output = []

        for i in range(self.height):
            for j in range(self.width):
                if not self.is_output(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.dir_shift[direction][0], j + self.dir_shift[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            direction_clauses.append(If(self.inserter[i][j] == self.direction[direction],
                                                        And(self.conveyor[x][y] != self.direction[0],
                                                            self.conveyor[x][y] != self.opposite_dir[direction]),
                                                        False))
                    inserter_output.append(If(self.inserter[i][j] != self.direction[0], Or(direction_clauses), True))

        return inserter_output

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
        return self.inserter_input() + self.inserter_output()


