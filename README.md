# Whatnot API

Very early work-in-progress asynchronous API wrapper for and documentation of the [Whatnot](https://www.whatnot.com) API.

## Roadmap

- [x] Authentication
- [x] Get user's livestreams
- [x] Get a livestream
- [ ] Get user by ID
- [x] Get user by username
- [ ] Get account information
- [ ] Get Explore/Recommendations/Saved Streams/etc

## Download

`poetry add whatnot` *or* `pip install whatnot`

## Example

```python
import asyncio
from whatnot import Whatnot

async def main():
    whatnot = Whatnot()
    whatnot.login("bob@example.com", "secret_password")
    
    lives = whatnot.get_user_lives(whatnot.get_user_id("whatnot"))
    
    print(f"User has {len(lives)} upcoming/active lives!")
    
asyncio.run(main())
```

## Disclaimer

This project is unofficial and is not affiliated with or endorsed by Whatnot.
