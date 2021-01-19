from historicprovider.historic_manager import HistoricManager
from historicprovider.xtb_historic_provider import XtbHistoricProvider
from tick_manager.tick_manager import TickManager
from utils.singleton import Singleton

@Singleton
class SymbolManager():
    def __init__(self ):
        self.symbols = []
        self.trading_client = None

    async def register_client(self, trading_client):
        self.trading_client = trading_client

    async def register_symbol(self, symbol ):
        if symbol not in self.symbols:

            await HistoricManager.instance().register_provider( XtbHistoricProvider( self.trading_client))
            await HistoricManager.instance().register_symbol( symbol)
            await TickManager.instance().register_client( self.trading_client )
            await TickManager.instance().register_symbol( symbol )


            self.symbols.append( symbol )
