import logging

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter


from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content


logger = logging.getLogger(__name__)


async def embedding_content(content: Content) -> None:
    logger.info(f"Summarizing content: {content.url}")
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        raw_content = content.raw_content
        summary = content.summary

        if not raw_content:
            logger.error("Content is empty, skipping embedding")
            raise ContentProcessingError("Content is empty, skipping embedding")

        content_document = Document(
            page_content=raw_content,
            metadata={"source": content.url, "content_id": content.content_id},
        )

        summary_document = (
            Document(
                page_content=summary,
                metadata={"source": content.url, "content_id": content.content_id},
            )
            if summary
            else None
        )

        docs = [content_document, summary_document] if summary else [content_document]

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)

        # See docker command above to launch a postgres instance with pgvector enabled.
        connection = settings.VECTOR_DB_URL
        logger.info(f"Connecting to postgres: {connection}")
        collection_name = settings.COLLECTION_NAME

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
