from abc import ABC, abstractmethod


class GridElement(ABC):
    # Abstract class that implements shared behaviours between elements that are grid based

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
        is_output = False
        if (x, y) in self.in_out_positions['OUT']:
            is_output = True
        return is_output

    def is_input(self, x, y):
        is_input = False
        if (x, y) in self.in_out_positions['IN']:
            is_input = True
        return is_input

    def input_item(self, x, y):
        return self.in_out_positions['IN'][(x, y)]

    def output_item(self, x, y):
        return self.in_out_positions['OUT'][(x, y)]
