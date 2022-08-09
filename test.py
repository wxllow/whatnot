from whatnot import Whatnot
import asyncio


async def main():
    whatnot = Whatnot()

    print((await whatnot.get_user("jlsgaming")).id)
    print("\n\n")
    print(await whatnot.get_user("abcxyz"))


asyncio.run(main())
