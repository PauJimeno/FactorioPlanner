from z3 import *


class RouteLogic:
    def __init__(self, blueprint_width, blueprint_height, route_start_end, conveyor_logic):
        # Width and height of the blueprint
        self.width = blueprint_width
        self.height = blueprint_height

        # Start and end positions of each route
        self.route_pos = route_start_end

        # Domain of values route variables can be assigned to (width+height)
        self.domain = blueprint_width + blueprint_height
        self.n_bits = math.ceil(math.log2(self.domain))

        # Reference to the ConveyorLogic object
        self.conveyor_logic = conveyor_logic
        self.directions = self.conveyor_logic.directions
        self.conveyor = self.conveyor_logic.surface_conveyor
        self.opposite_dir = self.conveyor_logic.opposite_dir

        # Z3 variable representing the path of a route
        self.route = [[BitVec(f"R_{i}_{j}", self.n_bits) for i in range(self.width)] for j in range(self.height)]

    def domain_constraint(self):
        return[And(UGE(self.route[i][j], 0), ULT(self.route[i][j], self.domain))
               for i in range(self.height) for j in range(self.width)]

    def part_of_route(self):
        return [(UGT(self.route[i][j], 0)) == (UGT(self.conveyor_logic.surface_conveyor[i][j], 0))
                for i in range(self.height) for j in range(self.width)]

    def route_start(self):
        return [self.route[pos[0][0]][pos[0][1]] == 1 for pos in self.route_pos]

    def route_increment(self):
        route_increment = []
        for i in range(self.height):
            for j in range(self.width):
                clauses = []
                for direction in self.directions:
                    x, y = i + self.directions[direction][0], j + self.directions[direction][1]
                    if 0 <= x < self.height and 0 <= y < self.width:
                        clauses.append(
                            Implies(And(UGT(self.route[x][y], 0), self.conveyor[x][y] == self.opposite_dir[direction]),
                                    And(UGT(self.route[i][j], self.route[x][y])))
                        )
                route_increment.append(Implies(UGT(self.conveyor[i][j], 0), And(clauses)))

        return route_increment

    def propagate_route(self):
        propagate_route = []
        for i in range(self.height):
            for j in range(self.width):
                for pos in self.route_pos:
                    if i != pos[0][0] or j != pos[0][1]:
                        direction_clauses = []
                        for direction in self.directions:
                            x, y = i + self.directions[direction][0], j + self.directions[direction][1]
                            if 0 <= x < self.height and 0 <= y < self.width:
                                direction_clauses.append(Implies(And(
                                    UGT(self.route[x][y], 0),
                                    self.conveyor[x][y] == self.opposite_dir[direction]),
                                    self.route[i][j] == self.route[x][y] + 1))
                        propagate_route.append(
                            Implies(UGT(self.conveyor[i][j], 0), Or(direction_clauses))
                        )

        return propagate_route

    def constraints(self):
        return self.route_increment() + self.route_start() + self.part_of_route() + self.domain_constraint() + self.propagate_route()
