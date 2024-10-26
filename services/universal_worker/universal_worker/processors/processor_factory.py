from typing import Type, Optional
from .processor import Processor
from .crawler_processor import CrawlerProcessor
from .embedding_processor import EmbeddingProcessor
from .classifier_processor import ClassifierProcessor
from .summarizer_processor import SummarizerProcessor
# from .summarizer_processor import SummarizerProcessor  # Example other processors


class ProcessorFactory:
    """Factory class to create instances of processors based on processor name."""

    _processors = {
        "crawler": CrawlerProcessor,
        "summarizer": SummarizerProcessor,
        "embedding": EmbeddingProcessor,
        "classifier": ClassifierProcessor,
        # Add additional processors here as needed
    }

    @staticmethod
    def create_processor(processor_name: str) -> Processor:
        """Creates and returns a processor instance based on the given name."""
        processor_class: Optional[Type[Processor]] = ProcessorFactory._processors.get(
            processor_name
        )
        if processor_class is None:
            raise ValueError(f"Processor '{processor_name}' not found.")
        return processor_class()  # Instantiate and return the processor class instance
