from z3 import *
from PIL import Image
import time

from model.ConveyorLogic import ConveyorLogic
from model.InserterLogic import InserterLogic
from model.RouteLogic import RouteLogic


class FactorioSolver:
    def __init__(self, blueprint_width, blueprint_height, route_pos):
        self.width = blueprint_width
        self.height = blueprint_height

        # Z3 solver declaration
        self.s = Solver()

        # Solution found variable
        self.has_solution = False

        self.model_variables = {}

        self.initialize_model_constraints(blueprint_width, blueprint_height, route_pos)

    def initialize_model_constraints(self, blueprint_width, blueprint_height, route_pos):
        conveyor_behaviour = ConveyorLogic(blueprint_width, blueprint_height, route_pos)
        route_behaviour = RouteLogic(blueprint_width, blueprint_height, route_pos, conveyor_behaviour)
        inserter_behaviour = InserterLogic(blueprint_width, blueprint_height, route_pos, conveyor_behaviour)

        self.model_variables.update({"CONVEYOR": conveyor_behaviour.surface_conveyor})
        self.model_variables.update({"ROUTE": route_behaviour.route})
        self.model_variables.update({"INSERTER": inserter_behaviour.inserter})

        self.s.add(conveyor_behaviour.constraints() + route_behaviour.constraints() + inserter_behaviour.constraints())

    def find_solution(self):
        start = time.time()
        self.has_solution = self.s.check() == sat
        computing_time = time.time() - start
        if self.has_solution:
            print("Solution found (SAT)")
        else:
            print("No solution was found (UNSAT)")
        print("Computing time: ", computing_time)
        print("Solver statistics: ")
        print(self.s.statistics())

    def model_to_string(self):
        if self.has_solution:
            m = self.s.model()
            num_digits = len(str("00"))

            for var_name, var_value in self.model_variables.items():
                print(var_name)
                for i in range(self.height):
                    for j in range(self.width):
                        print("{:>{}}".format(m[var_value[i][j]].as_long(), num_digits), end=' ')
                    print()
        else:
            print("No model was found")

    def model_to_image(self):
        # inserters_img = Image.open('sprites/inserters.png')
        belts_img = Image.open('sprites/conveyor.png')

        game_map = self.map_variables()

        game_map_img = Image.new('RGB', (len(game_map[0]) * belts_img.width, len(game_map) * belts_img.height), 'white')

        for i in range(len(game_map)):
            for j in range(len(game_map[0])):
                if game_map[i][j] is not None:
                    element, direction = game_map[i][j].split(':')
                    if element == 'CONV':
                        img = belts_img.rotate(int(direction))
                    game_map_img.paste(img, (j * img.width, i * img.height))

        game_map_img.save('ModelImages/game_map_model.png')

    def map_variables(self):
        game_map = [[None for i in range(self.width)] for j in range(self.height)]
        direction = {
            0: "empty",
            1: 0,   # North
            2: -90,  # East
            3: -180, # South
            4: -270  # West
        }
        model = self.s.model()

        # Conveyors
        for i in range(self.height):
            for j in range(self.width):
                conveyor = model[self.model_variables['CONVEYOR'][i][j]].as_long()
                if conveyor != 0:
                    game_map[i][j] = f"CONV:{direction[conveyor]}"

        return game_map
