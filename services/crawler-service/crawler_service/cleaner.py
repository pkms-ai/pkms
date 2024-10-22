import logging
import re

import google.generativeai as genai
from openai import OpenAI

from .config import settings

logger = logging.getLogger(__name__)

system_prompt = "You are a professional in web scraping and cleaning markdown. You excel at identifying irrelevant elements and extracting the core content cleanly.\n\nClean the provided markdown content from a website by removing irrelevant elements such as navigation and headers while maintaining the main content, language, images, and links. Ensure that the output is in markdown format only.\n\n# Steps\n\n1. **Identify Main Content**: Locate the sections of the markdown that correspond to the primary content based on context and relevance.\n2. **Remove Irrelevant Sections**: Identify and eliminate any markdown portions related to navigation, headers, footers, or any non-essential sections that do not contribute to the main content.\n3. **Preserve Language and Images**: Ensure that the main textual content remains intact, preserving the original language and all image references.\n4. **Perform Quality Check**: Review the cleaned markdown to ensure that only relevant content is maintained, and the markdown format is correctly preserved.\n\n# Output Format\n\n- The output should be pure markdown format.\n- Only relevant main content, language, and images should be included.\n- Ensure there is no extraneous or irrelevant information in the output.\n\n# Notes\n\n- Pay careful attention to sections of the markdown that are structured as navigation, headers, or footers to ensure they are removed.\n- Maintain any links or references integral to the main content.\n- Images should remain in their original markdown format with accurate alt text.\n"


def unwrap_first_codeblock(response_text: str) -> str:
    """
    Cleans and unwraps the first code block by removing the first occurrence of code block delimiters.
    """
    # Replace the first code block using `re.subn` which allows limiting replacements
    cleaned_text, num_subs = re.subn(
        r"```.*?```", "", response_text, count=1, flags=re.DOTALL
    )

    if num_subs == 0:
        # If no code block found, return the original text
        return response_text

    # Strip extra whitespace or newlines
    cleaned_text = cleaned_text.strip()

    return cleaned_text


def clean_markdown_gemini(markdown) -> str:
    logger.info("Cleaning markdown content using Gemini.")
    genai.configure(api_key=settings.GEMINI_API_KEY)

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8010,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-002",
        generation_config=generation_config,  # pyright: ignore
        system_instruction=system_prompt,
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(markdown)

    return response.text


def clean_markdown_openai(markdown) -> str:
    logger.info("Cleaning markdown content using OpenAI.")
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use your desired OpenAI model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": markdown},
        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )

    return response.choices[0].message.content or ""


async def clean_markdown(markdown: str) -> str:
    logger.info("Cleaning markdown content.")
    cleaned_markdown = ""
    try:
        # Try using Gemini first
        cleaned_markdown = clean_markdown_gemini(markdown)
    except Exception as e:
        # Handle rate limit or other exceptions by falling back to OpenAI
        logger.info(f"Gemini failed with error: {e}. Falling back to OpenAI.")
        try:  # Try using OpenAI
            cleaned_markdown = clean_markdown_openai(markdown)
        except Exception as e:
            logger.info(f"OpenAI failed with error: {e}.")
            logger.info("Both models failed. Returning the original markdown.")
            return markdown
    # Clean and unwrap only the first code block
    cleaned_markdown = unwrap_first_codeblock(cleaned_markdown)
    logger.info("Markdown cleaning complete.")
    return cleaned_markdown
