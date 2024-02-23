from z3 import *


class FactoryLogic:
    def __init__(self, blueprint_width, blueprint_height, conveyor_logic, inserter_logic):
        self.conveyor = conveyor_logic.surface_conveyor
        self.inserter = inserter_logic.inserter
        self.width = blueprint_width
        self.height = blueprint_height

    def collision(self):
        return [PbLe([(UGT(self.inserter[i][j], 0), 1), (UGT(self.conveyor[i][j], 0), 1)], 1)
                for i in range(self.height) for j in range(self.width)]

    def constraints(self):
        return self.collision()



