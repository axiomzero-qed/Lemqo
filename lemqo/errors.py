"""Expected input and verification failures; none represent acceptance."""


class Rejection(ValueError):
    """A certificate, claim, or resource-policy violation."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)
