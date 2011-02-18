class StockpileType(object):
    def __init__(self, description, subtypes = None):
        self.description = description
        self.subtypes = subtypes if subtypes else []
