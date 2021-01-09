class HistoricProvider():
    def __init__(self, *providers):
        self.providers=providers

    async def fetch_and_store_max_history(self, symbol ):
        for provider in self.providers:
            await provider.send_max_history( symbol )


