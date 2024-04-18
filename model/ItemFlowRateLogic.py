from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class ItemFlowRateLogic(DirectionalElement, GridElement):
    def __init__(self, width, height, in_out_pos, inserter, conveyor, route):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)

        self.conveyor = conveyor
        self.inserter = inserter
        self.route = route

        # Z3 variable that represents the rate of items/min a cell is transporting
        self.item_flow_rate = [[Real(f"ITEM_RATE_{i}_{j}") for i in range(width)] for j in range(height)]

    def domain_constraint(self):
        return[And(self.item_flow_rate[i][j] >= 0, self.item_flow_rate[i][j] <= 450)
               for i in range(self.height) for j in range(self.width)]

    def part_of_route(self):
        return [Implies(Not(UGT(self.route[i][j], 0)), self.item_flow_rate[i][j] == 0)
                for i in range(self.height) for j in range(self.width)]

    def item_input_rate(self):
        # The input cells rate is the rate specified in the input coordinates
        return [self.item_flow_rate[coord[0]][coord[1]] == self.input_rate(coord[0], coord[1]) for coord in self.input]

    def belt_item_flow_propagation(self):
        belt_flow_rate_propagation = []

        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    belt_input_cells = []
                    belt_output_cells = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            belt_input_cells.append(If(And(self.conveyor[i][j] != self.direction[direction],
                                                        Or(self.conveyor[x][y] == self.opposite_dir[direction],
                                                           self.inserter[x][y] == self.opposite_dir[direction])),
                                                        self.item_flow_rate[x][y], 0))
                            belt_output_cells.append(If(And(self.conveyor[i][j] != self.opposite_dir[direction],
                                                        self.inserter[x][y] == self.direction[direction]),
                                                        self.item_flow_rate[x][y], 0))
                    belt_flow_rate_propagation.append(Implies(self.conveyor[i][j] != self.direction[0], self.item_flow_rate[i][j] == sum(belt_input_cells) - sum(belt_output_cells)))
        return belt_flow_rate_propagation

    def inserter_item_flow_propagation(self):
        inserter_item_flow_propagation = []

        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    inserter_input_cells = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                        self.item_flow_rate[x][y] >= 50),
                                                        self.item_flow_rate[i][j] == 50))
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                               self.item_flow_rate[x][y] < 50, self.route[x][y] != 0), # La ruta ha de ser != 0 (no esta agafant d'un assembler)
                                                           self.item_flow_rate[i][j] == self.item_flow_rate[x][y]))
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                                    self.route[x][y] == 0),
                                                                # La ruta ha de ser == 0 (esta agafant d'un assembler)
                                                                self.item_flow_rate[i][j] <= 50))
                    inserter_item_flow_propagation.append(Implies(self.inserter[i][j] != self.direction[0], And(inserter_input_cells)))
        return inserter_item_flow_propagation

    def constraints(self):
        return self.item_input_rate() + self.belt_item_flow_propagation() + self.inserter_item_flow_propagation() + self.domain_constraint() + self.part_of_route()

    def max_output(self):
        return self.item_flow_rate[self.output[0][0]][self.output[0][1]]





