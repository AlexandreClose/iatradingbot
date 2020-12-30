from apilib import *
import asyncio
import websockets

def main():
    lib=apilib()
    result = asyncio.get_event_loop().run_until_complete(lib.connection("11671830","Azerty123"))
    print (result)


if __name__ == "__main__":
    main()


