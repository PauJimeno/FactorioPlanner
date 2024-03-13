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
blueprint_width = 8
blueprint_height = 8

in_out_pos = {
    'IN': [(0, 3)],
    'OUT': [(7, 7), (0, 7), (7, 0), (0, 0)],
}

solver = FactorioSolver(blueprint_width, blueprint_height, in_out_pos)

# FIND A SOLUTION #
if solver.find_solution():
    # PRINT THE MODEL OF THE SOLUTION #
    solver.model_to_string()
    solver.model_to_image()

else:
    print("UNSAT")
