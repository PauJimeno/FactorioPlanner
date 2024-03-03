from z3 import *


class FactoryLogic:
    def __init__(self, blueprint_width, blueprint_height, conveyor, inserter, assembler, direction):
        self.conveyor = conveyor
        self.inserter = inserter
        self.assembler = assembler
        self.width = blueprint_width
        self.height = blueprint_height
        self.direction = direction

    def collision(self):
        return [PbLe([(self.inserter[i][j] != self.direction[0], 1), (self.conveyor[i][j] != self.direction[0], 1)], 1)
                for i in range(self.height) for j in range(self.width)] +\
                [If(Or(self.inserter[i][j] != self.direction[0], self.conveyor[i][j] != self.direction[0]),
                    self.assembler[i][j] == 0, True)
                 for i in range(self.height) for j in range(self.width)]

    def constraints(self):
        return self.collision()



