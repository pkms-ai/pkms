import pytest
from content_submission_service.classifier import classify_content
from common_lib.models import ContentType


@pytest.mark.integration
def test_classify_content_web_article():
    result = classify_content("https://www.bbc.com/news/article-12345")
    assert result.content_type == ContentType.WEB_ARTICLE


@pytest.mark.integration
def test_classify_content_youtube():
    result = classify_content("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert result.content_type == ContentType.YOUTUBE_VIDEO


@pytest.mark.integration
def test_classify_content_unknown():
    result = classify_content("This is just some random text")
    assert result.content_type == ContentType.UNKNOWN
