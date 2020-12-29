from apilib import *
import asyncio

def main():
    asyncio.get_event_loop().run_until_complete(apilib.connection("11671830","Azerty123"))


if __name__ == "__main__":
    main()


