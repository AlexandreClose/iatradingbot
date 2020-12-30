from apilib import *
import asyncio
import websocket

def main():
    lib=apilib()
    result =asyncio.get_event_loop().run_until_complete(lib.connection("11671830","Azerty123"))
    print (result)
    result=asyncio.get_event_loop().run_until_complete(lib.getCalendar(result[0]))
    print(result)
    lib.connectionClosed(result[0])
if __name__ == "__main__":
    main()


