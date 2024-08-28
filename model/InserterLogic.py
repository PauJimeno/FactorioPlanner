from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class InserterLogic(DirectionalElement, GridElement):
    """
    This class contains all the constraints that implement the logic of the inserters.
    Note that all the constraints of the model are explained in detail in the project report.

    :param width: Width of the blueprint
    :type width: Int

    :param height: Height of the blueprint
    :type height: Int

    :param conveyor: reference to the variable conveyor
    :type conveyor: Array[Array] EnumSort

    :param assembler: reference to the collision variable of the assembler
    :type assembler: Array[Array] EnumSort

    :param in_out_pos: Contains the input and output positions and type of item carrying
    :type in_out_pos: Dictionary
    """

    def __init__(self, width, height, conveyor, assembler, in_out_pos):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)

        # Inserter variable for each cell of enumerated type "dir_type"
        self.inserter = [[Const(f"INS_{i}_{j}", DirectionalElement.dir_type)
                          for i in range(width)] for j in range(height)]

        self.conveyor = conveyor
        self.assembler = assembler

    def inserter_input(self):
        """
        Creates the constraint that ensures the input of an inserter is a valid element,
        the cell the inserter takes input can only be a conveyor pointing any direction
        or an assembler
        
        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
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

    def prevent_redundant_inserter(self):
        """
        Creates the constraint prevents redundant combination between inserters and conveyors,
        precisely when the output of an inserter is a conveyor pointing the same direction as 
        the inserter
        
        :return: List with all the logic regarding the constraint
        :rtype: Array
        """
        redundant_inserter = []

        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    direction_clauses = []
                    for direction in range(1, self.n_dir):
                        in_x, in_y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        out_x, out_y = i + self.displacement[self.opposite_num_dir[direction]][0], j + \
                                       self.displacement[self.opposite_num_dir[direction]][1]
                        if 0 <= in_x < self.height and 0 <= in_y < self.width and 0 <= out_x < self.height and 0 <= out_y < self.width:
                            direction_clauses.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                                 self.inserter[i][j] == self.conveyor[in_x][in_y]),
                                                             self.conveyor[out_x][out_y] == self.direction[0]))
                    redundant_inserter.append(Implies(self.inserter[i][j] != self.direction[0], And(direction_clauses)))

        return redundant_inserter

    def inserter_output(self):
        """
        Creates the constraint that ensures the output of an inserter is a valid element,
        the output cell of an inserter can only be a conveyor pointing a direction that it's
        not the opposite direction of the inserter, or an assembler.
        
        :return: List with all the logic regarding the constraint
        :rtype: Array
        """
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
        """
        Creates a list of all the constraints representing the logic of the class

        :return: all the constraint of the class logic in a single array
        :rtype: Array
        """
        return self.inserter_input() + self.inserter_output() + self.prevent_redundant_inserter()
