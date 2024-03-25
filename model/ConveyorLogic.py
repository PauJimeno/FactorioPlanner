from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class ConveyorLogic(DirectionalElement, GridElement):
    def __init__(self, width, height, in_out_pos):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)
        self.conveyor = [[Const(f"S_CONV_{i}_{j}", DirectionalElement.dir_type)
                          for i in range(width)] for j in range(height)]

    def conveyor_input(self):
        conveyor_input = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            direction_clauses.append(If(self.conveyor[i][j] != self.direction[direction],
                                                        Or(self.conveyor[x][y] == self.opposite_dir[direction],
                                                           self.inserter[x][y] == self.opposite_dir[direction]),
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
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            direction_clauses.append(If(self.conveyor[i][j] == self.direction[direction], Or(
                                                        And(self.conveyor[x][y] != self.direction[0],
                                                            self.conveyor[x][y] != self.opposite_dir[direction]),
                                                        And(self.inserter[x][y] != self.direction[0],
                                                            self.inserter[x][y] == self.direction[direction])
                                                        ),
                                                        False))
                    conveyor_output.append(If(self.conveyor[i][j] != self.direction[0], Or(direction_clauses), True))

        return conveyor_output

    def end_of_route(self):
        # An output cell cant carry the items to any other cell (end of route)
        end_of_route = []
        for pos in self.output:
            i = pos[0]
            j = pos[1]
            direction_clauses = []
            for direction in range(1, self.n_dir):
                x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                if 0 <= x < self.height and 0 <= y < self.width:
                    direction_clauses.append(If(self.conveyor[i][j] == self.direction[direction],
                                                self.conveyor[x][y] == self.direction[0], True))
            end_of_route.append(And(direction_clauses))

        return end_of_route

    def constraints(self):
        return self.conveyor_input() + self.conveyor_output() + self.end_of_route()

    def set_inserter(self, inserter):
        self.inserter = inserter
