import asyncio

from whatnot import Whatnot, exc

whatnot = Whatnot()


async def authenticated():
    # Test getting account info
    account_info = await whatnot.get_account_info()
    await whatnot.get_default_payment()

    print(f"Hello, {account_info.username}!")


async def general():
    # Test getting user info
    user_id = (await whatnot.get_user("whatnot")).id
    await whatnot.get_user_by_id(user_id)

    # Test getting user lives
    lives = await whatnot.get_user_lives(user_id)

    # Test getting a single live
    for l in [live.id for live in lives]:
        await whatnot.get_live(l)


async def main():
    # TRy general without auth
    await general()

    # Try authenticated without auth
    try:
        await authenticated()
        raise AssertionError("Authenticated should have failed")
    except exc.AuthenticationRequired:
        pass

    # Try general and authenticated with auth
    await whatnot.load_session()
    await general()
    await authenticated()

    # Close the session
    await whatnot.close()


asyncio.run(main())
