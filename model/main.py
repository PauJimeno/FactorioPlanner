from model.FactorioSolver import FactorioSolver
from model.InputInterface import InputInterface

'''
COSES A FER:
    - !!IMPORTANT!! FER QUE UN INSERTER PUGUI AGAFAR ITEMS D'UNA CINTA QUE APUNTA CAP A ELL NOMES EN CAS QUE L'INSERTER 
      ESTIGUI POSANT ITEMS A UN ASSEMBLER (FINAL DE RUTA)
    - Criteris dels outputs
    - Provar de posar el criteri d'optimització la minimització dels valors que pren la ruta (DONE)
    - Apuntar a la memoria els constraints que creo i el raonament darrere (DONE)
    - Començar amb els constructors, receptes i item flow rate (CONSTRUCTROS DONE, FLOWRATE DONE, )
'''

# GRAPHIC INTERFACE #
# interface = InputInterface()

# FOR TESTING #

'''
CODI PROVISIONAL PER TESTING DE RECEPTES
    Item 0 : Iron Plate
    Item 1 : Copper Plate
    Item 2 : Iron Stick
    Item 3 : Copper Cable
    Item 4 : Electronic Circuit
Una recipe compta amb els elements i quantitat d'entrada i sortida juntament amb el temps d'execució de la recepta.
'''

'''
De moment només se selecciona una sola recipe, un cop estiguin els constraints muntats caldrà crear un diccionari
amb totes les receptes involucrades en un cert ítem de sortida.
'''


recipe_1 = {"IRON_STICK": {"IN": [(1, 1)],
                           "OUT": [(2, 4)],
                           "TIME": 0.5},

            "COPPER_CABLE": {"IN": [(1, 2)],
                             "OUT": [(2, 4)],
                             "TIME": 0.5}
            }

recipe_2 = {"COPPER_CABLE": {"IN": [(1, 2)],
                             "OUT": [(2, 3)],
                             "TIME": 0.5}}

electronic_circuit_test = {
    "COPPER_CABLE": {
        "IN": [(1, 1)],
        "OUT": [(2, 3)]
    },
    "ELECTRONIC_CIRCUIT": {
        "IN": [(1, 0), (2, 3)],
        "OUT": [(1, 4)]
    }
}

# SOLVER DECLARATION #
blueprint_width = 7
blueprint_height = 7

in_out_pos = {
    'IN': {(0, 0): 0, (0, 6): 1},
    'OUT': {(6, 6): 4, (6, 0): 4},
}

solver = FactorioSolver(blueprint_width, blueprint_height, in_out_pos, electronic_circuit_test)

# FIND A SOLUTION #
if solver.find_solution():
    # PRINT THE MODEL OF THE SOLUTION #
    solver.model_to_string()
    solver.model_to_image()

else:
    print("UNSAT")
