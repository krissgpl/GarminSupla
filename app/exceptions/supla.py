class SuplaClientError(Exception):
    """Base exception for SUPLA client."""


class TokenExchangeError(SuplaClientError):
    """Failed to exchange the authorization code for OAuth tokens."""


class RefreshTokenError(SuplaClientError):
    """Failed to refresh the OAuth access token."""


class UnauthorizedError(SuplaClientError):
    """SUPLA API returned an unauthorized response."""


class ApiError(SuplaClientError):
    """Unexpected response from the SUPLA API."""


class GateStateUnavailableError(SuplaClientError):
    """Gate state cannot be determined safely."""
