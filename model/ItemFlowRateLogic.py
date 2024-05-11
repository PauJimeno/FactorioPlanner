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


        # Z3 variables that represent the rate of items/min a cell recives and outputs
        self.input_flow_rate = [[Real(f"INPUT_FLOW_RATE_{i}_{j}") for i in range(width)] for j in range(height)]
        self.output_flow_rate = [[Real(f"OUTPUT_FLOW_RATE_{i}_{j}") for i in range(width)] for j in range(height)]

    def item_input_rate(self):
        # The input cells rate is the rate specified in the input coordinates
        return [self.input_flow_rate[coord[0]][coord[1]] == self.input_rate(coord[0], coord[1]) for coord in self.input]

    def part_of_route(self):
        return [Implies(self.route[i][j] == 0, And(self.input_flow_rate[i][j] == 0, self.output_flow_rate[i][j] == 0))
                for i in range(self.height) for j in range(self.width)]

    def belt_item_flow_propagation(self):
        belt_flow_rate_propagation = []

        for i in range(self.height):
            for j in range(self.width):
                belt_input_cells = []
                belt_output_cells = []
                for direction in range(1, self.n_dir):
                    x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                    if 0 <= x < self.height and 0 <= y < self.width:
                        # Valor de sortida de les caselles que aporten items a la casella central
                        belt_input_cells.append(If(And(self.conveyor[i][j] != self.direction[direction],
                                                    Or(self.conveyor[x][y] == self.opposite_dir[direction],
                                                       self.inserter[x][y] == self.opposite_dir[direction])),
                                                    self.output_flow_rate[x][y], 0))
                        # Valor d'entrada de les caselles que agafen items de la casella central
                        belt_output_cells.append(If(self.inserter[x][y] == self.direction[direction],
                                                    self.input_flow_rate[x][y], 0))

                # L'entrada d'una cinta és la suma de sortides de les caselles adjacents que aporten items
                if not self.is_input(i, j):
                    belt_flow_rate_propagation.append(Implies(self.conveyor[i][j] != self.direction[0],
                                                              And(self.input_flow_rate[i][j] == sum(belt_input_cells), self.input_flow_rate[i][j]<=450)))
                # La sortida d'una cinta és la seva entrada menys la suma d'entrada de les caselles adjacents que prenen items
                belt_flow_rate_propagation.append(Implies(self.conveyor[i][j] != self.direction[0],
                                                          self.output_flow_rate[i][j] == (self.input_flow_rate[i][j] - sum(belt_output_cells))))
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
                            # L'entrada d'un inserter ha de ser mes petita o igual a 50 en cas que l'entrada de la casella d'on agafa items li entrin 50 o més items
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                        self.input_flow_rate[x][y] >= 50),
                                                        And(self.input_flow_rate[i][j] == 50, self.output_flow_rate[i][j] == 50)))
                            # L'entrada d'un inserter ha de ser mes petita o igual a l'entrada de la casella d'on agafa si l'entrada d'aquesta és mes petita que 50
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                               self.input_flow_rate[x][y] < 50, self.route[x][y] != 0), # La ruta ha de ser != 0 (no esta agafant d'un assembler)
                                                           And(self.input_flow_rate[i][j] == self.input_flow_rate[x][y], self.output_flow_rate[i][j] == self.input_flow_rate[x][y])))
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                                    self.route[x][y] == 0), And(self.input_flow_rate[i][j] == self.output_flow_rate[i][j], self.input_flow_rate[i][j]<=50, self.input_flow_rate[i][j]>=0, self.output_flow_rate[i][j]<=50, self.output_flow_rate[i][j]>=0)))

                    inserter_item_flow_propagation.append(Implies(self.inserter[i][j] != self.direction[0], And(inserter_input_cells)))
        return inserter_item_flow_propagation

    def constraints(self):
        return self.item_input_rate() + self.belt_item_flow_propagation() + self.inserter_item_flow_propagation() + self.part_of_route()

    def max_output(self):
        return self.output_flow_rate[self.output[0][0]][self.output[0][1]]





