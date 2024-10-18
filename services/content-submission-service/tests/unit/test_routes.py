import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from content_submission_service.main import app
from content_submission_service.models import ContentType, ContentClassification

client = TestClient(app)

@pytest.mark.asyncio
@patch('content_submission_service.routes.classify_content')
@patch('content_submission_service.routes.publish_to_queue')
async def test_submit_content(mock_publish, mock_classify):
    # Mock the classify_content function
    mock_classify.return_value = ContentClassification(content_type=ContentType.WEB_ARTICLE, url="https://example.com")

    # Mock the publish_to_queue function
    mock_publish.return_value = None

    response = client.post("/submit", json={"content": "https://example.com"})
    
    # Print response for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    
    # Check if mocks were called
    print(f"classify_content called: {mock_classify.called}")
    print(f"publish_to_queue called: {mock_publish.called}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.content}"
    assert "message" in response.json()
    assert "status" in response.json()
    assert "content_type" in response.json()
    assert response.json()["content_type"] == ContentType.WEB_ARTICLE.value

    # Verify that classify_content and publish_to_queue were called
    mock_classify.assert_called_once_with("https://example.com")
    mock_publish.assert_called_once()

@pytest.mark.asyncio
@patch('content_submission_service.routes.classify_content')
@patch('content_submission_service.routes.publish_to_queue')
async def test_submit_content_unknown(mock_publish, mock_classify):
    # Mock classify_content to return UNKNOWN
    mock_classify.return_value = ContentClassification(content_type=ContentType.UNKNOWN)

    response = client.post("/submit", json={"content": "some random text"})
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Failed to classify the content"

    # Verify that classify_content was called but publish_to_queue was not
    mock_classify.assert_called_once_with("some random text")
    mock_publish.assert_not_called()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
