from z3 import *


class InserterLogic:
    def __init__(self, blueprint_width, blueprint_height, route_start_end, conveyor_logic):
        # Width and height of the blueprint
        self.width = blueprint_width
        self.height = blueprint_height

        # Start and end positions of each route
        self.route_pos = route_start_end

        # Reference to the conveyor logic class
        self.conveyor = conveyor_logic.surface_conveyor

        # Domain of values inserters variables can be assigned to (0, 1, 2, 3, 4)
        self.domain = 5
        self.n_bits = math.ceil(math.log2(self.domain))

        # Encoded directions and the relative offset they represent
        self.directions = {
            1: (-1, 0), # North
            2: (0, 1),  # East
            3: (1, 0),  # South
            4: (0, -1)  # West
        }

        # Returns the opposite direction of the direction key
        self.opposite_dir = {
            1: 3,  # North -> South
            2: 4,  # East  -> West
            3: 1,  # South -> North
            4: 2   # West  -> East
        }

        # Z3 variable representing the positions an inserter might be and the directions it is pointing
        self.inserter = [[BitVec(f"INS_{i}_{j}", self.n_bits) for i in range(self.width)] for j in range(self.height)]

    def domain_constraint(self):
        return [And(UGE(self.inserter[i][j], 0), ULE(self.inserter[i][j], len(self.directions)))
                for i in range(self.height) for j in range(self.width)]

    def not_outside(self):
        row_limits = [And(self.inserter[i][0] != 4, self.inserter[i][self.width-1] != 2,
                          self.inserter[i][0] != 2, self.inserter[i][self.width-1] != 4)
                      for i in range(self.height)]
        col_limits = [And(self.inserter[0][j] != 1, self.inserter[self.height-1][j] != 3,
                          self.inserter[0][j] != 3, self.inserter[self.height-1][j] != 1)
                      for j in range(self.width)]

        return col_limits + row_limits

    def not_output_to_input(self):
        not_output_to_input = []
        for route in self.route_pos:
            consequence = []
            for direction in self.directions:
                x, y = route[0][0] + self.directions[direction][0], route[0][1] + self.directions[direction][1]
                if 0 <= x < self.height and 0 <= y < self.width:
                    consequence.append(self.inserter[x][y] != self.opposite_dir[direction])
            not_output_to_input.append(And(consequence))

        return not_output_to_input

    def connected(self):
        correctly_connected = []
        for i in range(self.height):
            for j in range(self.width):
                consequence = []
                for direction in self.directions:
                    x, y = i + self.directions[direction][0], j + self.directions[direction][1]
                    if 0 <= x < self.height and 0 <= y < self.width:
                        consequence.append(
                            Or(And(self.inserter[i][j] != direction,
                                   self.inserter[i][j] != self.opposite_dir[direction]),
                               And(UGT(self.conveyor[x][y], 0),
                                   self.conveyor[x][y] != (self.inserter[x][y] + 2) % 4 + 1)
                               ))
                correctly_connected.append(Implies(UGT(self.inserter[i][j], 0), And(consequence)))

        return correctly_connected

    def constraints(self):
        return self.domain_constraint() + self.not_outside() + self.not_output_to_input() + self.connected()

