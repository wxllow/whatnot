import json
from functools import wraps
from typing import Any, Union
from uuid import uuid4
import time

import aiohttp
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from . import queries
from .exc import *
from .types import *
from .utils import *


# Authentication decorator
def login_required(func) -> callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        if not (self.access_data):
            raise AuthenticationRequired("Not logged in")

        return func(self, *args, **kwargs)

    return wrapper


class Whatnot:
    def __init__(self) -> None:
        HEADERS = {
            "Apollographql-Client-Name": "web",
            "Apollographql-Client-Version": "20230710-1529",
            "Origin": "https://www.whatnot.com",
            "Referer": "https://www.whatnot.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "X-Whatnot-App": "whatnot-web",
            "X-Whatnot-App-Version": "20230710-1529",
        }

        # GQL client
        self.transport = AIOHTTPTransport(
            url=gql_url,
            headers=HEADERS
        )
        
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=False,
        )

        # HTTP session
        self.session = aiohttp.ClientSession(
            headers=HEADERS,
        )

        self.access_data = None

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
        # --- NOT WORKING CURRENTLY ---
        # # If logged in, check if the access token is expired
        # if self.access_data:
        #     if self.access_data["access_token"]["expires_at"] <= time.time():
        #         # Refresh the access token
        #         async with aiohttp.ClientSession(
        #             headers=self.HEADERS,
        #             cookies={
        #                 "accessToken": self.access_data["access_token"]["token"],
        #                 "refreshToken": self.access_data["refresh_token"]["token"],
        #                 "accessTokenExpires": self.access_data["refresh_token"]["expires_at"],
        #             }
        #         ) as session:
        #             async with session.post(
        #                 f"{api_url}/refresh",
        #                 json={},
        #                 headers={
        #                     **session.headers,
        #                     "Authorization": f"Bearer {self.access_data['refresh_token']['token']}"
        #                 },
        #             ) as resp:
        #                 print(await resp.json())
        #                 resp.raise_for_status()
        #                 data = await resp.json()
        #                 await self.login_with_access_data(data)

        #     # Add the access token to the headers
        #     self.session.headers[
        #         "Authorization"
        #     ] = f"Bearer {self.access_data['access_token']['token']}"

        return await self.client.execute_async(
            gql(query), variable_values=variables
        )

    def __repr__(self) -> str:
        return f"<Whatnot user_id={self.access_data['user_id']!r})>"

    """Authentication"""

    async def login_with_access_data(self, access_data: dict) -> None:
        """Login using an access token"""
        # Add expires_at times if they don't exist
        if not access_data["access_token"].get("expires_at"):
            access_data["access_token"]["expires_at"] = (
                int(time.time()) + access_data["access_token"]["expires_in"] - 5
            )

        if not access_data["refresh_token"].get("expires_at"):
            access_data["refresh_token"]["expires_at"] = (
                int(time.time()) + access_data["refresh_token"]["expires_in"] - 5
            )

        self.access_data = access_data

    async def _verify(self, token: str, code: Union[str, int], device_id: str) -> None:
        """Handles email/SMS verification"""
        async with self.session.post(
            f"{api_url}/verify",
            json={
                "device_id": device_id,
                "code": code,
                "verification_token": token,
            },
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

            await self.login_with_access_data(data)

    async def login(
        self, username: str, password: str, interaction: bool = False
    ) -> None:
        """Log in using a email and password"""
        device_id = str(uuid4())

        async with self.session.post(
            f"{api_url}/login",
            json={
                "device_id": device_id,
                "email": username,
                "password": password,
                "app_type": "WEB_MOBILE",  # or WEB_DESKTOP
            },
        ) as resp:
            if resp.status == 400:
                raise AuthenticationError("Invalid email or password")

            resp.raise_for_status()

            data = await resp.json()

            verification_method = data.get("verification_method")

            if not verification_method:
                return await self.login_with_access_data(data)

            if verification_method in ("email", "sms"):
                type_ = {"email": "Email", "sms": "SMS"}[verification_method]

                if not interaction:
                    raise AuthenticationError(f"{type_} verification required")

                i = input(f"{type_} verification required. Enter code: ")
                await self._verify(data["verification_token"], i, device_id)
            else:
                raise NotImplementedError(
                    f"Unimplemented verification method: {data.get('verification_method')}"
                )

    async def load_session(self) -> None:
        """Load a saved session"""
        with open("session.json", "r") as f:
            data = json.load(f)

            await self.login_with_access_data(data)

    async def save_session(self) -> None:
        """Save the session to 2 files: session.json and cookie_jar.pickle"""
        with open("session.json", "w") as f:
            json.dump(self.access_data, f)

    """Account Info"""

    @login_required
    async def get_account_info(self) -> AccountInfo:
        """Get your account information"""
        # query = (
        #     """
        #         query UserInfo {
        #         """
        #     + queries.ME_QUERY
        #     + "}"
        # )

        query = "query UserInfo {\n  me {\n    id\n    bio\n    email\n    phoneNumber\n    firstName\n    lastName\n    displayName\n    canGoLive\n    salesTaxExempt\n    username\n    directMessagingDisabled\n    hasMarketplaceAccess\n    sellerProfileClipsHidden\n    sellerProfileVodsHidden\n    activityStatusEnabled\n    shippingLabelFormat\n    profileImage {\n      id\n      bucket\n      key\n      __typename\n    }\n    defaultCard {\n      customerReference\n      cardMetadata\n      __typename\n    }\n    defaultShippingAddress {\n      fullName\n      postalCode\n      line1\n      line2\n      city\n      state\n      countryCode\n      __typename\n    }\n    homeAddress {\n      fullName\n      postalCode\n      line1\n      line2\n      city\n      state\n      countryCode\n      __typename\n    }\n    walletEntries {\n      address\n      chainType\n      __typename\n    }\n    __typename\n  }\n}"

        print(
            await self._req(
                query,
                {



                },
            )
        )
        return (await self._req(query))["me"]

    @login_required
    async def get_default_payment(self) -> PaymentInfo:
        """Get your default payment information"""
        query = (
            """
                query GetPaymentInfo {
                """
            + queries.ME_PAYMENT_QUERY
            + "}"
        )

        resp = (await self._req(query))["userDefaultPayment"]

        return PaymentInfo(resp) if resp else None

    """Users"""

    async def get_user(self, username: str) -> User:
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
        return User(result) if result else None

    async def get_user_by_id(self, id_: str) -> User:
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
        return User(result) if result else None

    async def get_user_lives(self, user_id: str, first: int = 6) -> list[LiveStream]:
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

    async def get_live(self, id_: str) -> LiveStream:
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

        result = await self._req(query, {"id": id_})
        return LiveStream(result["liveStream"]) if result else None

    """Recommendations/Saved Streams/etcs"""
