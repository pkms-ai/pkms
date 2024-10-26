# __init__.py in processors module

from .processor import Processor
from .processor_factory import ProcessorFactory

# from .summarizer_processor import SummarizerProcessor

__all__ = [
    "ProcessorFactory",
    "Processor",
]
