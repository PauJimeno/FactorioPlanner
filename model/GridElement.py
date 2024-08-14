class GridElement:
    """
    Abstract class that implements shared behaviours between elements that are grid based

    :param width: Width of the blueprint
    :type width: Int

    :param height: Height of the blueprint
    :type height: Int

    :param in_out_positions: Contains the input and output positions and type of item carrying
    :type in_out_positions: Dictionary
    """
    

    def __init__(self, width, height, in_out_positions):
        self.width = width
        self.height = height
        self.input = []
        self.output = []
        self.in_out_positions = in_out_positions
        if in_out_positions:
            # Separate the pair coordinates into two lists
            self.input = list(in_out_positions['IN'].keys())
            self.output = list(in_out_positions['OUT'].keys())

    def is_output(self, x, y):
        """
        Returns if a postition in the blueprint is an output

        :param x: row coordinate
        :type x: Int

        :param y: column coordinate
        :type y: Int

        :return: a boolean that is true if the (x,y) pos is an actual output
        :rtype: Bool
        """
        is_output = False
        if (x, y) in self.in_out_positions['OUT']:
            is_output = True
        return is_output

    def is_input(self, x, y):
        """
        Returns if a postition in the blueprint is an input

        :param x: row coordinate
        :type x: Int

        :param y: column coordinate
        :type y: Int

        :return: a boolean that is true if the (x,y) pos is an actual input
        :rtype: Bool
        """
        is_input = False
        if (x, y) in self.in_out_positions['IN']:
            is_input = True
        return is_input

    def input_item(self, x, y):
        """
        Returns the input item at the position (x,y)

        :param x: row coordinate
        :type x: Int

        :param y: column coordinate
        :type y: Int

        :return: the name of the item that the input cell at (x,y) is carrying
        :rtype: String
        """
        return self.in_out_positions['IN'][(x, y)]['ITEM']

    def output_item(self, x, y):
        """
        Returns the output item at the position (x,y)

        :param x: row coordinate
        :type x: Int

        :param y: column coordinate
        :type y: Int

        :return: the name of the item that the output cell at (x,y) is carrying
        :rtype: String
        """
        return self.in_out_positions['OUT'][(x, y)]['ITEM']

    def input_rate(self, x, y):
        """
        Returns the rate of the item at the position (x,y)

        :param x: row coordinate
        :type x: Int

        :param y: column coordinate
        :type y: Int

        :return: number of items per minute of the input cell (x,y)
        :rtype: Int
        """
        return self.in_out_positions['IN'][(x, y)]['RATE']
