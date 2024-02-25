from z3 import *

# Mirar millors maneres d'implmentar dominis finits


class ConveyorLogic:
    def __init__(self, width, height, dir_type):
        self.conveyor = [[Const(f"S_CONV_{i}_{j}", dir_type) for i in range(width)] for j in range(height)]

