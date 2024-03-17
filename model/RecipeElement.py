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
        self.max_items = len(self.item_to_variable) + 1

        # Maximum amount of items a recipie needs at a time
        self.max_items_in = max(pair[0] for recipe in recipes.values() for pair in recipe["IN"])

        # Maximum amount of items a recipie outputs at a time
        self.max_items_out = max(pair[0] for recipe in recipes.values() for pair in recipe["OUT"])

    def initialize_map_dictionaries(self, recipes):
        item_to_variable = {}
        variable_to_item = {}
        n_items = 1
        for recipe_name, recipe in recipes.items():
            items = recipe['IN'] + recipe['OUT']
            for item in items:
                if not item[1] in item_to_variable:
                    item_to_variable.update({item[1]: n_items})
                    variable_to_item.update({n_items: item[1]})
                    n_items += 1

        return item_to_variable, variable_to_item

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

