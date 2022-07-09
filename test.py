import asyncio
import json
from pprint import pprint

from whatnot import Whatnot


async def main():
    global whatnot
    whatnot = Whatnot()

    try:
        await whatnot.load_session()
    except Exception as e:
        print(e)
        print("Could not load session; Logging in...")
        await whatnot.login("wxllow@wxllow.dev", "5KKxEQh2Qr3!U9#%")
        await whatnot.save_session()

    # pprint((await whatnot.get_user_lives("1240048"))[0])
    # pprint(
    #     "https://www.whatnot.com/live/"
    #     + (await whatnot.get_user_lives("1240048", first=1))[0]["id"]
    # )

    pprint((await whatnot.get_live("a2d3d2a4-d5a7-42a0-aa93-4cbd22fbd951")))
    # await whatnot.get_live("a2d3d2a4-d5a7-42a0-aa93-4cbd22fbd951")


if __name__ == "__main__":
    asyncio.run(main())
