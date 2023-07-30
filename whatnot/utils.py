from base64 import b64decode
from enum import Enum

base_url = "https://www.whatnot.com"
api_url = "https://api.whatnot.com/api/v2"
gql_url = "https://api.whatnot.com/graphql/"
images_url = "https://images.whatnot.com"
login_url = f"{api_url}/login"


class LiveStatuses(Enum):
    CREATED = "CREATED"
    LIVE = "PLAYING"
    ENDED = "ENDED"


def decode_id(id_: str) -> int:
    if id_.isdigit():
        return id_

    return b64decode(id_).decode("utf-8").split(":", 1)[1]
