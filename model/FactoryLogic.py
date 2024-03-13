from z3 import *


class FactoryLogic:
    def __init__(self, width, height, conveyor, inserter, assembler):
        self.conveyor = conveyor.conveyor
        self.conveyor_dir = conveyor.direction
        self.inserter = inserter.inserter
        self.inserter_dir = inserter.direction
        self.assembler = assembler
        self.width = width
        self.height = height

    def collision(self):
        return [PbLe([(self.inserter[i][j] != self.inserter_dir[0], 1),
                      (self.conveyor[i][j] != self.conveyor_dir[0], 1)], 1)
                for i in range(self.height) for j in range(self.width)] +\
                [If(Or(self.inserter[i][j] != self.inserter_dir[0],
                       self.conveyor[i][j] != self.conveyor_dir[0]),
                    self.assembler[i][j] == 0, True)
                 for i in range(self.height) for j in range(self.width)]

    def constraints(self):
        return self.collision()



