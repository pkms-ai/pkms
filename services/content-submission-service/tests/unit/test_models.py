import pytest
from pydantic import ValidationError
from content_submission_service.models import (
    ContentSubmission,
)


def test_content_submission_valid():
    submission = ContentSubmission(content="https://example.com", source=None)
    assert submission.content == "https://example.com"


def test_content_submission_invalid():
    with pytest.raises(ValidationError):
        ContentSubmission(content="", source=None)  # Empty string should be invalid
