import logging
from typing import Dict

from workflow_base import ProcessorConfig, WorkflowConfigBase

from .processors import (
    ClassifierProcessor,
    CrawlerProcessor,
    EmbeddingProcessor,
    NotifierProcessor,
    SummarizerProcessor,
    TranscriberProcessor,
)

logger = logging.getLogger(__name__)


class WorkflowConfig(WorkflowConfigBase):
    CLASSIFY_QUEUE: str = "classify_queue"
    TRANSCRIBE_QUEUE: str = "transcribe_queue"
    CRAWL_QUEUE: str = "crawl_queue"
    SUMMARY_QUEUE: str = "summary_queue"
    ERROR_QUEUE: str = "error_queue"
    EMBEDDING_QUEUE: str = "embedding_queue"
    NOTIFY_QUEUE: str = "notify_queue"

    @property
    def processors(self) -> Dict[str, ProcessorConfig]:
        return {
            "classifier": ProcessorConfig(
                name="classifier",
                input_queue=self.CLASSIFY_QUEUE,
                output_queues=[self.CRAWL_QUEUE, self.TRANSCRIBE_QUEUE],
                error_queue=self.ERROR_QUEUE,
                implementation=ClassifierProcessor,
            ),
            "crawler": ProcessorConfig(
                name="crawler",
                input_queue=self.CRAWL_QUEUE,
                output_queues=[self.SUMMARY_QUEUE],
                error_queue=self.ERROR_QUEUE,
                implementation=CrawlerProcessor,
            ),
            "transcriber": ProcessorConfig(
                name="transcriber",
                input_queue=self.TRANSCRIBE_QUEUE,
                output_queues=[self.SUMMARY_QUEUE],
                error_queue=self.ERROR_QUEUE,
                implementation=TranscriberProcessor,
            ),
            "summarizer": ProcessorConfig(
                name="summarizer",
                input_queue=self.SUMMARY_QUEUE,
                output_queues=[self.EMBEDDING_QUEUE],
                error_queue=self.ERROR_QUEUE,
                implementation=SummarizerProcessor,
            ),
            "embedding": ProcessorConfig(
                name="embedding",
                input_queue=self.EMBEDDING_QUEUE,
                output_queues=[],
                error_queue=self.ERROR_QUEUE,
                implementation=EmbeddingProcessor,
            ),
            "notifier": ProcessorConfig(
                name="notifier",
                input_queue=self.NOTIFY_QUEUE,
                output_queues=[],
                error_queue=self.ERROR_QUEUE,
                implementation=NotifierProcessor,
            ),
        }
