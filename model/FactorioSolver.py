from PIL import ImageDraw
from z3 import *
from PIL import Image
import time

from model.AssemblerLogic import AssemblerLogic
from model.ConveyorLogic import ConveyorLogic
from model.FactoryLogic import FactoryLogic
from model.InserterLogic import InserterLogic
from model.RouteLogic import RouteLogic


class FactorioSolver:
    def __init__(self, width, height, in_out_pos):
        self.width = width
        self.height = height

        # Z3 solver declaration
        self.s = Optimize()

        # Solution found variable
        self.has_solution = False

        self.model_variables = {}

        start = time.time()
        self.initialize_model_constraints(width, height, in_out_pos)
        computing_time = time.time() - start
        print("Initialization time:", computing_time)

    def initialize_model_constraints(self, blueprint_width, blueprint_height, in_out_pos):
        conveyor_behaviour = ConveyorLogic(blueprint_width, blueprint_height, in_out_pos)
        assembler_behavior = AssemblerLogic(blueprint_width, blueprint_height)
        inserter_behaviour = InserterLogic(blueprint_width, blueprint_height, conveyor_behaviour.conveyor,
                                           assembler_behavior.collision_area, in_out_pos)
        conveyor_behaviour.set_inserter(inserter_behaviour.inserter)
        assembler_behavior.set_inserter(inserter_behaviour.inserter)
        route_behaviour = RouteLogic(blueprint_width, blueprint_height, in_out_pos,
                                     conveyor_behaviour.conveyor,
                                     inserter_behaviour.inserter, assembler_behavior.collision_area)
        factory_behavior = FactoryLogic(blueprint_width, blueprint_height, conveyor_behaviour,
                                        inserter_behaviour, assembler_behavior.collision_area)

        self.model_variables.update({"CONVEYOR": conveyor_behaviour.conveyor})
        self.model_variables.update({"ROUTE": route_behaviour.route})
        self.model_variables.update({"INSERTER": inserter_behaviour.inserter})
        self.model_variables.update({"ASSEMBLER": assembler_behavior.assembler})
        self.model_variables.update({"ASSEMBLER_COLLISION": assembler_behavior.collision_area})

        self.s.add(conveyor_behaviour.constraints()
                   + route_behaviour.constraints()
                   + inserter_behaviour.constraints()
                   + factory_behavior.constraints()
                   + assembler_behavior.constraints()
                   )

        # Minimize the objective function
        self.s.minimize(route_behaviour.optimize_criteria())

    def find_solution(self):
        start = time.time()
        self.has_solution = self.s.check() == sat
        computing_time = time.time() - start
        if self.has_solution:
            print("Solution found (SAT)")
        else:
            print("No solution was found (UNSAT)")
        print("Computing time: ", computing_time)
        # print("Solver statistics: ")
        # print(self.s.statistics())

        return self.has_solution

    def model_to_string(self):
        if self.has_solution:
            m = self.s.model()
            for var_name, var_value in self.model_variables.items():
                print(var_name)
                height, width = len(var_value), len(var_value[0])
                for i in range(height):
                    for j in range(width):
                        print(m[var_value[i][j]], end=' ')
                    print()
        else:
            print("No model was found")

    def model_to_image(self):
        if self.has_solution:
            inserter_img = Image.open('sprites/inserter.png').convert("RGBA")
            belt_img = Image.open('sprites/conveyor.png').convert("RGBA")
            assembler_img = Image.open('sprites/assembler.png').convert("RGBA")

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
                            pos = (j * img.width, i * img.height)
                        if element == 'INSE':
                            img = inserter_img.rotate(int(direction))
                            pos = (j * img.width, i * img.height)
                        if element == 'ASSE':
                            img = assembler_img.rotate(int(direction))
                            pos = (j * 64 - 64, i * 64 - 64)

                        game_map_img.paste(img, pos, mask=img)

            game_map_img.save('model_image/game_map_model.png')
        else:
            print("No model was found")

    def map_variables(self):
        game_map = [[None for i in range(self.width)] for j in range(self.height)]
        direction = {
            'empty': "empty",
            'north': 0,     # North
            'east': -90,    # East
            'west': -270,   # West
            'south': -180,  # South
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

        # Assemblers
        for i in range(self.height-2):
            for j in range(self.width-2):
                assembler = str(model[self.model_variables['ASSEMBLER'][i][j]]).strip('\"')
                if assembler != '0':
                    game_map[i+1][j+1] = f"ASSE:{0}"

        return game_map
