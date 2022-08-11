import json
from base64 import b64decode
from typing import Union

import aiohttp
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from . import queries
from .exc import *
from .types import *
from .utils import *


# Authentication decorator
def login_required(func) -> callable:
    def wrapper(self, *args, **kwargs) -> None:
        if not (self.access_token and self.user_id):
            raise AuthenticationError("Not logged in")

        func(self, *args, **kwargs)

    return wrapper


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

    async def __aenter__(self) -> "Whatnot":
        """Enter the context manager"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the session"""
        await self.session.close()

    async def _req(self, query: str, variables: Optional[dict] = None) -> dict:
        """Make a request to the GraphQL endpoint"""
        return await self.client.execute_async(gql(query), variable_values=variables)

    def __repr__(self) -> str:
        return f"<Whatnot user_id={self.user_id!r})>"

    """Authentication"""

    async def login_with_access_token(self, access_token: str, user_id: str) -> None:
        """Login using an access token"""
        self.access_token = access_token
        self.user_id = user_id
        self.transport.headers = {"Authorization": f"Bearer {self.access_token}"}

    async def _verify_email(self, token: str, code: Union[str, int]) -> None:
        """Handles email verification"""
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

            await self.login_with_access_token(data["access_token"], data["user_id"])

    async def login(
        self, username: str, password: str, interaction: bool = False
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

            verification_method = data.get("verification_method")

            if not verification_method:
                return await self.login_with_access_token(
                    data["access_token"], data["user_id"]
                )

            if verification_method == "email":
                if not interaction:
                    raise AuthenticationError("Email verification required")

                i = input("Email verification required. Enter code: ")

                await self._verify_email(data["verification_token"], i)
            else:
                raise NotImplementedError(
                    f"Unimplemented verification method: {data.get('verification_method')}"
                )

    async def load_session(self) -> None:
        """Load a saved session"""
        with open("session.json", "r") as f:
            data = json.load(f)

            self.access_token = data["access_token"]
            self.user_id = data["user_id"]

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

    """Account Info"""

    @login_required
    async def me(self) -> dict:
        pass

    """Users"""

    async def get_user_id(self, username: str) -> dict:
        """Get a user's id by their username (requires beautifulsoup4)"""
        return (await self.get_user(username)).id

    async def get_user(self, username: str) -> dict:
        """Get a user by their username"""
        query = (
            """
                query GetUser($username: String) {
                    getUser(username: $username) {
                """
            + queries.USER_QUERY
            + "}}"
        )

        result = (await self._req(query, {"username": username}))["getUser"]
        result.update({"id": b64decode(result["id"]).decode("utf-8").split(":", 1)[1]})
        return User(result)

    async def get_user_by_id(self, id_: str) -> dict:
        """Get a user by their id"""
        query = (
            """
            query GetUser($id: ID) {
                getUser(id: $id) {
            """
            + queries.USER_QUERY
            + "}}"
        )

        result = (await self._req(query, {"id": id_}))["getUser"]
        result.update({"id": b64decode(result["id"]).decode("utf-8").split(":", 1)[1]})
        return User(result)

    async def get_user_lives(self, user_id: str, first: int = 6) -> list:
        """Get a user's lives by their id"""
        query = (
            """
            query GetUserLiveStreams($userId: ID!, $first: Int) {
                searchLivestreams(userIds: [$userId], first: $first) {
                    edges {
                        node {
                            ... on LiveStream {"""
            + queries.LIVE_QUERY
            + "}}}}}"
        )

        result = await self._req(query, {"first": first, "userId": user_id})
        return [LiveStream(i["node"]) for i in result["searchLivestreams"]["edges"]]

    """Lives"""

    async def get_live(self, id_: str) -> dict:
        """Get a livestream by ID"""
        query = (
            """
            query GetLivestreamContext($id: ID!, $userId: ID) {
                liveStream(id: $id) {
                    ...LivestreamFragment
                }
            }

            fragment LivestreamFragment on LiveStream {"""
            + queries.LIVE_QUERY
            + "}"
        )

        result = await self._req(query, {"id": id_, "userId": self.user_id})
        return LiveStream(result["liveStream"])

    """Recommendations/Saved Streams/etcs"""
