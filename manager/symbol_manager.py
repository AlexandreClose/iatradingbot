from manager.historic_manager import HistoricManager
from manager.tick_manager import TickManager
from utils.singleton import Singleton

@Singleton
class SymbolManager:
    def __init__(self ):
        self.symbols = []

    async def register_symbol(self, symbol ):
        if symbol not in self.symbols:

            await HistoricManager.instance().register_symbol( symbol)
            await TickManager.instance().register_symbol( symbol )

            self.symbols.append( symbol )

symbol_manager = SymbolManager.instance()
