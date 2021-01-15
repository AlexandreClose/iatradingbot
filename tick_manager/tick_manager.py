import pandas as pd
import matplotlib.pyplot as plt


class TickManager:
    def __init__(self, symbols, client ):
        self.symbols = symbols
        self.client = client
        self.client.follow_tick_prices( symbols )

    async def get_tick_datas_updated(self, symbol ):
        return self.client.get_tick_prices( symbol )

    async def plot_tick_prices(self, symbol, label='bid' ):
        datas = await self.get_tick_datas_updated( symbol )
        tick_prices = pd.DataFrame(datas)
        tick_prices.set_index('timestamp', inplace = True)
        tick_prices.plot(y=label)
        plt.show()


