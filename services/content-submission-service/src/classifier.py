from openai import OpenAI
from models import ContentClassification
from config import settings


def classify_content(input_text: str) -> ContentClassification:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    

    prompt = """
    Classify the given content as WEB_ARTICLE, YOUTUBE_VIDEO, or BOOKMARK based on its type.

- Determine whether the content is text or a URL.
- If it's a URL, identify if it links to a web article, a YouTube video, or consider it a general bookmark if it doesn't fit the other categories.
- If the content is text, classify it as WEB_ARTICLE.

# Output Format

Provide the classification result as a single word: WEB_ARTICLE, YOUTUBE_VIDEO, or BOOKMARK.

# Examples

**Example 1:**

Input: "https://example.com/article"
Output: "WEB_ARTICLE"

**Example 2:**

Input: "https://youtube.com/watch?v=dQw4w9WgXcQ"
Output: "YOUTUBE_VIDEO"

**Example 3:**

Input: "Here is some text content that should be classified."
Output: "WEB_ARTICLE"

# Notes

- If the URL is unclear whether it's a web article or a general website bookmark, default to BOOKMARK unless clear evidence suggests otherwise.
"""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text},
        ],
        response_format=ContentClassification,
    )

    print(completion)
    print(completion.choices[0].message.content)

    classified_content = completion.choices[0].message.parsed

    return classified_content