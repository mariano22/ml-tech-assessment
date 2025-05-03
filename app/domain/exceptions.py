"""Custom domain-level exceptions for error handling across layers."""


class EmptyTranscriptError(ValueError):
    """Raised when the provided transcript is empty or whitespace-only."""


class TranscriptNotFoundError(ValueError):
    """Raised when a transcript analysis cannot be found in the repository."""


class InvalidBatchError(ValueError):
    """Raised when a batch request payload is invalid (empty list or invalid items).""" 