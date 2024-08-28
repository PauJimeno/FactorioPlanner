from z3 import *


class FactoryLogic:
    """
    This class conatins the logic that prevents any collisions between all factory elements.

    :param width: Width of the blueprint
    :type width: Int

    :param height: Height of the blueprint
    :type height: Int

    :param conveyor: Reference to the conveyor directions variable
    :type conveyor: Array[Array] EnumSort

    :param inserter: Reference to the inserter directions variable
    :type inserter: Array[Array] EnumSort
    
    :param assembler: Reference to the assembler collision_area variable
    :type assembler: Array[Array] BitVec
    """

    def __init__(self, width, height, conveyor, inserter, assembler):
        self.conveyor = conveyor.conveyor
        self.conveyor_dir = conveyor.direction
        self.inserter = inserter.inserter
        self.inserter_dir = inserter.direction
        self.assembler = assembler
        self.width = width
        self.height = height

    def collision(self):
        """
        Creates a constarint that ensures that all elements of the blueprint (conveyors, inserters and assemblers) don't collide between each other

        :return: the constraint that ensures there can't be any elements in the same cell of the blueprint
        :rtype: Array
        """
        return [PbLe([(self.inserter[i][j] != self.inserter_dir[0], 1),
                      (self.conveyor[i][j] != self.conveyor_dir[0], 1)], 1)
                for i in range(self.height) for j in range(self.width)] + \
            [If(Or(self.inserter[i][j] != self.inserter_dir[0],
                   self.conveyor[i][j] != self.conveyor_dir[0]),
                self.assembler[i][j] == 0, True)
             for i in range(self.height) for j in range(self.width)]

    def constraints(self):
        """
        Creates a list of all the constarints representing the logic of the class

        :return: the constraint that ensures there can't be any elements in the same cell of the blueprint
        :rtype: Array
        """
        return self.collision()
