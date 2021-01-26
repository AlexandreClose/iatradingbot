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

    async def unregister_symbol(self, symbol ):
        if symbol in self.symbols:
            await HistoricManager.instance().unregister_symbol( symbol)
            await TickManager.instance().unregister_symbol( symbol )
            self.symbols.remove( symbol )

symbol_manager = SymbolManager.instance()
