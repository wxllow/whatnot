USER_QUERY = """
    id
    username
    userFollowing
    followerCount
    followingCount
    averageShipDays
    isVerifiedSeller
    canBeMessagedByMe
    profileImage {
        id
        bucket
        key
    }
    bio
    soldCount
    sellerRating {
        overall
        numReviews
    }
"""

LIVE_QUERY = (
    """
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
    user {"""
    + USER_QUERY
    + """
    }
    isUserBanned
    isUserModerator(userId: $userId)
    nominatedModerators {
        id
    }
    explicitContent
    isHiddenBySeller
    """
)
