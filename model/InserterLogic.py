from z3 import *


class InserterLogic:
    def __init__(self, width, height, dir_type):
        self.inserter = [[Const(f"INS_{i}_{j}", dir_type) for i in range(width)] for j in range(height)]


