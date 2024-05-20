from abc import ABC, abstractmethod


class RecipeElement(ABC):
    # Abstract class that implements shared behaviours between elements that use recipes
    def __init__(self, recipes):
        self.recipes = recipes

        # Number of unique recipes used in the blueprint
        self.max_recipes = len(self.recipes)

        # Dictionaries that map item ID (python memory) to item ID in z3 memory and vice-versa
        self.item_to_variable, self.variable_to_item = self.initialize_map_dictionaries(recipes)

        # Number of unique items present in the blueprint
        self.max_items = len(self.item_to_variable)

        # Maximum amount of items a recipie needs at a time
        self.max_items_in = max(pair[1] for recipe in recipes.values() for pair in recipe["IN"])

        # Maximum amount of items a recipie outputs at a time
        self.max_items_out = max(pair[1] for recipe in recipes.values() for pair in recipe["OUT"])

        # Matrix of items needed of a certain recipe
        self.recipe_input = self.input_recipe_values()

        # Matrix of items a certain recipe outputs
        self.recipe_output = self.output_recipe_values()

    def initialize_map_dictionaries(self, recipes):
        item_to_variable = {}
        variable_to_item = {}
        n_items = 1
        for recipe_name, recipe in recipes.items():
            items = recipe['IN'] + recipe['OUT']
            for item in items:
                if not item[0] in item_to_variable:
                    item_to_variable.update({item[0]: n_items})
                    variable_to_item.update({n_items: item[0]})
                    n_items += 1

        return item_to_variable, variable_to_item

    def input_recipe_values(self):
        recipe_input = []
        for recipe_index, (recipe_name, recipe) in enumerate(self.recipes.items()):
            item_variables_in = [0] * self.max_items
            for item in recipe['IN']:
                item_variables_in[self.item_to_variable[item[0]] - 1] = item[1]
            recipe_input.append(item_variables_in)

        return recipe_input

    def output_recipe_values(self):
        recipe_output = []
        for recipe_index, (recipe_name, recipe) in enumerate(self.recipes.items()):
            item_variables_out = [0] * self.max_items
            for item in recipe['OUT']:
                item_variables_out[self.item_to_variable[item[0]] - 1] = item[1]
            recipe_output.append(item_variables_out)

        return recipe_output

    def model_item_id(self, item_id):
        model_item_id = -1
        if item_id in self.item_to_variable:
            model_item_id = self.item_to_variable[item_id]
        return model_item_id

    def memory_item_id(self, item_id):
        model_item_id = -1
        if item_id in self.variable_to_item:
            model_item_id = self.variable_to_item[item_id]
        return model_item_id

    def is_recipe_input(self, recipe_name, item_name):
        is_input = False
        recipe = self.recipes[recipe_name]
        for input in recipe['IN']:
            if input[0] == item_name:
                is_input = True
                break
        return is_input

    def is_recipe_output(self, recipe_name, item_name):
        is_output = False
        recipe = self.recipes[recipe_name]
        for output in recipe['OUT']:
            if output[0] == item_name:
                is_output = True
                break
        return is_output
