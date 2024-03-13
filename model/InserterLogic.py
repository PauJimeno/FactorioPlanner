from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class InserterLogic(DirectionalElement, GridElement):
    def __init__(self, width, height, conveyor, assembler, in_out_pos):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)

        # Inserter variable for each cell of enumerated type "dir_type"
        self.inserter = [[Const(f"INS_{i}_{j}", DirectionalElement.dir_type)
                          for i in range(width)] for j in range(height)]

        self.conveyor = conveyor
        self.assembler = assembler

    def inserter_input(self):
        inserter_input = []

        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            if not self.is_output(x, y):
                                # The inserter can take input from a conveyor or an assembler
                                direction_clauses.append(If(self.inserter[i][j] == self.opposite_dir[direction],
                                                            Or(self.conveyor[x][y] != self.direction[0],
                                                               self.assembler[x][y] != 0),
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
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            # Inserter can output to a conveyor or an assembler
                            direction_clauses.append(If(self.inserter[i][j] == self.direction[direction],
                                                        Or(And(self.conveyor[x][y] != self.direction[0],
                                                           self.conveyor[x][y] != self.opposite_dir[direction]),
                                                        self.assembler[x][y] != 0),
                                                     False))
                    inserter_output.append(If(self.inserter[i][j] != self.direction[0], Or(direction_clauses), True))

        return inserter_output

    def constraints(self):
        return self.inserter_input() + self.inserter_output()


