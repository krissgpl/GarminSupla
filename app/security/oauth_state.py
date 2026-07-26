import secrets


class OAuthState:
    """Manages OAuth state used for CSRF protection."""

    def __init__(self) -> None:
        self._state: str | None = None

    def generate(self) -> str:
        """Generate and store a new OAuth state."""

        self._state = secrets.token_urlsafe(32)
        return self._state

    def validate(self, state: str) -> bool:
        """Validate and consume the OAuth state."""

        if (
            self._state is None
            or not secrets.compare_digest(self._state, state)
        ):
            return False

        self.clear()
        return True

    def clear(self) -> None:
        """Clear the stored OAuth state."""

        self._state = None


oauth_state = OAuthState()
