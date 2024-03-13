from abc import ABC, abstractmethod


class GridElement(ABC):
    # Abstract class that implements shared behaviours between elements that are grid based

    def __init__(self, width, height, in_out_positions):
        self.width = width
        self.height = height
        self.input = []
        self.output = []
        if in_out_positions:
            self.input = in_out_positions['IN']
            self.output = in_out_positions['OUT']

    def is_output(self, x, y):
        is_output = False
        for pos in self.output:
            if x == pos[0] and y == pos[1]:
                is_output = True
        return is_output

    def is_input(self, x, y):
        is_output = False
        for pos in self.input:
            if x == pos[0] and y == pos[1]:
                is_output = True
        return is_output
