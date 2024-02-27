from model.FactorioSolver import FactorioSolver
from model.InputInterface import InputInterface

'''
COSES A FER:
    - Criteris dels outputs
    - Provar de posar el criteri d'optimització la minimització dels valors que pren la ruta
    - Apuntar a la memoria els constraints que creo i el raonament darrere
    - Començar amb els constructors, receptes i item flow rate
'''

# GRAPHIC INTERFACE #
# interface = InputInterface()

# FOR TESTING #

# SOLVER DECLARATION #
blueprint_width = 10
blueprint_height = 10
input_positions = [(0, 0)]
output_positions = [(7, 7), (0, 7), (7, 3), (5, 0), (9, 9)]
solver = FactorioSolver(blueprint_width, blueprint_height, input_positions, output_positions)

# FIND A SOLUTION #
if solver.find_solution():
    # PRINT THE MODEL OF THE SOLUTION #
    solver.model_to_string()
    solver.model_to_image()

else:
    print("UNSAT")
