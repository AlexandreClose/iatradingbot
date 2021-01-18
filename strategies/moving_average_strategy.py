from analyzer.moving_average_analyzer import MovingAverageAnalyzer


class ExponentialMovingAverageStrategy:
    def __init__(self, symbol):
        self.exponential_moving_average_analyzer = MovingAverageAnalyzer()