from model.FactorioSolver import FactorioSolver
from model.InputInterface import InputInterface

'''
COSES A FER:
    - !!IMPORTANT!! FER QUE UN INSERTER PUGUI AGAFAR ITEMS D'UNA CINTA QUE APUNTA CAP A ELL NOMES EN CAS QUE L'INSERTER 
      ESTIGUI POSANT ITEMS A UN ASSEMBLER (FINAL DE RUTA)
    - Criteris dels outputs
    - Provar de posar el criteri d'optimització la minimització dels valors que pren la ruta (DONE)
    - Apuntar a la memoria els constraints que creo i el raonament darrere (DONE)
    - Començar amb els constructors, receptes i item flow rate (CONSTRUCTROS DONE, )
'''

# GRAPHIC INTERFACE #
# interface = InputInterface()

# FOR TESTING #

'''
CODI PROVISIONAL PER TESTING DE RECEPTES
    Item 1 : Iron Plate
    Item 2 : Copper Plate
    Item 3 : Copper Cable
    Item 4 : Iron Stick
Una recipe compta amb els elements i quantitat d'entrada i sortida juntament amb el temps d'execució de la recepta.
'''

'''
De moment només se selecciona una sola recipe, un cop estiguin els constraints muntats caldrà crear un diccionari
amb totes les receptes involucrades en un cert ítem de sortida.
'''


recipe_1 = {"IRON_STICK": {"IN": [(1, 1)],
                           "OUT": [(2, 4)],
                           "TIME": 0.5}}

recipe_2 = {"COPPER_CABLE": {"IN": [(1, 2)],
                             "OUT": [(2, 3)],
                             "TIME": 0.5}}

# SOLVER DECLARATION #
blueprint_width = 8
blueprint_height = 8

in_out_pos = {
    'IN': {(0, 0): 1, (5, 2): 1},
    'OUT': {(7, 7): 4},
}

solver = FactorioSolver(blueprint_width, blueprint_height, in_out_pos, recipe_1)

# FIND A SOLUTION #
if solver.find_solution():
    # PRINT THE MODEL OF THE SOLUTION #
    solver.model_to_string()
    solver.model_to_image()

else:
    print("UNSAT")
