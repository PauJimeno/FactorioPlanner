from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement
from model.RecipeElement import RecipeElement


class ItemFlowLogic(DirectionalElement, GridElement, RecipeElement):
    def __init__(self, width, height, route, inserter, conveyor, in_out_pos, recipes):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)
        RecipeElement.__init__(self, recipes)

        self.route = route
        self.inserter = inserter
        self.conveyor = conveyor

        self.item_bits = math.ceil(math.log2(self.max_items+1))

        # Z3 variable that represents what item is present in each blueprint cell
        self.item_flow = [[BitVec(f"ITEM_FLOW_{i}_{j}", self.item_bits)
                          for i in range(width)] for j in range(height)]

    def domain_constraint(self):
        return[ULE(self.item_flow[i][j], self.max_items)
               for i in range(self.height) for j in range(self.width)]

    def part_of_route(self):
        # If a cell is part of route, then that cell must carry an item
        return [(UGT(self.route[i][j], 0)) == (UGT(self.item_flow[i][j], 0))
                for i in range(self.height) for j in range(self.width)]

    def item_input(self):
        # The input cells carry the item specified in the input coordinates
        input_items = []
        for coord in self.input:
            input_items.append(self.item_flow[coord[0]][coord[1]] == self.model_item_id(self.input_item(coord[0], coord[1])))
        return input_items

    def item_output(self):
        # The input cells carry the item specified in the input coordinates
        output_items = []
        for coord in self.output:
            output_items.append(self.item_flow[coord[0]][coord[1]] == self.model_item_id(self.output_item(coord[0], coord[1])))
        return output_items

    def item_carry(self):
        item_carry_conveyor = []
        item_carry_inserter = []
        for i in range(self.height):
            for j in range(self.width):
                inserter_carry = []
                conveyor_carry = []
                for direction in range(1, self.n_dir):
                    x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                    if 0 <= x < self.height and 0 <= y < self.width:
                        # An inserter takes items from the neighbouring cell pointing to it
                        if not self.is_input(i, j):
                            inserter_carry.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction], UGT(self.route[x][y], 0)),
                                                     self.item_flow[i][j] == self.item_flow[x][y]))
                            # An inserter puts items to the neighbouring cell it is pointing to
                            inserter_carry.append(Implies(And(self.inserter[i][j] == self.direction[direction], UGT(self.route[x][y], 0)),
                                                     self.item_flow[x][y] == self.item_flow[i][j]))
                        if not self.is_output(i, j):
                            # A conveyor puts items to the neighbouring cell it is pointing to
                            conveyor_carry.append(Implies(self.conveyor[i][j] == self.direction[direction],
                                                     self.item_flow[x][y] == self.item_flow[i][j]))
                # Tot i que la implicació és redundant ja que inserter i conveyor carry forcen que les direccions estiguin entre 1-4, la implicació reduieix el temps de solving
                item_carry_conveyor.append(Implies(self.conveyor[i][j] != self.direction[0], And(conveyor_carry)))
                item_carry_inserter.append(Implies(self.inserter[i][j] != self.direction[0], And(inserter_carry)))

        return item_carry_inserter + item_carry_conveyor

    def constraints(self):
        return self.part_of_route() + self.item_input() + self.item_output() + self.domain_constraint() + self.item_carry()



