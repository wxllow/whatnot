from enum import Enum


base_url = "https://www.whatnot.com"

api_url = "https://api.whatnot.com/api"
gql_url = "https://api.whatnot.com/graphql"
login_url = f"{api_url}/login"


class LiveStatuses(Enum):
    CREATED = "CREATED"
    LIVE = "PLAYING"
    ENDED = "ENDED"
