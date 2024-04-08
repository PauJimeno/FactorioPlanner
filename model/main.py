from model.FactorioSolver import FactorioSolver
import json


def load_recipes(file_name):
    with open(file_name, 'r') as f:
        loaded_recipes = json.load(f)
    return loaded_recipes


recipes = load_recipes("recipes/recipes.json")

test_1 = {}
test_1.update({"copper-cable": recipes["copper-cable"]})
test_1.update({"electronic-circuit": recipes["electronic-circuit"]})


# SOLVER DECLARATION #
blueprint_width = 6
blueprint_height = 6

in_out_pos = {
    'IN': {(0, 0): {'ITEM': 'iron-plate', 'RATE': 200}, (0, 5): {'ITEM': 'copper-plate', 'RATE': 100}},
    'OUT': {(5, 5): {'ITEM': 'electronic-circuit'}},
}

solver = FactorioSolver(blueprint_width, blueprint_height, in_out_pos, test_1)

# FIND A SOLUTION #
if solver.find_solution():
    # PRINT THE MODEL OF THE SOLUTION #
    solver.model_to_string()
    solver.model_to_image()

else:
    print("UNSAT")
