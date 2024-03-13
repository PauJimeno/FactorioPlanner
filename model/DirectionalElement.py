from abc import ABC, abstractmethod
from z3 import *


class DirectionalElement(ABC):
    # Abstract class that implements shared behaviours between directional elements in the model
    dir_type, direction = EnumSort('direction', ['empty', 'north', 'east', 'south', 'west'])

    def __init__(self):
        self.displacement = {
            1: (-1, 0),  # North
            2: (0, 1),   # East
            3: (1, 0),   # South
            4: (0, -1)   # West
        }

        self.opposite_dir = {
            1: self.direction[3],  # North -> South
            2: self.direction[4],  # East  -> West
            3: self.direction[1],  # South -> North
            4: self.direction[2]   # West  -> East
        }

        self.n_dir = 5  # (north, east, south, west, empty)
