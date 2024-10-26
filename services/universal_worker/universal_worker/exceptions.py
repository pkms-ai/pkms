class ContentProcessingError(Exception):
    pass


class ContentAlreadyExistsError(Exception):
    """Custom exception for content that already exists in the database."""

    pass
