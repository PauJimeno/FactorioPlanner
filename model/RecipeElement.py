class RecipeElement:
    """
    Abstract class that implements shared behaviours between elements that use recipes

    :param recipes: Contains the recipes that the assemblers in the blueprint will use, for each recipe it has a list
                    of the items it requires and which rate in items/min needs and the outputting item and rate.
    :type recipes: Dictionary
    """

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
        """
        Creates the dictionaries that map the item names to item ids and vice-versa
        
        :param recipes: Contains the recipes that the assemblers in the blueprint will use, for each recipe it has a list
                        of the items it requires and which rate in items/min needs and the outputting item and rate.
        :type recipes: Dictionary

        :return: A dictionary that for each item name (key), has its id (value),
                 and a dictionary that for each item id (key), has its name (value)
        :rtype: Dictionary, Dictionary
        """
        item_to_variable = {}
        variable_to_item = {}
        n_items = 1
        for recipe_name, recipe in recipes.items():
            items = recipe['IN'] + recipe['OUT']
            # For all the items present in the recipes
            for item in items:
                if not item[0] in item_to_variable:
                    # Cretes the mapping between name and id
                    item_to_variable.update({item[0]: n_items})
                    variable_to_item.update({n_items: item[0]})
                    n_items += 1

        return item_to_variable, variable_to_item

    def input_recipe_values(self):
        """
        Creates a matrix that each row represents a recipe and each column the items,
        the value each cell takes is the amount of items used by the recipe (0 if not used)

        :return: A matrix with the amount of items each recipe uses
        :rtype: Array[Array]
        """
        recipe_input = []
        for recipe_index, (recipe_name, recipe) in enumerate(self.recipes.items()):
            item_variables_in = [0] * self.max_items
            for item in recipe['IN']:
                item_variables_in[self.item_to_variable[item[0]] - 1] = item[1]
            recipe_input.append(item_variables_in)

        return recipe_input

    def output_recipe_values(self):
        """
        Creates a matrix that each row represents a recipe and each column the items,
        the value each cell takes is the amount of items produced by the recipe (0 if not produced)

        :return: A matrix with the amount of items each recipe produces
        :rtype: Array[Array]
        """
        recipe_output = []
        for recipe_index, (recipe_name, recipe) in enumerate(self.recipes.items()):
            item_variables_out = [0] * self.max_items
            for item in recipe['OUT']:
                item_variables_out[self.item_to_variable[item[0]] - 1] = item[1]
            recipe_output.append(item_variables_out)

        return recipe_output

    def model_item_id(self, item_id):
        """
        Given a item name returns its id if the name exists or -1 if it doesn't
        
        :param item_id: Item name
        :type item_id: String

        :return: The mapped id to the name
        :rtype: Int
        """
        model_item_id = -1
        if item_id in self.item_to_variable:
            model_item_id = self.item_to_variable[item_id]
        return model_item_id

    def memory_item_id(self, item_id):
        """
        Given a item id returns its name if the name exists or -1 if it doesn't
        
        :param item_id: Item id
        :type item_id: Int

        :return: The mapped name to the id
        :rtype: String
        """
        model_item_id = -1
        if item_id in self.variable_to_item:
            model_item_id = self.variable_to_item[item_id]
        return model_item_id

    def is_recipe_input(self, recipe_name, item_name):
        """
        Checks if the item_name is an input of the recipe_name
        
        :param recipe_name: Recipe name
        :type recipe_name: String

        :param item_name: Item name
        :type item_name: String

        :return: True if the item_name is an input of recipe_name, false otherwise
        :rtype: Bool
        """
        is_input = False
        recipe = self.recipes[recipe_name]
        for input in recipe['IN']:
            if input[0] == item_name:
                is_input = True
                break
        return is_input

    def is_recipe_output(self, recipe_name, item_name):
        """
        Checks if the item_name is an output of the recipe_name
        
        :param recipe_name: Recipe name
        :type recipe_name: String

        :param item_name: Item name
        :type item_name: String

        :return: True if the item_name is an output of recipe_name, false otherwise
        :rtype: Bool
        """
        is_output = False
        recipe = self.recipes[recipe_name]
        for output in recipe['OUT']:
            if output[0] == item_name:
                is_output = True
                break
        return is_output
