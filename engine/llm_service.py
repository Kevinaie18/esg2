"""
Enhanced LLM service interface for handling interactions with different LLM providers.
Includes robust error handling, provider fallback, and Streamlit Cloud integration.
Version 1.1 - Updated Claude models
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import os
import time
from dataclasses import dataclass
from enum import Enum
import streamlit as st
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from functools import lru_cache
import litellm
from litellm import completion
from datetime import datetime

# Configure logger
logger.remove()
logger.add(
    "logs/llm_service.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)


class ProviderError(Exception):
    """Base exception for provider-specific errors."""
    pass


class RateLimitError(ProviderError):
    """Raised when a rate limit is hit."""
    pass


class TokenLimitError(ProviderError):
    """Raised when token limit is exceeded."""
    pass


class ProviderType(Enum):
    """Enum for supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"


# Model name mappings - Updated for V1.1
MODEL_MAPPINGS = {
    # OpenAI models
    "gpt-4-turbo-preview": "gpt-4-turbo-preview",
    "gpt-4o": "gpt-4o",
    "gpt-4": "gpt-4",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    # Anthropic models - UPDATED
    "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4-20250514",
    "claude-3-5-sonnet-20241022": "anthropic/claude-3-5-sonnet-20241022",
    # Legacy Claude models (keep for backwards compatibility)
    "claude-3-opus-20240229": "anthropic/claude-3-opus-20240229",
    "claude-3-sonnet-20240229": "anthropic/claude-3-sonnet-20240229",
    "claude-3-haiku-20240307": "anthropic/claude-3-haiku-20240307",
    # DeepSeek models
    "deepseek-chat": "fireworks_ai/accounts/fireworks/models/deepseek-r1-basic",
}


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 120
    max_retries: int = 3
    retry_delay: int = 1


@dataclass
class RequestMetrics:
    """Metrics for an LLM request."""
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    latency: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None


class BaseLLMService(ABC):
    """Base class for LLM services with common functionality."""
    
    provider_name: str = ""
    env_key: str = ""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Set up the provider-specific client."""
        os.environ[self.env_key] = self.config.api_key
        logger.info(f"Successfully initialized {self.provider_name} client")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response from the LLM."""
        start_time = time.time()
        
        # Resolve model name through mapping
        model = MODEL_MAPPINGS.get(self.config.model, self.config.model)
        
        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            # Calculate metrics
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            latency = time.time() - start_time
            
            # Log metrics
            self._log_metrics(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency=latency,
                success=True
            )
            
            return response.choices[0].message.content
            
        except litellm.RateLimitError as e:
            self._log_metrics(0, 0, 0, time.time() - start_time, False, str(e))
            raise RateLimitError(str(e))
        except Exception as e:
            self._log_metrics(0, 0, 0, time.time() - start_time, False, str(e))
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the text."""
        try:
            model = MODEL_MAPPINGS.get(self.config.model, self.config.model)
            return litellm.token_counter(model=model, text=text)
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            # Fallback: estimate ~4 chars per token
            return len(text) // 4
    
    def _log_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency: float,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log request metrics."""
        metrics = RequestMetrics(
            provider=self.provider_name,
            model=self.config.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=self._calculate_cost(prompt_tokens, completion_tokens),
            latency=latency,
            timestamp=datetime.now(),
            success=success,
            error=error
        )
        logger.info(f"Request metrics: {metrics}")
    
    @abstractmethod
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the request. Provider-specific."""
        pass


class OpenAIService(BaseLLMService):
    """OpenAI LLM service implementation."""
    
    provider_name = "openai"
    env_key = "OPENAI_API_KEY"
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the request."""
        PRICING = {
            "gpt-4-turbo-preview": {"prompt": 0.01, "completion": 0.03},
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002}
        }
        
        model = self.config.model
        if model not in PRICING:
            return 0.0
        
        prompt_cost = (prompt_tokens / 1000) * PRICING[model]["prompt"]
        completion_cost = (completion_tokens / 1000) * PRICING[model]["completion"]
        return prompt_cost + completion_cost


