class HistoricProvider():
    def __init__(self, *providers):
        self.providers=providers

    async def fetch_and_store_max_history(self, symbol ):
        for provider in self.providers:
            await provider.send_max_history( symbol )

    async def fetch_time_delta_history(self, symbol, minutes_number):
        for provider in self.providers:
            return await provider.fetch_time_delta_history( symbol, minutes_number )



