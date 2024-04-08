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

        self.selected_recipe = [BitVec(f"A_R_{i}", self.recipe_bits) for i in range(self.max_assemblers)]

        self.input_ratio = [[Real(f"RATIO_{i}_{j}")
                                for i in range(self.max_items)] for j in range(self.max_assemblers)]

        self.min_ratio = [Real(f"MIN_RATIO_{i}") for i in range(self.max_assemblers)]

    def domain_constraint(self):
        return [ULE(self.assembler[i][j], self.max_assemblers)
                for i in range(self.placement_height) for j in range(self.placement_width)] + \
            [ULE(self.collision_area[i][j], self.max_assemblers)
             for i in range(self.height) for j in range(self.width)] + \
            [ULE(self.selected_recipe[i], self.max_recipes)
             for i in range(self.max_assemblers)] + \
            [And(self.min_ratio[i] >= 0, self.min_ratio[i] <= 1)
             for i in range(self.max_assemblers)] + \
            [And(self.input_ratio[i][j] >= 0, self.input_ratio[i][j] <= 1)
             for i in range(self.max_assemblers) for j in range(self.max_items)]


    def distinct_assemblers(self):
        distinct = []
        for assembler in range(1, self.max_assemblers + 1):
            distinct.append(sum([If(self.assembler[i][j] == assembler, 1, 0)
                                 for i in range(self.placement_height) for j in range(self.placement_width)]) <= 1)
        return distinct

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
                link.append(If(self.collision_area[i][j] != 0, Or(neighbors), self.collision_area[i][j] == 0))
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
                        for recipe in range(self.max_recipes):
                            recipe_selected = self.selected_recipe[assembler] == recipe + 1
                            if self.recipe_output[recipe][item] != 0:
                                assembler_output.append(
                                    Implies(And(assembler_selected, recipe_selected),
                                       Or(outputs)))
                            else:
                                assembler_output.append(
                                    Implies(And(assembler_selected, recipe_selected),
                                       Not(Or(outputs))))

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
                        for recipe in range(self.max_recipes):
                            recipe_selected = self.selected_recipe[assembler] == recipe + 1
                            if self.recipe_input[recipe][item] != 0:
                                assembler_input.append(
                                    Implies(And(assembler_selected, recipe_selected),
                                       Or(inputs)))
                            else:
                                assembler_input.append(
                                    Implies(And(assembler_selected, recipe_selected),
                                       Not(Or(inputs))))

        return assembler_input

    def input_ratios(self):
        input_ratios = []
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
                                    inputs.append(If(And(self.inserter[x][y] == self.opposite_dir[direction],
                                                         self.item_flow[x][y] == item + 1), self.item_flow_rate[x][y], 0))
                        for recipe in range(self.max_recipes):
                            recipe_selected = self.selected_recipe[assembler] == recipe + 1
                            if self.recipe_input[recipe][item] != 0:
                                input_ratios.append(Implies(And(assembler_selected, recipe_selected),
                                                       self.input_ratio[assembler][item] == sum(inputs) /
                                                       self.recipe_input[recipe][item]))
                            else:
                                input_ratios.append(
                                    Implies(And(assembler_selected, recipe_selected), self.input_ratio[assembler][item] == 0))
        return input_ratios

    def min_input_ratio(self):
        min_ratio = []
        for assembler in range(self.max_assemblers):
            for item in range(self.max_items):
                non_zero_ratio = If(self.input_ratio[assembler][item] > 0, self.input_ratio[assembler][item], 1)
                min_ratio.append(self.min_ratio[assembler] <= non_zero_ratio)
        return min_ratio

    def associate_recipe(self):
        assembler_recipe = []
        for k in range(1, self.max_assemblers + 1):
            exists_assembler = []
            for i in range(self.placement_height):
                for j in range(self.placement_width):
                    exists_assembler.append(self.assembler[i][j] == k)
            assembler_recipe.append(
                If(Or(exists_assembler), self.selected_recipe[k - 1] != 0, self.selected_recipe[k - 1] == 0))

        return assembler_recipe

    def constraints(self):
        return self.domain_constraint() + self.distinct_assemblers() + self.set_collision() + self.link_assembler_collision() + self.assembler_input() + self.assembler_output() + self.associate_recipe() + self.input_ratios() + self.min_input_ratio()

    def set_inserter(self, inserter):
        self.inserter = inserter

    def set_item_flow(self, item_flow):
        self.item_flow = item_flow

    def set_item_flow_rate(self, item_flow_rate):
        self.item_flow_rate = item_flow_rate

