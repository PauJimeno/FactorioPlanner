from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class RouteLogic(DirectionalElement, GridElement):
    def __init__(self, width, height, in_out_pos, conveyor, inserter, assembler):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)

        # Domain of values route variables can be assigned to (width*height)
        self.domain = width * height
        self.n_bits = math.ceil(math.log2(self.domain))

        # Reference to the conveyor direction variable
        self.conveyor = conveyor

        # Reference to the inserter direction variable
        self.inserter = inserter

        # Reference to the assembler collision variable
        self.assembler = assembler

        # Z3 variable representing the path of a route
        self.route = [[BitVec(f"R_{i}_{j}", self.n_bits) for i in range(self.width)] for j in range(self.height)]

    def domain_constraint(self):
        return [ULE(self.route[i][j], self.domain - 1)
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
                for pos in self.input]

    def route_end(self):
        # Each output cell must have a larger value than 1, and it must be a conveyor
        return [And(UGT(self.route[pos[0]][pos[1]], 1),
                    self.conveyor[pos[0]][pos[1]] != self.direction[0])
                for pos in self.output]

    def forward_consistency(self):
        forward_consistency = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_output(i, j):
                    inserter_output = []
                    conveyor_output = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            # A route cell must have at least one cell route greater than or equal to itself (Output)
                            conveyor_output.append(If(self.conveyor[i][j] == self.direction[direction],
                                                      UGT(self.route[x][y], self.route[i][j]), False))

                            # Route continues
                            inserter_output.append(If(And(self.inserter[i][j] == self.direction[direction],
                                                          self.assembler[x][y] == 0),
                                                      UGT(self.route[x][y], self.route[i][j]), False))

                            # Route ends because the inserter is inputting items to the assembler
                            inserter_output.append(If(And(self.inserter[i][j] == self.direction[direction],
                                                          self.assembler[x][y] != 0),
                                                      self.route[x][y] == 0, False))

                    forward_consistency.append(
                        If(UGT(self.route[i][j], 0), Or(conveyor_output + inserter_output), True))
        return forward_consistency

    def backward_consistency(self):
        backward_consistency = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    inserter_input = []
                    conveyor_input = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            conveyor_input.append(If(And(self.conveyor[i][j] != self.direction[direction],
                                                         self.conveyor[i][j] != self.direction[0]),
                                                     And(ULT(self.route[x][y], self.route[i][j]),
                                                         UGT(self.route[x][y], 0)),
                                                     False))

                            inserter_input.append(If(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                         self.assembler[x][y] == 0),
                                                     And(ULT(self.route[x][y], self.route[i][j]),
                                                         UGT(self.route[x][y], 0)),
                                                     False))

                            # Route start because inserter is taking input from an assembler
                            inserter_input.append(If(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                         self.assembler[x][y] != 0),
                                                     self.route[i][j] == 1,
                                                     False))

                    backward_consistency.append(If(UGT(self.route[i][j], 0), Or(conveyor_input + inserter_input), True))
        return backward_consistency

    def constraints(self):
        return self.route_start() + \
            self.part_of_route() + \
            self.domain_constraint() + \
            self.route_end() + \
            self.forward_consistency() + \
            self.backward_consistency()

    def optimize_criteria(self):
        return sum([If(self.route[i][j] == 0, 0, 1) for i in range(self.height) for j in range(self.width)])
