import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socket

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

def start():
    env = settings.ENVIRONMENT or "development"
    host = "0.0.0.0"
    port = settings.PORT or 8000

    print(f"CORS origins: {settings.cors_origins}")  # Debug print

    try:
        if env == "development":
            uvicorn.run("src.main:app", host=host, port=port, reload=True)
        else:
            uvicorn.run("src.main:app", host=host, port=port)
    except Exception as e:
        print(f"Error starting the server: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    start()