class AnthropicService(BaseLLMService):
    """Anthropic LLM service implementation."""
    
    provider_name = "anthropic"
    env_key = "ANTHROPIC_API_KEY"
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the request."""
        PRICING = {
            # New models
            "claude-sonnet-4-20250514": {"prompt": 0.003, "completion": 0.015},
            "claude-3-5-sonnet-20241022": {"prompt": 0.003, "completion": 0.015},
            # Legacy models
            "claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
            "claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015},
            "claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125}
        }
        
        model = self.config.model
        if model not in PRICING:
            return 0.0
        
        prompt_cost = (prompt_tokens / 1000) * PRICING[model]["prompt"]
        completion_cost = (completion_tokens / 1000) * PRICING[model]["completion"]
        return prompt_cost + completion_cost


class DeepSeekService(BaseLLMService):
    """DeepSeek LLM service implementation."""
    
    provider_name = "deepseek"
    env_key = "FIREWORKS_API_KEY"
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the request."""
        PRICING = {
            "deepseek-chat": {"prompt": 0.0005, "completion": 0.001}
        }
        
        model = self.config.model
        if model not in PRICING:
            return 0.0
        
        prompt_cost = (prompt_tokens / 1000) * PRICING[model]["prompt"]
        completion_cost = (completion_tokens / 1000) * PRICING[model]["completion"]
        return prompt_cost + completion_cost


class LLMServiceManager:
    """Manager class for handling multiple LLM providers with fallback support."""
    
    def __init__(self):
        self.providers: Dict[ProviderType, BaseLLMService] = {}
        self._load_config()
        self._initialize_providers()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables and Streamlit secrets."""
        # Load API keys
        self.api_keys = {
            ProviderType.OPENAI: os.getenv("OPENAI_API_KEY"),
            ProviderType.ANTHROPIC: os.getenv("ANTHROPIC_API_KEY"),
            ProviderType.DEEPSEEK: os.getenv("FIREWORKS_API_KEY")
        }
        
        # Default models - Updated for V1.1
        self.models = {
            ProviderType.OPENAI: "gpt-4-turbo-preview",
            ProviderType.ANTHROPIC: "claude-sonnet-4-20250514",
            ProviderType.DEEPSEEK: "deepseek-chat"
        }
    
    def _initialize_providers(self) -> None:
        """Initialize LLM providers."""
        service_classes = {
            ProviderType.OPENAI: OpenAIService,
            ProviderType.ANTHROPIC: AnthropicService,
            ProviderType.DEEPSEEK: DeepSeekService
        }
        
        for provider_type, service_class in service_classes.items():
            if self.api_keys[provider_type]:
                config = ProviderConfig(
                    api_key=self.api_keys[provider_type],
                    model=self.models[provider_type]
                )
                self.providers[provider_type] = service_class(config)
                logger.info(f"Initialized {provider_type.value} provider")
    
    def generate_response(
        self,
        prompt: str,
        primary_provider: ProviderType = ProviderType.OPENAI,
        fallback_providers: Optional[List[ProviderType]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response using the specified provider with fallback options."""
        providers_to_try = [primary_provider]
        if fallback_providers:
            providers_to_try.extend(fallback_providers)
        
        last_error = None
        for provider in providers_to_try:
            if provider not in self.providers:
                logger.warning(f"Provider {provider.value} not initialized, skipping...")
                continue
            
            try:
                logger.info(f"Attempting to generate response with {provider.value}")
                return self.providers[provider].generate_response(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            except Exception as e:
                last_error = e
                logger.error(f"Error with {provider.value}: {str(e)}")
                continue
        
        if last_error:
            raise last_error
        raise ProviderError("No available providers to handle the request")


@lru_cache()
def get_llm_manager() -> LLMServiceManager:
    """Get or create the LLM service manager instance."""
    return LLMServiceManager()
