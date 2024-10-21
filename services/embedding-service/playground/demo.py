from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# read from a file

content = open("playground/content.md").read()
summary = "This is a summary of the content"

content_document = Document(
    page_content=content, metadata={"source": "https://example.com"}
)
summary_document = Document(
    page_content=content, metadata={"source": "https://example.com"}
)

docs = [content_document, summary_document]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)


# See docker command above to launch a postgres instance with pgvector enabled.
connection = "postgresql+psycopg://vector_user:vector_pass@localhost:6024/pkms_vector"  # Uses psycopg3!
collection_name = "my_collection"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

vector_store.add_documents(documents=splits)
