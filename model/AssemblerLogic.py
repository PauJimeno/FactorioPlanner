from z3 import *


class AssemblerLogic:
    def __init__(self, width, height):
        self.assembler_size = 3
        self.max_assemblers = (width // self.assembler_size) * (height // self.assembler_size)

        self.n_bits = math.ceil(math.log2(self.max_assemblers+1))

        self.placement_width = width - 2
        self.placement_height = height - 2

        self.width = width
        self.height = height

        # Center cell of the assembler (takes value from 0 to max_assemblers)
        self.assembler = [[BitVec(f"A_{i}_{j}", self.n_bits)
                           for i in range(self.placement_width)] for j in range(self.placement_height)]

        self.collision_area = [[BitVec(f"C_A_{i}_{j}", self.n_bits)
                                for i in range(self.width)] for j in range(self.height)]

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

    def constraints(self):
        return self.domain_constraint() + self.distinct_assemblers() + self.set_collision()
