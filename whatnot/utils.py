from enum import Enum

base_url = "https://www.whatnot.com"
api_url = "https://api.whatnot.com/api"
gql_url = "https://api.whatnot.com/graphql"
images_url = "https://images.whatnot.com"
login_url = f"{api_url}/login"


class LiveStatuses(Enum):
    CREATED = "CREATED"
    LIVE = "PLAYING"
    ENDED = "ENDED"
