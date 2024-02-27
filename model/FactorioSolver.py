from PIL import ImageDraw
from z3 import *
from PIL import Image
import time

from model.ConveyorLogic import ConveyorLogic
from model.FactoryLogic import FactoryLogic
from model.InserterLogic import InserterLogic
from model.RouteLogic import RouteLogic


class FactorioSolver:
    def __init__(self, blueprint_width, blueprint_height, input_pos, output_pos):
        self.width = blueprint_width
        self.height = blueprint_height

        # Z3 solver declaration
        self.s = Optimize()

        # Solution found variable
        self.has_solution = False

        self.model_variables = {}

        self.initialize_model_constraints(blueprint_width, blueprint_height, input_pos, output_pos)

    def initialize_model_constraints(self, blueprint_width, blueprint_height, input_pos, output_pos):
        dir_type, directions = EnumSort('direction', ['empty', 'north', 'east', 'south', 'west'])

        conveyor_behaviour = ConveyorLogic(blueprint_width, blueprint_height, input_pos, output_pos, dir_type, directions)
        inserter_behaviour = InserterLogic(blueprint_width, blueprint_height, conveyor_behaviour.conveyor, input_pos, output_pos, dir_type, directions)
        conveyor_behaviour.set_inserter(inserter_behaviour.inserter)
        route_behaviour = RouteLogic(blueprint_width, blueprint_height, input_pos, output_pos, conveyor_behaviour.conveyor,
                                     inserter_behaviour.inserter, directions)

        factory_behavior = FactoryLogic(blueprint_width, blueprint_height, conveyor_behaviour.conveyor,
                                        inserter_behaviour.inserter, directions)

        self.model_variables.update({"CONVEYOR": conveyor_behaviour.conveyor})
        self.model_variables.update({"ROUTE": route_behaviour.route})
        self.model_variables.update({"INSERTER": inserter_behaviour.inserter})

        self.s.add(conveyor_behaviour.constraints()
                   + route_behaviour.constraints()
                   + inserter_behaviour.constraints()
                   + factory_behavior.constraints()
                   )

        # Maximize the objective function
        self.s.maximize(route_behaviour.optimize_criteria())

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

        return self.has_solution

    def model_to_string(self):
        if self.has_solution:
            m = self.s.model()
            for var_name, var_value in self.model_variables.items():
                print(var_name)
                for i in range(self.height):
                    for j in range(self.width):
                        print(m[var_value[i][j]], end=' ')
                    print()
        else:
            print("No model was found")

    def model_to_image(self):
        if self.has_solution:
            inserter_img = Image.open('sprites/inserter.png').convert("RGBA")
            belt_img = Image.open('sprites/conveyor.png').convert("RGBA")

            game_map = self.map_variables()

            # Create a new image with white background
            game_map_img = Image.new('RGBA', (len(game_map[0]) * belt_img.width, len(game_map) * belt_img.height),
                                     (255, 255, 255, 255))
            draw = ImageDraw.Draw(game_map_img)

            # Draw the grid
            for i in range(0, game_map_img.width, belt_img.width):
                draw.line([(i, 0), (i, game_map_img.height)], fill="gray")
            for i in range(0, game_map_img.height, belt_img.height):
                draw.line([(0, i), (game_map_img.width, i)], fill="gray")

            # Draw the right and bottom lines
            draw.line([(game_map_img.width - 1, 0), (game_map_img.width - 1, game_map_img.height)], fill="gray")
            draw.line([(0, game_map_img.height - 1), (game_map_img.width, game_map_img.height - 1)], fill="gray")

            for i in range(len(game_map)):
                for j in range(len(game_map[0])):
                    if game_map[i][j] is not None:
                        element, direction = game_map[i][j].split(':')
                        if element == 'CONV':
                            img = belt_img.rotate(int(direction))
                        if element == 'INSE':
                            img = inserter_img.rotate(int(direction))
                        game_map_img.paste(img, (j * img.width, i * img.height), mask=img)

            game_map_img.save('model_image/game_map_model.png')
        else:
            print("No model was found")

    def map_variables(self):
        game_map = [[None for i in range(self.width)] for j in range(self.height)]
        direction = {
            'empty': "empty",
            'north': 0,     # North
            'east': -90,   # East
            'south': -180,  # South
            'west': -270   # West
        }
        model = self.s.model()

        # Conveyors
        for i in range(self.height):
            for j in range(self.width):
                conveyor = str(model[self.model_variables['CONVEYOR'][i][j]]).strip('\"')
                if conveyor != 'empty' and conveyor != 'None':
                    game_map[i][j] = f"CONV:{direction[conveyor]}"

        # Inserters
        for i in range(self.height):
            for j in range(self.width):
                inserter = str(model[self.model_variables['INSERTER'][i][j]]).strip('\"')
                if inserter != 'empty' and inserter != 'None':
                    game_map[i][j] = f"INSE:{direction[inserter]}"

        return game_map
