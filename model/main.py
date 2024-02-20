from model.FactorioSolver import FactorioSolver

# MODEL INPUTS #
blueprint_width = 6
blueprint_height = 10
route_pos = [((0, 0), (3, 3))]

# SOLVER DECLARATION #
solver = FactorioSolver(blueprint_width, blueprint_height, route_pos)

# FIND A SOLUTION #
solver.find_solution()

# PRINT THE MODEL OF THE SOLUTION #
solver.model_to_string()
solver.model_to_image()

