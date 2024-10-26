import logging
from typing import Any, Dict, Tuple, List, Optional, Callable, Coroutine
from abc import ABC, abstractmethod

from aio_pika.abc import AbstractIncomingMessage

logger = logging.getLogger(__name__)


class Processor(ABC):
    """Abstract base class for processors, defining the main processing and error handling methods,
    and enforcing queue settings as abstract properties."""

    @property
    @abstractmethod
    def input_queue(self) -> str:
        """Abstract property for the input queue name."""
        pass

    @property
    @abstractmethod
    def exchange_queue(self) -> str:
        """Abstract property for the exchange queue name."""
        pass

    @property
    @abstractmethod
    def output_queues(self) -> List[str]:
        """Abstract property for the list of output queue names."""
        pass

    @property
    @abstractmethod
    def error_queue(self) -> str:
        """Abstract property for the error queue name."""
        pass

    @abstractmethod
    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Abstract method that defines the processor logic, must be implemented by subclasses."""
        pass

    @property
    def handle_error(
        self,
    ) -> Optional[
        Callable[
            [Exception, Optional[Dict[str, Any]], AbstractIncomingMessage],
            Coroutine[Any, Any, None],
        ]
    ]:
        """Optional error handler; defaults to None if not overridden."""
        return None
