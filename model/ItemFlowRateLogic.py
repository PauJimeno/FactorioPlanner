from z3 import *

from model.DirectionalElement import DirectionalElement
from model.GridElement import GridElement


class ItemFlowRateLogic(DirectionalElement, GridElement):
    """
    This class contains all the constraints that implement the logic of the flow rate of items.
    Note that all the constraints of the model are explained in detail in the project report.

    :param width: Width of the blueprint
    :type width: Int

    :param height: Height of the blueprint
    :type height: Int

    :param route: reference to the route variable
    :type route: Arrat[Array] EnumSort

    :param conveyor: reference to the variable conveyor
    :type conveyor: Arrat[Array] EnumSort

    :param inserter: reference to the inserter variable
    :type inserter: Arrat[Array] EnumSort

    :param recipes: Contains the recipes that the assemblers in the blueprint will use, for each recipe it has a list
                    of the items it requires and which rate in items/min needs and the outputting item and rate.
    :type recipes: Dictionary
    """
    def __init__(self, width, height, in_out_pos, inserter, conveyor, route):
        DirectionalElement.__init__(self)
        GridElement.__init__(self, width, height, in_out_pos)

        self.conveyor = conveyor
        self.inserter = inserter
        self.route = route


        # Z3 variables that represent the rate of items/min a cell recives and outputs
        self.input_flow_rate = [[Real(f"INPUT_FLOW_RATE_{i}_{j}") for i in range(width)] for j in range(height)]
        self.output_flow_rate = [[Real(f"OUTPUT_FLOW_RATE_{i}_{j}") for i in range(width)] for j in range(height)]

    def item_input_rate(self):
        """
        The input cells rate is the rate specified in the input coordinates

        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
        # The input cells rate is the rate specified in the input coordinates
        return [self.input_flow_rate[coord[0]][coord[1]] == self.input_rate(coord[0], coord[1]) for coord in self.input]

    def variable_input_rate(self):
        """
        The input cells rate is the rate specified in the input coordinates

        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
        return [And(self.input_flow_rate[coord[0]][coord[1]] >= 0, self.input_flow_rate[coord[0]][coord[1]] <= 450) for coord in self.input]

    def part_of_route(self):
        """
        A cell that cant transport items (route = 0) also cant have item flow rate (item_flow_rate = 0)

        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
        return [Implies(self.route[i][j] == 0, And(self.input_flow_rate[i][j] == 0, self.output_flow_rate[i][j] == 0))
                for i in range(self.height) for j in range(self.width)]

    def belt_item_flow_propagation(self):
        """
        Creates a constraint that encodes the behaviour of how the ammount of items a conveyor
        carries is propagated.
        The input rate of a conveyor is the sum of all the outputs of the neighbouring cells
        (inserter or conveyor) pointing towards the conveyor.
        The output rate of a conveyor is its input minus the sum of inputs of inserters taking
        items from the conveyor.

        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
        belt_flow_rate_propagation = []

        for i in range(self.height):
            for j in range(self.width):
                belt_input_cells = []
                belt_output_cells = []
                for direction in range(1, self.n_dir):
                    x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                    if 0 <= x < self.height and 0 <= y < self.width:
                        # Valor de sortida de les caselles que aporten items a la casella central
                        belt_input_cells.append(If(And(self.conveyor[i][j] != self.direction[direction],
                                                    Or(self.conveyor[x][y] == self.opposite_dir[direction],
                                                       self.inserter[x][y] == self.opposite_dir[direction])),
                                                    self.output_flow_rate[x][y], 0))
                        # Valor d'entrada de les caselles que agafen items de la casella central
                        belt_output_cells.append(If(self.inserter[x][y] == self.direction[direction],
                                                    self.input_flow_rate[x][y], 0))

                # L'entrada d'una cinta és la suma de sortides de les caselles adjacents que aporten items
                if not self.is_input(i, j):
                    belt_flow_rate_propagation.append(Implies(self.conveyor[i][j] != self.direction[0],
                                                              And(self.input_flow_rate[i][j] == sum(belt_input_cells), self.input_flow_rate[i][j]<=450)))
                # La sortida d'una cinta és la seva entrada menys la suma d'entrada de les caselles adjacents que prenen items
                belt_flow_rate_propagation.append(Implies(self.conveyor[i][j] != self.direction[0],
                                                          And(self.output_flow_rate[i][j] == (self.input_flow_rate[i][j] - sum(belt_output_cells)), self.output_flow_rate[i][j]>=0)))
        return belt_flow_rate_propagation

    def inserter_item_flow_propagation(self):
        """
        Creates a constraint that encodes the behaviour of how the ammount of items an inserter
        carries is propagated.
        The input rate of an inserter is at max 50 if the input cell carries 50 or more items,
        in the other hand if the input cell carries less than 50 the inserter will carry at most
        the same amount of items.
        The ouput flow rate of the inseter will always be the same as the input.

        :return: List with all the logic regarding the constarint
        :rtype: Array
        """
        
        inserter_item_flow_propagation = []

        for i in range(self.height):
            for j in range(self.width):
                if not self.is_input(i, j):
                    inserter_input_cells = []
                    for direction in range(1, self.n_dir):
                        x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                        if 0 <= x < self.height and 0 <= y < self.width:
                            # L'entrada d'un inserter ha de ser mes petita o igual a 50 en cas que l'entrada de la casella d'on agafa items li entrin 50 o més items
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                        self.input_flow_rate[x][y] >= 50),
                                                        And(self.input_flow_rate[i][j] <= 50, self.input_flow_rate[i][j] == self.output_flow_rate[i][j])))
                            # L'entrada d'un inserter ha de ser mes petita o igual a l'entrada de la casella d'on agafa si l'entrada d'aquesta és mes petita que 50
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                               self.input_flow_rate[x][y] < 50, self.route[x][y] != 0), # La ruta ha de ser != 0 (no esta agafant d'un assembler)
                                                           And(self.input_flow_rate[i][j] <= self.input_flow_rate[x][y], self.output_flow_rate[i][j] == self.input_flow_rate[i][j])))
                            inserter_input_cells.append(Implies(And(self.inserter[i][j] == self.opposite_dir[direction],
                                                                    self.route[x][y] == 0), And(self.input_flow_rate[i][j] == self.output_flow_rate[i][j], self.input_flow_rate[i][j]<=50)))

                    inserter_item_flow_propagation.append(Implies(self.inserter[i][j] != self.direction[0], And(And(inserter_input_cells), self.input_flow_rate[i][j] > 0)))
        return inserter_item_flow_propagation

    def item_loss(self):
        """
        Sums the number of items that are not getting used by assemblers (loss),
        the loss happens when the flow rate of aconveyor feeding an inserter feeding an assembler
        is greater than 0.

        :return: sum of unsused items, used for optimization 
        :rtype: Array
        """
        loss = []
        for i in range(self.height):
            for j in range(self.width):
                for direction in range(1, self.n_dir):
                    x, y = i + self.displacement[direction][0], j + self.displacement[direction][1]
                    if 0 <= x < self.height and 0 <= y < self.width:
                        # En la direcció de la cinta hi ha un inserter amb la mateixa direcció
                        loss.append(If(And(self.conveyor[i][j] != self.direction[0], self.inserter[x][y] == self.conveyor[i][j]), self.output_flow_rate[i][j], 0))
        return sum(loss)

    def item_output(self):
        """
        Sums the number of output items produced by the blueprint.

        :return: sum of produced items, used for optimization 
        :rtype: Array
        """
        item_output = []
        for pos in self.output:
            i = pos[0]
            j = pos[1]
            item_output.append(self.output_flow_rate[i][j])
        return sum(item_output)

    def constraints(self):
        """
        Creates a list of all the constarints representing the logic of the class

        :return: class constraints compacted in a single list
        :rtype: Array
        """
        return self.variable_input_rate() + self.belt_item_flow_propagation() + self.inserter_item_flow_propagation() + self.part_of_route()
