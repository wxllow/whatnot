from typing import Union
import logging
import json

import aiohttp
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from .utils import *
from .exceptions import *
from .types import *


try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    logging.warn(
        "Optional dependency beautifulsoup4 is not available, some functionality will be unavailable."
    )
    HAS_BS4 = False


class Whatnot:
    def __init__(self) -> None:
        # GQL client
        self.transport = AIOHTTPTransport(url=gql_url)
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=False,
        )

        # HTTP session
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
            }
        )

        self.access_token = None
        self.user_id = None

    # Authentication
    async def _verify_email(self, token: str, code: Union[str, int]) -> None:
        async with self.session.post(
            f"{api_url}/verify",
            json={
                # wants device_id too
                "code": code,
                "verification_token": token,
            },
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

            self.access_token = data["access_token"]
            self.user_id = data["user_id"]

            self.transport.headers = {"Authorization": f"Bearer {self.access_token}"}

    async def login(
        self, username: str, password: str, interaction: bool = True
    ) -> None:
        """Log in using a email and password"""
        async with self.session.post(
            f"{api_url}/login",
            json={
                # "device_id": "aea87c97-aaba-4426-ae44-d3db92e188d9", # Don't know what this is exactly, but the API doesn't seem to care
                "username": username,
                "password": password,
            },
        ) as resp:
            if resp.status == 400:
                raise AuthenticationError("Invalid email or password")

            resp.raise_for_status()

            data = await resp.json()

            if data.get("verification_method") == "email":
                if interaction:
                    i = input("Email verification required. Enter code: ")

                    await self._verify_email(data["verification_token"], i)
                else:
                    raise AuthenticationError("Email verification required")
            else:
                raise NotImplementedError("Unimplemented verification method:")

    async def load_session(self) -> None:
        """Load a saved session"""
        with open("session.json", "r") as f:
            data = json.load(f)

            self.access_token = data["access_token"]
            self.user_id = data["user_id"]

        self.session.cookie_jar.load("cookie_jar.pickle")

        self.transport.headers = {"Authorization": f"Bearer {self.access_token}"}

    async def save_session(self) -> None:
        """Save the session to 2 files: session.json and cookie_jar.pickle"""
        with open("session.json", "w") as f:
            json.dump(
                {
                    "access_token": self.access_token,
                    "user_id": self.user_id,
                },
                f,
            )

        self.session.cookie_jar.save("cookie_jar.pickle")

    """Account Info"""

    """Users"""

    async def get_user_id(self, username: str) -> dict:
        """Get a user's id by their username (requires beautifulsoup4)"""
        if not HAS_BS4:
            raise ImportError("beautifulsoup4 not available")

        url = f"{base_url}/user/{username}"

        async with self.session.get(url) as resp:
            resp.raise_for_status()

            soup = BeautifulSoup(await resp.text(), "html.parser")

        head = soup.find("head")
        script = soup.find_all("script")[2].text
        loc = script.find('"key":"users/')

        if loc == -1:
            raise KeyError("Cannot find ID from username!")

        return script[loc:].split("/")[1]

    # async def get_user(self, user_id: str) -> dict:
    #     pass

    async def get_user_lives(self, user_id: str, first: int = 6) -> list:
        """Get a user's lives by their id"""
        query = gql(
            """
            query GetUserLiveStreams($userId: ID!, $first: Int) {
                searchLivestreams(userIds: [$userId], first: $first) {
                    edges {
                        node {
                            ... on LiveStream {
                                id
                                status
                                trailerUrl
                                trailerThumbnailUrl
                                title
                                startTime
                                categories
                                categoryNodes {
                                    id
                                    label
                                }
                            }
                        }
                    }
                }
            }
            """
        )

        result = await self.client.execute_async(
            query,
            variable_values={"first": first, "userId": user_id},
        )

        return [UserLiveStream(i["node"]) for i in result["searchLivestreams"]["edges"]]

    """Lives"""

    async def get_live(self, id_: str) -> dict:
        """Get a livestream by ID"""
        query = gql(
            """
            query GetLivestreamContext($id: ID!, $userId: ID) {
                liveStream(id: $id) {
                    ...LivestreamFragment
                }
            }

            fragment LivestreamFragment on LiveStream {
                id
                status
                trailerUrl
                trailerThumbnailUrl
                title
                startTime
                pinnedProductId
                activeViewers
                categories
                categoryNodes {
                    id
                    label
                }
                totalWatchlistUsers
                isSellerInternationalToBuyer
                streamToken
                user {
                    id
                    username
                    followerCount
                    userFollowing
                    profileImage {
                        id
                        bucket
                        key
                    }
                    isVerifiedSeller
                    sellerRating {
                        overall
                        numReviews
                    }
                }
                isUserBanned
                isUserModerator(userId: $userId)
                nominatedModerators {
                    id
                }
                explicitContent
                isHiddenBySeller
            }
            """
        )

        result = await self.client.execute_async(
            query,
            variable_values={"id": id_, "userId": self.user_id},
        )

        return LiveStream(result["liveStream"])

    """Recommendations/Saved Streams/etcs"""
