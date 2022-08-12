import json
from base64 import urlsafe_b64encode
from datetime import datetime, timezone
from typing import Optional

from .utils import LiveStatuses, decode_id, images_url


class Base:
    def __init__(self, data: dict) -> None:
        self._from_data(data)

    def _from_data(self, data: dict):
        pass


class Address(Base):
    def _from_data(self, data: dict) -> None:
        super()._from_data(data)

        self.city: str = data["city"]
        self.full_name: str = data["fullName"]
        self.line1: str = data["line1"]
        self.line2: str = data["line2"]
        self.postal_code: str = data["postalCode"]
        self.state: str = data["state"]

    def __repr__(self) -> str:
        return f"<Address {self.postal_code}>"


class AccountInfo(Base):
    def _from_data(self, data: dict) -> None:
        super()._from_data(data)

        self.bio: Optional[str] = data["bio"]
        self.can_go_live: bool = data["canGoLive"]
        self.default_card: Optional[dict] = data["defaultCard"]
        self.default_shipping_address: Optional[Address] = (
            Address(data["defaultShippingAddress"])
            if data["defaultShippingAddress"]
            else None
        )
        self.direct_messaging_disabled: bool = data["directMessagingDisabled"]
        self.email: str = data["email"]
        self.first_name: str = data["firstName"]
        self.home_address: Optional[dict] = data["homeAddress"]
        self.id: str = decode_id(data["id"])
        self.last_name: str = data["lastName"]
        self.sales_tax_exempt: bool = data["salesTaxExempt"]
        self.seller_approved: bool = data["sellerApproved"]
        self.shipping_label_format: str = data["shippingLabelFormat"]
        self.username: str = data["username"]
        self.wallet_entries: list = data["walletEntries"]

    def __repr__(self) -> str:
        return f"<AccountInfo>"


def card_metadata_string_bool(i: str) -> Optional[bool]:
    return True if i == "Yes" else False if i == "Unknown" else False


class CardMetadata(Base):
    def _from_data(self, data: dict) -> None:
        super()._from_data(data)
        self.bin: str = data["bin"]
        self.card_type: str = data["card_type"]
        self.cardholder_name: Optional[str] = data["cardholder_name"]
        self.created_at: datetime = datetime.strptime(
            data["updated_at"], "%Y-%m-%d %H:%M:%S"
        )
        self.customer_id: str = data["customer_id"]
        self.customer_global_id: str = data["customer_global_id"]
        self.default: bool = data["default"]
        self.expiration_month: str = data["expiration_month"]
        self.expiration_year: str = data["expiration_year"]
        self.expired: bool = data["expired"]
        self.global_id: str = data["global_id"]
        self.graphql_id: str = data["graphql_id"]
        self.image_url: str = data["image_url"]
        self.last_4: str = data["last_4"]
        self.payment_instrument_name: str = data["payment_instrument_name"]
        self.source_description: str = data["source_description"]
        self.subscriptions: list = data["subscriptions"]
        self.token: str = data["token"]
        self.updated_at: datetime = datetime.strptime(
            data["updated_at"], "%Y-%m-%d %H:%M:%S"
        )
        self.commercial: str = data["commercial"]
        self.debit: bool = card_metadata_string_bool(data["debit"])
        self.durbin_regulated: bool = card_metadata_string_bool(
            data["durbin_regulated"]
        )
        self.healthcare: bool = card_metadata_string_bool(data["healthcare"])
        self.payroll: bool = card_metadata_string_bool(data["payroll"])
        self.prepaid: bool = card_metadata_string_bool(data["prepaid"])
        self.product_id: str = data["product_id"]
        self.country_of_issuance: str = data["country_of_issuance"]
        self.issuing_bank: str = data["issuing_bank"]
        self.gateway: Optional[str] = data["gateway"]
        self.is_expired: bool = data["is_expired"]

    def __repr__(self) -> str:
        return f"<CardMetadata>"


class PaymentInfo(Base):
    def _from_data(self, data: dict) -> None:
        super()._from_data(data)
        self.billing_address: Optional[dict] = (
            Address(data["billingAddress"]) if data["billingAddress"] else None
        )
        self.card_description: str = data["cardDescription"]
        self.card_metadata: dict = CardMetadata(json.loads(data["cardMetadata"]))
        self.card_reference: str = data["cardReference"]
        self.card_type: str = data["cardType"]
        self.created_at: datetime = datetime.strptime(
            data["createdAt"], "%a, %d %b %Y %H:%M:%S %Z"
        )
        self.customer_reference: str = data["customerReference"]
        self.gateway: str = data["gateway"]

    def __repr__(self) -> str:
        return f"<PaymentInfo>"


class User(Base):
    def _from_data(self, data: dict) -> None:
        super()._from_data(data)
        self.id: str = decode_id(data["id"])
        self.username: str = data["username"]
        self.follower_count: str = data["followerCount"]
        self.is_verified_seller: bool = data["isVerifiedSeller"]
        self.profile_image: dict = data[
            "profileImage"
        ]  # Todo: auto-convert this to a URL
        self.profile_url: str = f"{images_url}/{urlsafe_b64encode(json.dumps(self.profile_image).encode('utf-8')).decode('utf-8')}"
        self.seller_rating: dict = data["sellerRating"]
        self.user_following: bool = data["userFollowing"]
        self.average_ship_days: Optional[int] = data["averageShipDays"]
        self.bio: Optional[str] = data["bio"]
        self.can_be_messaged_by_me: bool = data["canBeMessagedByMe"]
        self.following_count: int = data["followingCount"]
        self.sold_count: int = data["soldCount"]

    def __repr__(self) -> str:
        return f"<User {self.username!r}>"


class CategoryNode(Base):
    def _from_data(self, data: dict) -> None:
        self.id: str = data["id"]
        self.label: str = data["label"]

    def __repr__(self) -> str:
        return f"<CategoryNode {self.label!r}>"


class LiveStream(Base):
    def _from_data(self, data: dict) -> None:
        self.active_viewers: int = data["activeViewers"]
        self.categories: list = data["categories"]
        self.category_nodes: list = [
            CategoryNode(data=i) for i in data["categoryNodes"]
        ]
        self.explicit_content: bool = data["explicitContent"]
        self.id: str = data["id"]
        self.is_hidden_by_seller: bool = data["isHiddenBySeller"]
        self.is_seller_international_to_buyer: bool = data[
            "isSellerInternationalToBuyer"
        ]
        self.is_user_banned: bool = data["isUserBanned"]
        self.is_user_moderator: bool = data["isUserModerator"]
        self.nominatedModerators: list = [i["id"] for i in data["nominatedModerators"]]
        self.pinned_product_id: Optional[str] = data["pinnedProductId"]
        self.start_time: datetime = datetime.fromtimestamp(
            int(data["startTime"]) / 1000, tz=timezone.utc
        )
        self.status = LiveStatuses(data["status"])
        self.stream_token: str = data["streamToken"]
        self.title: str = data["title"]
        self.total_watchlist_users: int = data["totalWatchlistUsers"]
        self.trailer_thumbnail_url: Optional[str] = data["trailerThumbnailUrl"]
        self.trailer_url: Optional[str] = data["trailerUrl"]
        self.user: dict = User(data["user"])

    def __repr__(self) -> str:
        return f"<LiveStream id={self.id!r} title={self.title!r}>"
