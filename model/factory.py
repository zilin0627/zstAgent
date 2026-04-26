import time
from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi

from utils.config_handler import rag_config


_SSL_KEYWORDS = ("ssl", "eof", "connection", "timeout", "max retries", "connectionpool")


class BasModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class RetryChatTongyi(ChatTongyi):
    """ChatTongyi with retry on transient network errors."""

    _max_retries: int = 3
    _retry_base_delay: float = 1.5

    def _call_with_retry(self, fn, *args, **kwargs):
        last_err = None
        for attempt in range(self._max_retries):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_err = exc
                err_lower = str(exc).lower()
                if any(kw in err_lower for kw in _SSL_KEYWORDS) and attempt < self._max_retries - 1:
                    time.sleep(self._retry_base_delay * (2 ** attempt))
                    continue
                raise
        raise last_err

    def _generate(self, *args, **kwargs):
        return self._call_with_retry(super()._generate, *args, **kwargs)

    def _stream(self, *args, **kwargs):
        return self._call_with_retry(super()._stream, *args, **kwargs)


class ChatModelFactory(BasModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return RetryChatTongyi(model=rag_config["chat_model_name"])


class RetryDashScopeEmbeddings(DashScopeEmbeddings):
    """DashScopeEmbeddings with retry on SSL / network transient errors."""

    _max_retries: int = 3
    _retry_base_delay: float = 1.5

    def _call_with_retry(self, fn, *args, **kwargs):
        last_err = None
        for attempt in range(self._max_retries):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_err = exc
                err_lower = str(exc).lower()
                if any(kw in err_lower for kw in _SSL_KEYWORDS) and attempt < self._max_retries - 1:
                    time.sleep(self._retry_base_delay * (2 ** attempt))
                    continue
                raise
        raise last_err

    def embed_documents(self, texts, **kwargs):
        return self._call_with_retry(super().embed_documents, texts, **kwargs)

    def embed_query(self, text, **kwargs):
        return self._call_with_retry(super().embed_query, text, **kwargs)


class EmbeddingsFactory(BasModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return RetryDashScopeEmbeddings(model=rag_config["embedding_model_name"])


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
