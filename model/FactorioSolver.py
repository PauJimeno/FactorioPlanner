from PIL import ImageDraw
from z3 import *
from PIL import Image
import time
import json

from model.AssemblerLogic import AssemblerLogic
from model.ConveyorLogic import ConveyorLogic
from model.FactoryLogic import FactoryLogic
from model.InserterLogic import InserterLogic
from model.ItemFlowLogic import ItemFlowLogic
from model.ItemFlowRateLogic import ItemFlowRateLogic
from model.RouteLogic import RouteLogic


class FactorioSolver:
    """
    This class manages all the components form the model given an instance, it also creates the Z3 Optimizer
    and allows to solve the instance and retrieve the solution in many ways.

    :param width: Width of the blueprint
    :type width: Int

    :param height: Height of the blueprint
    :type height: Int

    :param in_out_pos: Contains the input and output positions and type of item carrying
    :type in_out_pos: Dictionary

    :param recipes: Contains the recipes that the assemblers in the blueprint will use, for each recipe it has a list of
    the items it requires and which rate in items/min needs and the outputting item and rate.
    :type recipes: Dictionary
    """
    def __init__(self, width, height, in_out_pos, recipes):
        self.width = width
        self.height = height

        # Z3 solver declaration
        self.s = Optimize()
        self.s.set("timeout", 1800000)

        self.solving_time = 0

        # Solution found variable
        self.has_solution = False
        self.timed_out = False

        self.grid_variables = {}

        self.array_variables = {}

        start = time.time()
        self.initialize_model(width, height, in_out_pos, recipes)
        computing_time = time.time() - start
        print("Model initialization time:", computing_time)

    def initialize_model(self, blueprint_width, blueprint_height, in_out_pos, recipes):
        conveyor_behaviour = ConveyorLogic(blueprint_width, blueprint_height, in_out_pos)
        self.assembler_behaviour = AssemblerLogic(blueprint_width, blueprint_height, recipes)
        inserter_behaviour = InserterLogic(blueprint_width, blueprint_height, conveyor_behaviour.conveyor,
                                           self.assembler_behaviour.collision_area, in_out_pos)
        conveyor_behaviour.set_inserter(inserter_behaviour.inserter)
        self.assembler_behaviour.set_inserter(inserter_behaviour.inserter)
        route_behaviour = RouteLogic(blueprint_width, blueprint_height, in_out_pos,
                                     conveyor_behaviour.conveyor,
                                     inserter_behaviour.inserter, self.assembler_behaviour.collision_area, recipes)
        factory_behaviour = FactoryLogic(blueprint_width, blueprint_height, conveyor_behaviour,
                                         inserter_behaviour, self.assembler_behaviour.collision_area)
        item_flow_behaviour = ItemFlowLogic(blueprint_width, blueprint_height, route_behaviour.route, inserter_behaviour.inserter, conveyor_behaviour.conveyor, in_out_pos, recipes)
        item_flow_rate_behaviour = ItemFlowRateLogic(blueprint_width, blueprint_height, in_out_pos, inserter_behaviour.inserter, conveyor_behaviour.conveyor, route_behaviour.route)

        self.assembler_behaviour.set_item_flow(item_flow_behaviour.item_flow)
        self.assembler_behaviour.set_item_flow_rate(item_flow_rate_behaviour.output_flow_rate)

        self.grid_variables.update({"CONVEYOR": conveyor_behaviour.conveyor})
        self.grid_variables.update({"ROUTE": route_behaviour.route})
        self.grid_variables.update({"INSERTER": inserter_behaviour.inserter})
        self.grid_variables.update({"ASSEMBLER": self.assembler_behaviour.assembler})
        self.grid_variables.update({"ASSEMBLER_COLLISION": self.assembler_behaviour.collision_area})
        self.grid_variables.update({"ITEM_FLOW": item_flow_behaviour.item_flow})
        self.grid_variables.update({"INPUT_FLOW_RATE": item_flow_rate_behaviour.input_flow_rate})
        self.grid_variables.update({"OUTPUT_FLOW_RATE": item_flow_rate_behaviour.output_flow_rate})
        # self.grid_variables.update({"INPUT RATIO": assembler_behaviour.input_ratio})

        self.s.add(conveyor_behaviour.constraints()
                   + route_behaviour.constraints()
                   + inserter_behaviour.constraints()
                   + factory_behaviour.constraints()
                   + self.assembler_behaviour.constraints()
                   + item_flow_behaviour.constraints()
                   + item_flow_rate_behaviour.constraints()
                   )

        # Minimize the objective function
        self.s.maximize(item_flow_rate_behaviour.item_output())
        # self.s.minimize(item_flow_rate_behaviour.item_loss())
        # self.s.minimize(route_behaviour.route_length())

    def find_solution(self):
        start = time.time()
        result = self.s.check()
        computing_time = time.time() - start
        if result == sat:
            self.has_solution = True
            print("Solution found (SAT)")
        elif result == unsat:
            self.has_solution = False
            print("No solution was found (UNSAT)")
        else:  # result is unknown
            self.has_solution = False
            self.timed_out = True
            print("The solver timed out before finding a solution (UNKNOWN)")
        print("Computing time: ", computing_time)
        self.solving_time = computing_time

        return self.has_solution

    def model_to_string(self):
        if self.has_solution:
            m = self.s.model()
            # Print grid variables
            for var_name, var_value in self.grid_variables.items():
                print(var_name)
                height, width = len(var_value), len(var_value[0])
                for i in range(height):
                    for j in range(width):
                        print(m[var_value[i][j]], end='          ')
                    print()

            # Print Array variables
            for var_name, var_value in self.array_variables.items():
                print(var_name)
                length = len(var_value)
                for i in range(length):
                    print(m[var_value[i]], end=' ')
                print()
        else:
            print("No model was found")

    def model_to_json(self):
        instance_data_path = f"static/model_image/solved_instance.json"
        instance_model = {}
        if self.has_solution:
            model = self.s.model()
            for var_name, var_value in self.grid_variables.items():
                height, width = len(var_value), len(var_value[0])
                variable = []
                for i in range(height):
                    row = []
                    for j in range(width):
                        value = str(model[var_value[i][j]])
                        if var_name == 'ASSEMBLER_COLLISION' or var_name == 'ITEM_FLOW' or var_name == 'ASSEMBLER':
                            if value == '0':
                                value = 'none'
                            else:
                                if var_name == 'ITEM_FLOW':
                                    value = self.assembler_behaviour.variable_to_item[int(float(str(model[var_value[i][j]])))]
                                elif var_name == 'ASSEMBLER_COLLISION' or var_name == 'ASSEMBLER':
                                    value = self.assembler_behaviour.selected_recipe[int(float(str(model[var_value[i][j]])))-1]
                        row.append(value)
                    variable.append(row)
                instance_model[var_name] = variable
            instance_model["status"] = "SAT"
        elif self.timed_out:
            instance_model["status"] = "TIMED_OUT"
        else:
            instance_model["status"] = "UNSAT"
        instance_model["solving_time"] = self.solving_time

        with open(instance_data_path, 'w') as f:
            json.dump(instance_model, f)
        return instance_model
