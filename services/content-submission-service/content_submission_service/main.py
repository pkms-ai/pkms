import logging
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import router

app = FastAPI(title="Content Submission Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# def start():
#     env = settings.ENVIRONMENT
#     host = "0.0.0.0"
#     port = settings.PORT
#
#     logger.info(f"Starting server in {env} mode")
#     logger.info(f"CORS origins: {settings.cors_origins}")
#
#     try:
#         if env == "development":
#             uvicorn.run(
#                 "content_submission_service.main:app", host=host, port=port, reload=True
#             )
#         else:
#             uvicorn.run("content_submission_service.main:app", host=host, port=port)
#     except Exception as e:
#         logger.error(f"Error starting the server: {e}")
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     start()
