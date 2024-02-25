from model.FactorioSolver import FactorioSolver
from model.InputInterface import InputInterface


# GRAPHIC INTERFACE #
# interface = InputInterface()

# FOR TESTING #

# SOLVER DECLARATION #
blueprint_width = 8
blueprint_height = 8
route_pos = [((0, 0), (7, 7)), ((7, 0), (7, 7))]
solver = FactorioSolver(blueprint_width, blueprint_height, route_pos)

# FIND A SOLUTION #
if solver.find_solution():
    # PRINT THE MODEL OF THE SOLUTION #
    solver.model_to_string()
    solver.model_to_image()

else:
    print("UNSAT")
