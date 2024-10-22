import logging
import re

import google.generativeai as genai
from openai import OpenAI

from .config import settings
from .exceptions import ContentProcessingError
from .models import Content, ContentType

logger = logging.getLogger(__name__)


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


def get_system_prompt(content_type: ContentType) -> str:
    match content_type:
        case ContentType.PUBLICATION:
            return "You are an excellent academic paper reviewer. You conduct paper summarization on the full paper text provided by the user, with following instructions:\n\nREVIEW INSTRUCTION:\n\n**Summary of Academic Paper's Technical Approach**\n\n1. **Title and authors of the Paper:**\n   Provide the title and authors of the paper.\n\n2. **Main Goal and Fundamental Concept:**\n   Begin by clearly stating the primary objective of the research presented in the academic paper. Describe the core idea or hypothesis that underpins the study in simple, accessible language.\n\n3. **Technical Approach:**\n   Provide a detailed explanation of the methodology used in the research. Focus on describing how the study was conducted, including any specific techniques, models, or algorithms employed. Avoid delving into complex jargon or highly technical details that might obscure understanding.\n\n4. **Distinctive Features:**\n   Identify and elaborate on what sets this research apart from other studies in the same field. Highlight any novel techniques, unique applications, or innovative methodologies that contribute to its distinctiveness.\n\n5. **Experimental Setup and Results:**\n   Describe the experimental design and data collection process used in the study. Summarize the results obtained or key findings, emphasizing any significant outcomes or discoveries.\n\n6. **Advantages and Limitations:**\n   Concisely discuss the strengths of the proposed approach, including any benefits it offers over existing methods. Also, address its limitations or potential drawbacks, providing a balanced view of its efficacy and applicability.\n\n7. **Conclusion:**\n   Sum up the key points made about the paper's technical approach, its uniqueness, and its comparative advantages and limitations. Aim for clarity and succinctness in your summary.\n\nOUTPUT INSTRUCTIONS:\n\n1. Only use the headers provided in the instructions above.\n2. Format your output in clear, human-readable Markdown.\n3. Only output the prompt, and nothing else, since that prompt might be sent directly into an LLM.\n"
        case _:  # Default to empty string
            return "# IDENTITY and PURPOSE\n\nYou are an expert content summarizer. You take content in and output a Markdown formatted summary using the format below.\n\nTake a deep breath and think step by step about how to best accomplish this goal using the following steps.\n\n# OUTPUT SECTIONS\n\n- Combine all of your understanding of the content into a single, 20-word sentence in a section called ONE SENTENCE SUMMARY:.\n\n- Output the 10 most important points of the content as a list with no more than 15 words per point into a section called MAIN POINTS:.\n\n- Output a list of the 5 best takeaways from the content in a section called TAKEAWAYS:.\n\n# OUTPUT INSTRUCTIONS\n\n- Create the output using the formatting above.\n- You only output human readable Markdown.\n- Output numbered lists, not bullets.\n- Do not output warnings or notes—just the requested sections.\n- Do not repeat items in the output sections.\n- Do not start items with the same opening words."


def summarize_content_gemini(content: Content) -> str:
    logger.info("Summarizing content using Gemini")
    genai.configure(api_key=settings.GEMINI_API_KEY)

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,  # pyright: ignore
        system_instruction=get_system_prompt(content.content_type),
    )

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(content.raw_content)
    return response.text


def summarize_content_openai(content: Content) -> str:
    logger.info("Summarizing content using OpenAI")
    try:
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": get_system_prompt(content.content_type),
                },
                {  # pyright: ignore
                    "role": "user",
                    "content": content.raw_content,
                },
            ],
            temperature=1,
            max_tokens=1048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        summarized_content = response.choices[0].message.content
        if not summarized_content:
            raise ContentProcessingError("Failed to summarize content")
        return summarized_content
    except Exception as e:
        logger.exception(f"Error summarizing content: {e}")
        raise ContentProcessingError(f"Error summarizing content: {str(e)}")


async def summarize_content(content: Content) -> str:
    logger.info(f"Summarizing content: {content.url}")
    summary = ""
    try:
        # Try using Gemini first
        summary = summarize_content_gemini(content)
    except Exception as e:
        # Handle rate limit or other exceptions by falling back to OpenAI
        logger.info(f"Gemini failed with error: {e}. Falling back to OpenAI.")
        try:  # Try using OpenAI
            summary = summarize_content_openai(content)
        except Exception as e:
            logger.info(f"OpenAI failed with error: {e}.")
            logger.info("Both models failed. Returning the original markdown.")
            return ""

    # Clean and unwrap only the first code block
    summary = unwrap_first_codeblock(summary)
    logger.info(f"Content summarized: {summary[:100]}")
    return summary
