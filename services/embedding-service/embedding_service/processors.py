import logging
from typing import Any, Dict, Tuple

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import ValidationError

from .config import settings
from .models import Content

logger = logging.getLogger(__name__)


class ContentProcessingError(Exception):
    pass


async def embedding_content(content: Content) -> None:
    logger.info(f"Summarizing content: {content.url}")
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        raw_content = content.raw_content
        summary = content.summary

        content_document = Document(
            page_content=raw_content,
            metadata={"source": content.url, "content_id": content.content_id},
        )
        summary_document = Document(
            page_content=summary,
            metadata={"source": content.url, "content_id": content.content_id},
        )

        docs = [content_document, summary_document]

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)

        # See docker command above to launch a postgres instance with pgvector enabled.
        connection = settings.VECTOR_DB_URL
        logger.info(f"Connecting to postgres: {connection}")
        collection_name = "my_collection"

        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection,
            use_jsonb=True,
        )

        vector_store.add_documents(documents=splits)

    except Exception as e:
        logger.exception(f"Error embedding_content: {e}")
        raise ContentProcessingError(f"Error embedding content: {str(e)}")


async def process_content(content: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    url = content.get("url")
    logger.info(f"Starting content processing: {url}")
    try:
        validated_content = Content.model_validate(content)
        await embedding_content(validated_content)

        logger.info("Content embeddings completely.")

        return "", validated_content.model_dump()

    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")

    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
