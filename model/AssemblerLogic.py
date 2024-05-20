from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement
from model.RecipeElement import RecipeElement


class AssemblerLogic(DirectionalElement, GridElement, RecipeElement):
    def __init__(self, width, height, recipe):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, {})
        RecipeElement.__init__(self, recipe)
        self.assembler_size = 3
        self.max_assemblers = (width // self.assembler_size) * (height // self.assembler_size)
        self.assembler_upper_bound()
        self.assembler_bits = math.ceil(math.log2(self.max_assemblers + 1))

        self.placement_width = width - 2
        self.placement_height = height - 2

        self.width = width
        self.height = height

        self.displacement = {
            1: [(-2, -1), (-2, 0), (-2, 1)],  # North
            2: [(-1, 2), (0, 2), (1, 2)],  # East
            3: [(2, -1), (2, 0), (2, 1)],  # South
            4: [(-1, -2), (0, -2), (1, -2)]  # West
        }

        self.recipe_bits = math.ceil(math.log2(self.max_recipes + 1))

        # Center cell of the assembler (takes value from 0 to max_assemblers)
        self.assembler = [[BitVec(f"A_{i}_{j}", self.assembler_bits)
                           for i in range(self.placement_width)] for j in range(self.placement_height)]

        # 3x3 area around the center of an assembler
        self.collision_area = [[BitVec(f"C_A_{i}_{j}", self.assembler_bits)
                                for i in range(self.width)] for j in range(self.height)]

        self.input_ratio = [[Real(f"RATIO_{i}_{j}")
                                for i in range(self.max_items)] for j in range(self.max_assemblers)]

    def assembler_upper_bound(self):
        # Determine the max assemblers per recipe the blueprint can have
        produced_required_items = {}
        item_to_produce = "none"
        z3_variable = []
        for recipe_name, recipe in self.recipes.items():
            # Initialize the dictionary for the recipe
            produced_required_items[recipe_name] = {"required": {}, "produced": {}}
            for input in recipe["IN"]:
                if self.is_produced(input[0]):
                    produced_required_items[recipe_name]["required"][input[0]] = input[1]
            for output in recipe["OUT"]:
                if self.is_needed(output[0]):
                    produced_required_items[recipe_name]["produced"][output[0]] = output[1]
                else:
                    item_to_produce = output[0]
            variable = Int(recipe_name + "-assembler")
            produced_required_items[recipe_name].update({"z3_variable": variable})
            z3_variable.append(variable)

        s = Optimize()

        # Define the domain of the number of possible assemblers
        for recipe_name, assembler_recipe in produced_required_items.items():
            s.add(And(assembler_recipe["z3_variable"] > 0, assembler_recipe["z3_variable"] <= self.max_assemblers))

        # Ensure the total amount of assemblers does not surpass the maximum amount
        s.add(sum(z3_variable) <= self.max_assemblers)

        # The number of items needed is covered
        for recipe_name, recipe in produced_required_items.items():
            if recipe["produced"]: # Not the objective recipe
                s.add(recipe["z3_variable"]*recipe["produced"][recipe_name] >= sum(self.demand(recipe_name, produced_required_items)))

        # Multi objective optimization
        s.maximize(produced_required_items[item_to_produce]["z3_variable"])
        s.minimize(sum(z3_variable))
        if s.check() == sat:
            m = s.model()
            self.selected_recipe = []
            for (recipe_name, recipe) in produced_required_items.items():
                n_assemblers = m.evaluate(recipe["z3_variable"]).as_long()
                for assembler in range(n_assemblers):
                    self.selected_recipe.append(recipe_name)
            self.max_assemblers = len(self.selected_recipe)
            print("MAX ASSEMBLERS: ", self.max_assemblers)
            print("SELECTED RECIPES: ", self.selected_recipe)
        else:
            print("OJOOOO NO S'HA TROBAT UPPER BOUND, PENSAR QUE FER EN AQUESTS CASOS")

    def demand(self, item, produced_required_items):
        demand = []
        for recipe_name, recipe in produced_required_items.items():
            for item_name, quantity in recipe["required"].items():
                if item_name == item:
                    demand.append(recipe["z3_variable"]*quantity)
        return demand
    def is_produced(self, item):
        is_produced = False
        for recipe_name, recipe in self.recipes.items():
            for output in recipe["OUT"]:
                if output[0] == item:
                    is_produced = True
                    break
        return is_produced

    def is_needed(self, item):
        is_needed = False
        for recipe_name, recipe in self.recipes.items():
            for input in recipe["IN"]:
                if input[0] == item:
                    is_needed = True
                    break
        return is_needed

    def domain_constraint(self):
        return [ULE(self.assembler[i][j], self.max_assemblers)
                for i in range(self.placement_height) for j in range(self.placement_width)] + \
            [ULE(self.collision_area[i][j], self.max_assemblers)
             for i in range(self.height) for j in range(self.width)] + \
            [And(self.input_ratio[i][j] >= 0, self.input_ratio[i][j] <= 1)
             for i in range(self.max_assemblers) for j in range(self.max_items)]

    def distinct_assemblers(self):
        distinct = []
        for assembler in range(1, self.max_assemblers + 1):
            distinct.append(sum([If(self.assembler[i][j] == assembler, 1, 0)
                                 for i in range(self.placement_height) for j in range(self.placement_width)]) <= 1)
        return distinct

    def lower_bound_assemblers(self):
        lower_bound = []
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                lower_bound.append(If(UGT(self.assembler[i][j], 0), 1, 0))
        return [sum(lower_bound) >= self.max_recipes]

    def link_assembler_collision(self):
        link = []
        for i in range(self.height):
            for j in range(self.width):
                neighbors = []
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        x = di + i - 1
                        y = dj + j - 1
                        if 0 <= x < self.placement_height and 0 <= y < self.placement_width:
                            neighbors.append(self.assembler[x][y] == self.collision_area[i][j])
                link.append(Implies(self.collision_area[i][j] != 0, Or(neighbors)))
        return link

    def set_collision(self):
        set_collision = []
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                surround_collision = []
                for di in range(-1, 2):
                    for dj in range(-1, 2):
                        x = di + i + 1
                        y = dj + j + 1
                        if 0 <= x < self.height and 0 <= y < self.width:
                            surround_collision.append(self.collision_area[x][y] == self.assembler[i][j])
                set_collision.append(Implies(self.assembler[i][j] != 0, And(surround_collision)))
        return set_collision

    def assembler_output(self):
        assembler_output = []
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                for assembler in range(self.max_assemblers):
                    assembler_selected = self.assembler[i][j] == assembler + 1
                    for item in range(self.max_items):
                        outputs = []
                        for direction in self.displacement:
                            for pos in self.displacement[direction]:
                                x = i + 1 + pos[0]
                                y = j + 1 + pos[1]
                                if 0 <= x < self.height and 0 <= y < self.width:
                                    outputs.append(And(self.inserter[x][y] == self.direction[direction],
                                                       self.item_flow[x][y] == item + 1))
                        recipe = self.selected_recipe[assembler]
                        if self.is_recipe_output(recipe, self.variable_to_item[item+1]):
                            assembler_output.append(
                                Implies(assembler_selected, Or(outputs)))
                        else:
                            assembler_output.append(
                                Implies(assembler_selected, Not(Or(outputs))))

        return assembler_output

    def assembler_input(self):
        assembler_input = []
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                for assembler in range(self.max_assemblers):
                    assembler_selected = self.assembler[i][j] == assembler + 1
                    for item in range(self.max_items):
                        inputs = []
                        for direction in self.displacement:
                            for pos in self.displacement[direction]:
                                x = i + 1 + pos[0]
                                y = j + 1 + pos[1]
                                if 0 <= x < self.height and 0 <= y < self.width:
                                    inputs.append(And(self.inserter[x][y] == self.opposite_dir[direction],
                                                      self.item_flow[x][y] == item + 1))
                        recipe = self.selected_recipe[assembler]
                        if self.is_recipe_input(recipe, self.variable_to_item[item+1]):
                            assembler_input.append(
                                Implies(assembler_selected,
                                   Or(inputs)))
                        else:
                            assembler_input.append(
                                Implies(assembler_selected,
                                   Not(Or(inputs))))

        return assembler_input

    def input_ratios(self):
        input_ratios = []
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                for assembler in range(self.max_assemblers):
                    for input in self.recipes[self.selected_recipe[assembler]]["IN"]:
                        item = self.item_to_variable[input[0]]
                        inputs = []
                        for direction in self.displacement:
                            for pos in self.displacement[direction]:
                                x = i + 1 + pos[0]
                                y = j + 1 + pos[1]
                                if 0 <= x < self.height and 0 <= y < self.width:
                                    inputs.append(If(And(self.inserter[x][y] == self.opposite_dir[direction],
                                                         self.item_flow[x][y] == item), self.output_flow_rate[x][y], 0))
                        input_ratios.append(Implies(self.assembler[i][j] == assembler + 1,
                                                       self.input_ratio[assembler][item-1] == sum(inputs) / input[1]))

        return input_ratios

    def equal_ratios(self):
        equal_ratios = []
        for j in range(self.max_assemblers):
            for i in range(1, self.max_items):
                equal_ratios.append(self.input_ratio[j][i] == self.input_ratio[j][0])
        return equal_ratios

    def set_output_rate(self):
        output_ratios = []
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                for assembler in range(self.max_assemblers):
                    outputs = []
                    for direction in self.displacement:
                        for pos in self.displacement[direction]:
                            x = i + 1 + pos[0]
                            y = j + 1 + pos[1]
                            if 0 <= x < self.height and 0 <= y < self.width:
                                outputs.append(If(self.inserter[x][y] == self.direction[direction], self.output_flow_rate[x][y], 0))
                    for output in self.recipes[self.selected_recipe[assembler]]["OUT"]:
                        output_item = self.item_to_variable[output[0]]
                        output_ratios.append(Implies(self.assembler[i][j] == assembler + 1, sum(outputs) == self.input_ratio[assembler][output_item-1] * output[1]))

        return output_ratios

    def constraints(self):
        return self.domain_constraint() + self.distinct_assemblers() + self.set_collision() + self.link_assembler_collision() + self.assembler_input() + self.assembler_output() + self.input_ratios() + self.equal_ratios() + self.set_output_rate() + self.lower_bound_assemblers()

    def set_inserter(self, inserter):
        self.inserter = inserter

    def set_item_flow(self, item_flow):
        self.item_flow = item_flow

    def set_item_flow_rate(self, output_flow_rate):
        self.output_flow_rate = output_flow_rate

