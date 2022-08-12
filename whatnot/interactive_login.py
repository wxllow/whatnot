import asyncio
from getpass import getpass

from . import Whatnot, exc


async def main():
    async with Whatnot() as whatnot:
        while True:
            try:
                email = input("Email: ")
                password = getpass("Password: ")

                await whatnot.login(email, password, interaction=True)
                await whatnot.save_session()
                break
            except exc.AuthenticationError as e:
                print(f"{e}\nLogin failed! Try again.")

        print(
            f"Login successful! Hello {await whatnot.get_user_by_id(whatnot.user_id).username}!"
        )


asyncio.run(main())
