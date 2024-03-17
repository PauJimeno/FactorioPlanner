from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class AssemblerLogic(DirectionalElement, GridElement):
    def __init__(self, width, height):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, {})

        self.assembler_size = 3
        self.max_assemblers = (width // self.assembler_size) * (height // self.assembler_size)

        self.assembler_bits = math.ceil(math.log2(self.max_assemblers + 1))

        self.placement_width = width - 2
        self.placement_height = height - 2

        self.width = width
        self.height = height

        self.displacement = {
            1: [(-2, -1), (-2, 0), (-2, 1)],  # North
            2: [(-1, 2), (0, 2), (1, 2)],     # East
            3: [(2, -1), (2, 0), (2, 1)],     # South
            4: [(-1, -2), (0, -2), (1, -2)]   # West
        }

        self.max_recipes = 8
        self.recipe_bits = math.ceil(math.log2(self.max_recipes))

        # Center cell of the assembler (takes value from 0 to max_assemblers)
        self.assembler = [[BitVec(f"A_{i}_{j}", self.assembler_bits)
                           for i in range(self.placement_width)] for j in range(self.placement_height)]

        # 3x3 area around the center of an assembler
        self.collision_area = [[BitVec(f"C_A_{i}_{j}", self.assembler_bits)
                                for i in range(self.width)] for j in range(self.height)]

        self.selected_recipe = [[BitVec(f"A_R_{i}_{j}", self.recipe_bits)
                           for i in range(self.placement_width)] for j in range(self.placement_height)]

    def domain_constraint(self):
        return [ULE(self.assembler[i][j], self.max_assemblers)
                for i in range(self.placement_height) for j in range(self.placement_width)] +\
                [ULE(self.collision_area[i][j], self.max_assemblers)
                 for i in range(self.placement_height-2) for j in range(self.placement_width-2)]

    def distinct_assemblers(self):
        distinct = []
        for assembler in range(1, self.max_assemblers+1):
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
                set_collision.append(If(self.assembler[i][j] != 0, And(surround_collision), True))
        return set_collision

    def assembler_input(self):
        assembler_input = []

        for i in range(self.placement_height):
            for j in range(self.placement_width):
                has_input = []
                for direction in self.displacement:
                    for pos in self.displacement[direction]:
                        x = i + 1 + pos[0]
                        y = j + 1 + pos[1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            has_input.append(self.inserter[x][y] == self.opposite_dir[direction])
                assembler_input.append(If(self.assembler[i][j] != 0, Or(has_input), True))
        return assembler_input

    def assembler_output(self):
        assembler_output = []

        for i in range(self.placement_height):
            for j in range(self.placement_width):
                has_output = []
                for direction in self.displacement:
                    for pos in self.displacement[direction]:
                        x = i + 1 + pos[0]
                        y = j + 1 + pos[1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            has_output.append(self.inserter[x][y] == self.direction[direction])
                assembler_output.append(If(self.assembler[i][j] != 0, Or(has_output), True))
        return assembler_output

    def associate_recipe(self):
        assembler_recipe = []

        for i in range(self.placement_height):
            for j in range(self.placement_width):
                assembler_recipe.append(If(self.assembler[i][j] != 0, UGT(self.selected_recipe[i][j], 0), True))
        return assembler_recipe


    def constraints(self):
        return self.domain_constraint() + self.distinct_assemblers() + self.set_collision() + self.link_assembler_collision() + self.assembler_input() + self.assembler_output() + self.associate_recipe()

    def set_inserter(self, inserter):
        self.inserter = inserter
