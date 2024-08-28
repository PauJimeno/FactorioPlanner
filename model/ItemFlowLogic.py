from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement
from model.RecipeElement import RecipeElement


class ItemFlowLogic(DirectionalElement, GridElement, RecipeElement):
    """
    This class contains all the constraints that implement the logic of the flow of items.
    Note that all the constraints of the model are explained in detail in the project report.

    :param width: Width of the blueprint
    :type width: Int

    :param height: Height of the blueprint
    :type height: Int

    :param route: reference to the route variable
    :type route: Arrat[Array] EnumSort

    :param conveyor: reference to the variable conveyor
    :type conveyor: Arrat[Array] EnumSort

    :param inserter: reference to the inserter variable
    :type inserter: Arrat[Array] EnumSort

    :param in_out_pos: Contains the input and output positions and type of item carrying
    :type in_out_pos: Dictionary

    :param recipes: Contains the recipes that the assemblers in the blueprint will use, for each recipe it has a list
                    of the items it requires and which rate in items/min needs and the outputting item and rate.
    :type recipes: Dictionary
    """

    def __init__(self, width, height, route, inserter, conveyor, in_out_pos, recipes):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)
        RecipeElement.__init__(self, recipes)

        self.route = route
        self.inserter = inserter
        self.conveyor = conveyor

        self.item_bits = math.ceil(math.log2(self.max_items + 1))

        # Z3 variable that represents what item is present in each blueprint cell
        self.item_flow = [[BitVec(f"ITEM_FLOW_{i}_{j}", self.item_bits)
                           for i in range(width)] for j in range(height)]

    def domain_constraint(self):
        """
        Creates a constraint that ensures teh variable item_flow
        only takes values inside the domain [0..self.max_items]
        
        :return: List with all the logic regarding the constraint
        :rtype: Array
        """
        return [ULE(self.item_flow[i][j], self.max_items)
                for i in range(self.height) for j in range(self.width)]

    def part_of_route(self):
        """
        If a cell is part of route, then that cell must carry an item

        :return: List with all the logic regarding the constraint
        :rtype: Array
        """
        return [(UGT(self.route[i][j], 0)) == (UGT(self.item_flow[i][j], 0))
                for i in range(self.height) for j in range(self.width)]

    def item_input(self):
        """
        The input cells carry the item specified in the input coordinates

        :return: List with all the logic regarding the constraint
        :rtype: Array
        """

        input_items = []
        for coord in self.input:
            input_items.append(
                self.item_flow[coord[0]][coord[1]] == self.model_item_id(self.input_item(coord[0], coord[1])))
        return input_items

    def item_output(self):
        """
        The input cells carry the item specified in the input coordinates

        :return: List with all the logic regarding the constraint
        :rtype: Array
        """

        output_items = []
        for coord in self.output:
            output_items.append(
                self.item_flow[coord[0]][coord[1]] == self.model_item_id(self.output_item(coord[0], coord[1])))
        return output_items

    def item_carry(self):
        """
        Creates a constraint that encode the behaviour of how items are
        carryed between cells that transport them.
        If a cell contains an inserter or a conveyor, its item_flow value will propagate
        to the cell its pointing. Also, if the cell has an inserter, the item_flow value
        will not be propagated if the output of the inserter is an assembler.

        :return: List with all the logic regarding the constraint
        :rtype: Array
        """
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
                            inserter_carry.append(Implies(
                                And(self.inserter[i][j] == self.opposite_dir[direction], UGT(self.route[x][y], 0)),
                                self.item_flow[i][j] == self.item_flow[x][y]))
                            # An inserter puts items to the neighbouring cell it is pointing to
                            inserter_carry.append(
                                Implies(And(self.inserter[i][j] == self.direction[direction], UGT(self.route[x][y], 0)),
                                        self.item_flow[x][y] == self.item_flow[i][j]))
                        if not self.is_output(i, j):
                            # A conveyor puts items to the neighbouring cell it is pointing to
                            conveyor_carry.append(Implies(self.conveyor[i][j] == self.direction[direction],
                                                          self.item_flow[x][y] == self.item_flow[i][j]))
                # Tot i que la implicació és redundant ja que inserter i conveyor carry forcen que les direccions
                # estiguin entre 1-4, la implicació reduieix el temps de solving
                item_carry_conveyor.append(Implies(self.conveyor[i][j] != self.direction[0], And(conveyor_carry)))
                item_carry_inserter.append(Implies(self.inserter[i][j] != self.direction[0], And(inserter_carry)))

        return item_carry_inserter + item_carry_conveyor

    def constraints(self):
        """
        Creates a list of all the constraints representing the logic of the class

        :return: all the constraint of the class logic in a single array
        :rtype: Array
        """
        return self.part_of_route() + self.item_input() + self.item_output() + self.domain_constraint() + self.item_carry()
