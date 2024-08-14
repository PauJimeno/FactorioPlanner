from z3 import *


class DirectionalElement:
    """
    Abstract class that implements shared behaviours between directional elements in the model
    """
    # The EnumSort type is a global variabel of the class because there can only be one declaration of the same type
    dir_type, direction = EnumSort('direction', ['empty', 'north', 'east', 'south', 'west'])

    def __init__(self):
        # Position relative to (0,0) after moving in each direction
        self.displacement = {
            1: (-1, 0),  # North
            2: (0, 1),   # East
            3: (1, 0),   # South
            4: (0, -1)   # West
        }

        # Opposite position relative to (0,0) after moving in each direction
        self.opposite_dir = {
            1: self.direction[3],  # North -> South
            2: self.direction[4],  # East  -> West
            3: self.direction[1],  # South -> North
            4: self.direction[2]   # West  -> East
        }

        # Opposite direction for each direction
        self.opposite_num_dir = {
            1: 3,  # North -> South
            2: 4,  # East  -> West
            3: 1,  # South -> North
            4: 2   # West  -> East
        }

        self.n_dir = 5  # (north, east, south, west, empty)
