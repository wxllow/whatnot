from datetime import datetime
from .utils import LiveStatuses


class Base:
    def __init__(self, data: dict) -> None:
        self._from_data(data)

    def _from_data(self, data: dict):
        pass


class BaseUser(Base):
    def _from_data(self, data: dict) -> None:
        self.id: str = data["id"]
        self.username: str = data["username"]
        self.follower_count: str = data["followerCount"]
        self.is_verified_seller: bool = data["isVerifiedSeller"]
        self.profile_image: dict = data[
            "profileImage"
        ]  # Todo: auto-convert this to a URL
        self.seller_rating: dict = data["sellerRating"]
        self.user_following: bool = data["userFollowing"]


class CategoryNode(Base):
    def _from_data(self, data: dict) -> None:
        self.id: str = data["id"]
        self.label: str = data["label"]


class BaseLiveStream(Base):
    def _from_data(self, data: dict):
        self.categories: list = data["categories"]
        self.category_nodes: list = [
            CategoryNode(data=i) for i in data["categoryNodes"]
        ]
        self.id: str = data["id"]
        self.title: str = data["title"]
        self.status = LiveStatuses(data["status"])
        self.start_time: datetime = datetime.fromtimestamp(
            int(data["startTime"]) / 1000
        )
        self.trailerUrl: str | None = data["trailerUrl"]
        self.trailerThumbnailUrl: str | None = data["trailerThumbnailUrl"]

    def __repr__(self) -> str:
        return f"<BaseLiveStream id={self.id!r} title={self.title!r}>"


class UserLiveStream(BaseLiveStream):
    def __repr__(self) -> str:
        return f"<UserLiveStream id={self.id!r} title={self.title!r}>"


class LiveStream(BaseLiveStream):
    def _from_data(self, data: dict) -> None:
        super()._from_data(data)
        self.active_viewers: int = data["activeViewers"]
        self.explicit_content: bool = data["explicitContent"]
        self.is_hidden_by_seller: bool = data["isHiddenBySeller"]
        self.is_seller_international_to_buyer: bool = data[
            "isSellerInternationalToBuyer"
        ]
        self.is_user_banned: bool = data["isUserBanned"]
        self.is_user_moderator: bool = data["isUserModerator"]
        self.nominatedModerators: list = [i["id"] for i in data["nominatedModerators"]]
        self.pinned_product_id: str | None = data["pinnedProductId"]
        self.stream_token: str = data["streamToken"]
        self.total_watchlist_users: int = data["totalWatchlistUsers"]
        self.user: dict = BaseUser(data["user"])

    def __repr__(self) -> str:
        return f"<LiveStream id={self.id!r} title={self.title!r}>"
