import pytest
from pydantic import ValidationError
from common_lib.models import ContentSubmission, ClassifiedContent, ContentType


def test_content_submission_valid():
    submission = ContentSubmission(content="https://example.com")
    assert submission.content == "https://example.com"


def test_content_submission_invalid():
    with pytest.raises(ValidationError):
        ContentSubmission(content="")  # Empty string should be invalid


def test_content_classification():
    classification = ClassifiedContent(
        content_type=ContentType.WEB_ARTICLE, url="https://example.com"
    )
    assert classification.content_type == ContentType.WEB_ARTICLE
    assert classification.url == "https://example.com"
