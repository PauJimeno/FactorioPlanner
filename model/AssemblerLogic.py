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

        # self.input_ratio = [[Real(f"RATIO_{i}_{j}")
        #                         for i in range(self.max_items)] for j in range(self.max_assemblers)]

        self.input_ratio = self.create_ratio_dict()

    def create_ratio_dict(self):
        ratio_dict = {}
        for assembler in range(0, self.max_assemblers):
            ratio_dict[assembler + 1] = {}
            recipe = self.recipes[self.selected_recipe[assembler]]["IN"]
            for item in recipe:
                ratio_dict[assembler + 1][self.item_to_variable[item[0]]] = Real(
                    f"RATIO_{assembler + 1}_{self.item_to_variable[item[0]]}")
        return ratio_dict

    def assembler_upper_bound(self):
        # Determine the max assemblers per recipe the blueprint can have
        produced_required_items = {}
        item_to_produce = "none"
        assemblers = []
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
            rate = Real(recipe_name + "-rate")
            assembler = Int(recipe_name + "-assembler")
            produced_required_items[recipe_name].update({"production_rate": rate})
            produced_required_items[recipe_name].update({"n_assembler": assembler})
            assemblers.append(assembler)

        s = Optimize()

        # Define the domain of the number of possible assemblers
        domain = []
        for recipe_name, assembler_recipe in produced_required_items.items():
            domain.append(And(assembler_recipe["production_rate"] > 0,
                              assembler_recipe["production_rate"] <= self.max_assemblers))
        s.add(domain)

        ceil = []
        # Ensure n_assembler is the corresponding ceil to the production_rate
        for recipe_name, assembler_recipe in produced_required_items.items():
            ceil.append(If(ToInt(assembler_recipe["production_rate"]) < assembler_recipe["production_rate"],
                           assembler_recipe["n_assembler"] == ToInt(assembler_recipe["production_rate"]) + 1,
                           assembler_recipe["n_assembler"] == ToInt(assembler_recipe[
                                                                        "production_rate"])))
        s.add(ceil)
        # Ensure the total amount of assemblers does not surpass the maximum amount

        max_ass = sum(assemblers) <= self.max_assemblers
        s.add(max_ass)

        # The number of items needed is covered
        disti = []
        for recipe_name, recipe in produced_required_items.items():
            if recipe["produced"]:  # Not the objective recipe
                disti.append(recipe["production_rate"] * recipe["produced"][recipe_name] == sum(
                    self.demand(recipe_name, produced_required_items)))
        s.add(disti)

        # Multi objective optimization
        s.maximize(produced_required_items[item_to_produce]["n_assembler"] + produced_required_items[item_to_produce]["production_rate"])
        if s.check() == sat:
            m = s.model()
            self.selected_recipe = []
            for (recipe_name, recipe) in produced_required_items.items():
                n_assemblers = m.evaluate(recipe["n_assembler"]).as_long()
                print("Recipe", recipe_name, "working at", m.evaluate(recipe["production_rate"]))
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
                    demand.append(recipe["production_rate"] * quantity)
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

    def create_assembler_dict(self, selected_recipe):
        # Creates a dictionary with the recipes that in the best of cases will need more than one assembler
        assembler_dict = {}
        for i, recipe in enumerate(selected_recipe):
            if selected_recipe.count(recipe) > 1:
                if recipe not in assembler_dict:
                    assembler_dict[recipe] = {}
                # Create z3 variables for x and y
                x = Int(f'x_{i + 1}')
                y = Int(f'y_{i + 1}')
                used = Bool(f'used_{i + 1}')
                assembler_dict[recipe][i + 1] = [x, y, used]
        return assembler_dict

    def symmetry_breaking(self):
        symmetry_breaking = []
        self.assembler_recipes = self.create_assembler_dict(self.selected_recipe)

        # Domain of the variable
        for recipe in self.assembler_recipes:
            assemblers = self.assembler_recipes[recipe]
            assembler_keys = list(assemblers.keys())
            for i in range(len(assembler_keys)):
                x, y, used = assemblers[assembler_keys[i]]
                symmetry_breaking.append(And(x >= 0, x < self.placement_width))
                symmetry_breaking.append(And(y >= 0, y < self.placement_height))


        # Order the positions of the assemblers to break the vertical and horizontal symetry
        for recipe in self.assembler_recipes:
            assemblers = self.assembler_recipes[recipe]
            assembler_keys = list(assemblers.keys())
            for i in range(len(assembler_keys) - 1):
                x0, y0, _ = assemblers[assembler_keys[i]]
                x1, y1, _ = assemblers[assembler_keys[i + 1]]
                symmetry_breaking.append(x0 <= x1)
                symmetry_breaking.append(Implies(x0 == x1, y0 < y1))

        # Link the variable ordered positions to the assembler variable
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                for recipe in self.assembler_recipes:
                    assemblers = self.assembler_recipes[recipe]
                    assembler_keys = list(assemblers.keys())
                    for k in range(len(assembler_keys)):
                        x, y, used = assemblers[assembler_keys[k]]
                        symmetry_breaking.append(Implies(self.assembler[i][j] == assembler_keys[k], used))
                        symmetry_breaking.append(Implies(And(x == i, y == j, used), self.assembler[i][j] == assembler_keys[k]))
        return symmetry_breaking

    def print_auxiliary_variables(self, model):
        for recipe in self.assembler_recipes:
            assemblers = self.assembler_recipes[recipe]
            assembler_keys = list(assemblers.keys())
            for i in range(len(assembler_keys)):
                x, y, used = assemblers[assembler_keys[i]]
                print(f"Recipe: {recipe}, Assembler: {assembler_keys[i]}, x = {model[x]}, y = {model[y]}, used = {model[used]}")

    def domain_constraint(self):
        item_ratio_domain = []
        for assembler in range(1, self.max_assemblers + 1):
            for item in self.input_ratio[assembler]:
                item_ratio_domain.append(
                    And(self.input_ratio[assembler][item] > 0, self.input_ratio[assembler][item] <= 1))

        return [ULE(self.assembler[i][j], self.max_assemblers)
                for i in range(self.placement_height) for j in range(self.placement_width)] + \
            [ULE(self.collision_area[i][j], self.max_assemblers)
             for i in range(self.height) for j in range(self.width)] + \
            item_ratio_domain

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
                        if self.is_recipe_output(recipe, self.variable_to_item[item + 1]):
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
                        if self.is_recipe_input(recipe, self.variable_to_item[item + 1]):
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
                                                    self.input_ratio[assembler + 1][item] == sum(inputs) / input[1]))

        return input_ratios

    def equal_ratios(self):
        equal_ratios = []
        for assembler in range(1, self.max_assemblers + 1):
            items = list(self.input_ratio[assembler].keys())
            if items:
                first_item_ratio = self.input_ratio[assembler][items[0]]
                for item in items[1:]:
                    equal_ratios.append(self.input_ratio[assembler][item] == first_item_ratio)
        return equal_ratios

    def set_output_rate(self):
        output_ratios = []
        for i in range(self.placement_height):
            for j in range(self.placement_width):
                for assembler in range(self.max_assemblers):
                    outputs = []
                    output_rate = Real(f'output_rate_{i}_{j}_{assembler}')
                    output_ratios.append(And(output_rate >= 0, output_rate <= 50))
                    for direction in self.displacement:
                        for pos in self.displacement[direction]:
                            x = i + 1 + pos[0]
                            y = j + 1 + pos[1]
                            if 0 <= x < self.height and 0 <= y < self.width:
                                outputs.append(
                                    If(self.inserter[x][y] == self.direction[direction], self.output_flow_rate[x][y],
                                       0))
                                output_ratios.append(Implies(self.inserter[x][y] == self.direction[direction],
                                                             self.output_flow_rate[x][y] == output_rate))
                    first_item_ratio = next(iter(self.input_ratio[assembler + 1].values()))
                    for output in self.recipes[self.selected_recipe[assembler]]["OUT"]:
                        output_ratios.append(Implies(self.assembler[i][j] == assembler + 1,
                                                     sum(outputs) == first_item_ratio * output[1]))
        return output_ratios

    def constraints(self):
        return self.domain_constraint() + self.distinct_assemblers() + self.set_collision() + self.link_assembler_collision() + self.assembler_input() + self.assembler_output() + self.input_ratios() + self.equal_ratios() + self.set_output_rate() + self.lower_bound_assemblers() + self.symmetry_breaking()

    def set_inserter(self, inserter):
        self.inserter = inserter

    def set_item_flow(self, item_flow):
        self.item_flow = item_flow

    def set_item_flow_rate(self, output_flow_rate):
        self.output_flow_rate = output_flow_rate
