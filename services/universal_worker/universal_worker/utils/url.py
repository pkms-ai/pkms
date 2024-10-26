import requests
import logging

from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

logger = logging.getLogger(__name__)


def clean_url(original_url) -> Optional[str]:
    try:
        # Step 1: Unshorten URL by following redirects
        response = requests.get(original_url, allow_redirects=True, timeout=10)
        resolved_url = response.url

        # Step 2: Parse the URL
        parsed_url = urlparse(resolved_url)

        # Step 3: Remove query parameters that often don't affect uniqueness
        filtered_query = {
            k: v
            for k, v in parse_qs(parsed_url.query).items()
            if k not in ["utm_source", "utm_medium", "utm_campaign", "ref"]
        }

        # Step 4: Normalize URL by stripping fragments and rebuilding
        normalized_url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc.lower(),  # Convert domain to lowercase
                parsed_url.path.rstrip("/"),  # Remove trailing slash
                parsed_url.params,
                urlencode(filtered_query, doseq=True),  # Rebuild query string
                "",  # Drop fragment
            )
        )

        return normalized_url

    except requests.RequestException as e:
        logger.info(f"Error resolving URL: {e}")
        return None
