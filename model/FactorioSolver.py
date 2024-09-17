from z3 import *
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

    :param recipes: Contains the recipes that the assemblers in the blueprint will use, for each recipe it has a list
                    of the items it requires and which rate in items/min needs and the outputting item and rate.
    :type recipes: Dictionary
    """

    def __init__(self, width, height, in_out_pos, recipes, selected_opt):
        # Attribute initialization
        self.width = width
        self.height = height
        self.solving_time = 0
        self.has_solution = False
        self.timed_out = False
        self.grid_variables = {}
        self.array_variables = {}

        self.assembler_size = 3
        self.max_assemblers = (width // self.assembler_size) * (height // self.assembler_size)
        self.max_recipes = len(recipes)

        # Z3 solver declaration
        self.s = Optimize()
        self.s.set("timeout", 1800000)

        # Model initialization with the corresponding instance data
        if self.max_assemblers >= self.max_recipes:
            self.initialize_model(width, height, in_out_pos, recipes, selected_opt)

    def initialize_model(self, blueprint_width, blueprint_height, in_out_pos, recipes, selected_opt):
        """
        Creates all the constraints given the instance data, and sets the optimization criteria to the Optimizer. It
        also saves the model variables to later be evaluated.

        :param blueprint_width: number of rows
        :type blueprint_width: Int

        :param blueprint_height: number of columns
        :type blueprint_height: Int

        :param in_out_pos: input and output positions with the corresponding items they are carrying
        :type in_out_pos: Dictionary

        :param recipes: each recipe used with the item quantities and types required for the input and output
        :type recipes: Dictionary

        :param selected_opt: optimization criteria ('maximize-output', 'minimize-route', 'minimize-loss')
        :type selected_opt: String
        """

        # Cration of all the objects containing the logic that creates the constraints
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
        item_flow_behaviour = ItemFlowLogic(blueprint_width, blueprint_height, route_behaviour.route,
                                            inserter_behaviour.inserter, conveyor_behaviour.conveyor, in_out_pos,
                                            recipes)
        item_flow_rate_behaviour = ItemFlowRateLogic(blueprint_width, blueprint_height, in_out_pos,
                                                     inserter_behaviour.inserter, conveyor_behaviour.conveyor,
                                                     route_behaviour.route)

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

        # Add all the constraints of the model to the solver
        self.s.add(conveyor_behaviour.constraints()
                   + route_behaviour.constraints()
                   + inserter_behaviour.constraints()
                   + factory_behaviour.constraints()
                   + self.assembler_behaviour.constraints()
                   + item_flow_behaviour.constraints()
                   + item_flow_rate_behaviour.constraints()
                   )
        # Selection of the optimization criteria
        self.s.maximize(item_flow_rate_behaviour.item_output())
        if selected_opt == 'minimize-loss':
            self.s.minimize(item_flow_rate_behaviour.item_loss())
        elif selected_opt == 'minimize-route':
            self.s.minimize(route_behaviour.route_length())

    def find_solution(self):
        """
        Tells the solver to find a solution, saves the solving status (SAT, UNSAT, TIMED OUT), it also saves the time it
        took the solver to finish.

        :return: The solving status (solution found or not found)
        :rtype: Bool
        """
        if self.max_assemblers >= self.max_recipes:
            start = time.time()
            result = self.s.check()
            computing_time = time.time() - start
            if result == sat:
                self.has_solution = True
            elif result == unsat:
                self.has_solution = False
            else:
                self.has_solution = False
                self.timed_out = True
            self.solving_time = computing_time
        else:
            self.has_solution = False

        return self.has_solution

    def model_to_json(self):
        """
        Checks if the solver found a solution, if so evaluates all the model variables and store them in a dictionary,
        it also saves the time spent in solving and the status of the solution.

        :return: a JSON transformable dictionary with all the information of the solved instance
        :rtype: Dictionary
        """

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
                                    value = self.assembler_behaviour.variable_to_item[
                                        int(float(str(model[var_value[i][j]])))]
                                elif var_name == 'ASSEMBLER_COLLISION' or var_name == 'ASSEMBLER':
                                    value = self.assembler_behaviour.selected_recipe[
                                        int(float(str(model[var_value[i][j]]))) - 1]
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
