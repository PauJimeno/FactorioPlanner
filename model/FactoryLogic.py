class FactoryLogic:
    def __init__(self, blueprint_width, blueprint_height, conveyor_logic, inserter_logic):
        self.conveyor_logic = conveyor_logic
        self.inserter_logic = inserter_logic
        self.width = blueprint_width
        self.blueprint_height

    def collision(self):
        collision = []



