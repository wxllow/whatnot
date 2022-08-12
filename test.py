import asyncio

from whatnot import Whatnot


async def main():
    async with Whatnot() as whatnot:
        await whatnot.load_session()

        # Test getting account info
        await whatnot.get_account_info()
        await whatnot.get_default_payment()

        # Test getting user info
        user_id = (await whatnot.get_user("whatnot")).id
        await whatnot.get_user_by_id(user_id)

        # Test getting user lives
        lives = await whatnot.get_user_lives(user_id)

        # Test getting a live
        for l in [live.id for live in lives]:
            await whatnot.get_live(l)


asyncio.run(main())
