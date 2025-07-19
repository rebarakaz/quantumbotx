class BaseStrategy:
    def __init__(self, bot):
        self.bot = bot  # bot instance yang punya atribut: market, lot_size, dst.

    def analyze(self):
        """Override this method in your custom strategy"""
        raise NotImplementedError("analyze() harus diimplementasikan di strategi turunan.")
