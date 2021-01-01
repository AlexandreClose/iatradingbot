from apilib import xtbClient
import asyncio

async def main_process():
    client=xtbClient()
    res1 = await client.login("11671830","Azerty123")
    res2 = await client.getNews()
    print ( res2 )

def main():
    asyncio.get_event_loop().run_until_complete( main_process( ) )

if __name__ == "__main__":
    main()


