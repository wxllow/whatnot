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

ME_QUERY = """
me {
    id
    bio
    email
    firstName
    lastName
    sellerApproved
    canGoLive
    salesTaxExempt
    username
    directMessagingDisabled
    shippingLabelFormat
    defaultCard {
      customerReference
      cardMetadata
    }
    defaultShippingAddress {
      fullName
      postalCode
      line1
      line2
      city
      state
    }
    homeAddress {
      fullName
      postalCode
      line1
      line2
      city
      state
    }
    walletEntries {
        address
        chainType
    }
}
"""

ME_PAYMENT_QUERY = """
userDefaultPayment {
    customerReference
    cardMetadata
    cardReference
    billingAddress {
        postalCode
        line1
        line2
        city
        state
    }
    cardDescription
    cardType
    createdAt
    gateway
}
"""
