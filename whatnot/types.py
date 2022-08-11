import json
from base64 import urlsafe_b64encode
from datetime import datetime, timezone
from typing import Optional

from .utils import LiveStatuses, images_url


class Base:
    def __init__(self, data: dict) -> None:
        self._from_data(data)

    def _from_data(self, data: dict):
        pass


class User(Base):
    def _from_data(self, data: dict) -> None:
        super()._from_data(data)
        self.id: str = data["id"]
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
