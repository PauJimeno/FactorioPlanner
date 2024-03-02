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

recipes = {"IRON_STICK": {"IN": []}}




# SOLVER DECLARATION #
blueprint_width = 9
blueprint_height = 9
input_positions = [(0, 0)]
output_positions = [(8, 8), (0, 8)]
solver = FactorioSolver(blueprint_width, blueprint_height, input_positions, output_positions)

# FIND A SOLUTION #
if solver.find_solution():
    # PRINT THE MODEL OF THE SOLUTION #
    solver.model_to_string()
    solver.model_to_image()

else:
    print("UNSAT")
