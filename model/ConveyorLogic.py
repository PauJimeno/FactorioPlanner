from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class ConveyorLogic(DirectionalElement, GridElement):
    """
    This class contains all the constraints that implement the logic of the conveyors.
    Note that all the constraints of the model are explained in detail in the project report.

    :param width: Width of the blueprint
    :type width: Int

    :param height: Height of the blueprint
    :type height: Int

    :param in_out_pos: Contains the input and output positions and type of item carrying
    :type in_out_pos: Dictionary
    """
    def __init__(self, width, height, in_out_pos):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)
        self.conveyor = [[Const(f"S_CONV_{i}_{j}", DirectionalElement.dir_type)
                          for i in range(width)] for j in range(height)]

    def conveyor_input(self):
        """
        Creates the constraint that ensures the input of a conveyor is a valid element,
        in all the three valid input positions of a conveyor there can only be inserters or other convetors pointing towards it
        
        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
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
        """
        Creates the constraint that ensures the output of a conveyor is a valid element,
        the output cell of a conveyor can only be another conveyor that is not pointing to it, or an
        inserter pointing in the same direction of the conveyor.
        
        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
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
        """
        Creates the constraint that ensures the conveyor at the output of the blueprint doesn't have any other
        conveyor in the direction its pointing.
        
        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
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
        """
        Creates a list of all the constarints representing the logic of the class

        :return: all the constraint of the class logic in a single array
        :rtype: Array
        """
        return self.conveyor_input() + self.conveyor_output() + self.end_of_route()

    def set_inserter(self, inserter):
        """
        Setter of the variable inserter

        :param inserter: reference to the variable inserter
        :type inserter: Arrat[Array] EnumSort
        """
        self.inserter = inserter
