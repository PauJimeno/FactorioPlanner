from z3 import *

from model.RecipeElement import RecipeElement


class RecipeLogic(RecipeElement):
    def __init__(self, recipes):
        RecipeElement.__init__(self, recipes)

        self.recipe_bits = math.ceil(self.max_recipes)
        self.item_bits = math.ceil(self.max_items)
        self.items_in_bits = math.ceil(self.max_items_in)
        self.items_out_bits = math.ceil(self.max_items_out)

        # Matriu que indexa receptes amb quants items de cada tipus necessita com a entrada
        self.recipe_input = Array('inputs', BitVecSort(self.recipe_bits), ArraySort(BitVecSort(self.item_bits), BitVecSort(self.items_in_bits)))

        # Matriu que indexa receptes amb quants items de cada tipus produeix com a sortida
        self.recipe_output = Array('outputs', BitVecSort(self.recipe_bits), ArraySort(BitVecSort(self.item_bits), BitVecSort(self.items_out_bits)))

    def input_recipe_values(self):
        constant_input_values = []
        for recipe_index, (recipe_name, recipe) in enumerate(self.recipes.items()):
            item_variables_in = [0] * self.max_items
            for item in recipe['IN']:
                item_variables_in[self.item_to_variable[item[1]]] = item[0]
            constant_input_values.extend(
                self.recipe_input[recipe_index][i] == item_in
                for i, item_in in enumerate(item_variables_in)
            )
        return constant_input_values

    def output_recipe_values(self):
        constant_output_values = []
        for recipe_index, (recipe_name, recipe) in enumerate(self.recipes.items()):
            item_variables_out = [0] * self.max_items
            for item in recipe['OUT']:
                item_variables_out[self.item_to_variable[item[1]]] = item[0]
            constant_output_values.extend(
                self.recipe_output[recipe_index][i] == item_out
                for i, item_out in enumerate(item_variables_out)
            )
        return constant_output_values

    def constraints(self):
        return self.input_recipe_values() + self.output_recipe_values()

