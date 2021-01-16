from analyzer.exponential_moving_average_analyzer import ExponentialMovingAverageAnalyzer


class ExponentialMovingAverageStrategy:
    def __init__(self, symbol):
        self.exponential_moving_average_analyzer = ExponentialMovingAverageAnalyzer( )