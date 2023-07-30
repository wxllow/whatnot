# Whatnot API

Work-in-progress unofficial asynchronous API wrapper for [Whatnot](https://www.whatnot.com) API.

***Currently, authorized actions are currently broken due to API changes, however, most of the project is still usable. If you would like to help fix it, please contribute :)***

If anyone wants to take on this project, let me know, because I do not have the time to work on it and I have no use for it anymore either way.

## Download

`poetry add whatnot` *or* `pip install whatnot`

## Roadmap

See [ROADMAP.md](ROADMAP.md)

## Example

```python
import asyncio
from whatnot import Whatnot

async def main():
    async with Whatnot() as whatnot:
        # Get the whatnot account
        whatnot_user = await whatnot.get_user("whatnot")
        print(whatnot_user.username)
        # OR await whatnot.get_user_by_id("21123")

        # Get user's lives
        lives = await whatnot.get_user_lives(whatnot_user.id)

        # Print out all of the lives
        for live in lives:
            print(live.title)


asyncio.run(main())
```

## Project Layout

- whatnot
  - exc.py - Exceptions
  - interactive_login.py - Interactive Login Tool
  - queries.py - Queries
  - types.py - Types
  - utils.py - Utilities
  - whatnot.py - Main class

## Disclaimer

This project is unofficial and is not affiliated with or endorsed by Whatnot.
