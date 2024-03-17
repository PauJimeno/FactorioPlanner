from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement
from model.RecipeElement import RecipeElement


class ItemFlowLogic(DirectionalElement, GridElement, RecipeElement):
    def __init__(self, width, height, route, in_out_pos, recipes):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)
        RecipeElement.__init__(self, recipes)

        self.route = route

        self.item_bits = math.ceil(self.max_items)

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
        for coord, item in self.in_out_positions['IN'].items():
            input_items.append(self.item_flow[coord[0]][coord[0]] == self.model_item_id(item))
        return input_items

    def item_output(self):
        # The input cells carry the item specified in the input coordinates
        output_items = []
        for coord, item in self.in_out_positions['OUT'].items():
            output_items.append(self.item_flow[coord[0]][coord[0]] == self.model_item_id(item))
        return output_items

    def item_carry(self):
        # Each cell that is part of a route must carry its item to the neighbour cell with a greater route value
        item_carry = []
        for i in range(self.width):
            for j in range(self.height):
                carry = []
                for direction in range(1, self.n_dir):
                    x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                    if 0 <= x < self.height and 0 <= y < self.width:
                        carry.append(If(UGT(self.route[x][y], self.route[i][j]),
                                        self.item_flow[x][y] == self.item_flow[i][j], True))
                item_carry.append(If(UGT(self.route[i][j], 0), And(carry), True))
        return item_carry

    def constraints(self):
        return self.part_of_route() + self.item_input() + self.item_output() + self.domain_constraint() + self.item_carry()



