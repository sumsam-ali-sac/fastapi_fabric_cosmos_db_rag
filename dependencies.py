"""
Enhanced dependency injection with factory pattern and better error handling
Dependency injection setup for FastAPI
"""

from typing import Dict

from azure.cosmos.aio import CosmosClient
from azure.identity import DefaultAzureCredential
from openai import AsyncAzureOpenAI

from config import Settings, get_settings
from core.logger import get_logger
from exceptions import DatabaseConnectionError

logger = get_logger(__name__)


class ClientFactory:
    """Factory for creating and managing client instances"""

    _cosmos_instance: "CosmosDBClient" = None
    _openai_instance: "OpenAIClients" = None

    @classmethod
    def get_cosmos_client(cls, settings: Settings) -> "CosmosDBClient":
        """Get or create Cosmos DB client - Singleton pattern"""
        if cls._cosmos_instance is None:
            cls._cosmos_instance = CosmosDBClient(settings)
        return cls._cosmos_instance

    @classmethod
    def get_openai_clients(cls, settings: Settings) -> "OpenAIClients":
        """Get or create OpenAI clients - Singleton pattern"""
        if cls._openai_instance is None:
            cls._openai_instance = OpenAIClients(settings)
        return cls._openai_instance

    @classmethod
    def reset(cls):
        """Reset client instances - useful for testing"""
        cls._cosmos_instance = None
        cls._openai_instance = None


class CosmosDBClient:
    """
    Enhanced Cosmos DB client with connection pooling and health checks
    Cosmos DB client wrapper with improved error handling
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: CosmosClient = None
        self.db = None
        self.movies_container = None
        self.cache_container = None
        self._connected = False

    async def connect(self) -> None:
        """Initialize Cosmos DB connection with retry logic"""
        if self._connected:
            return

        retries = 0
        last_error = None

        while retries < self.settings.cosmos_max_retries:
            try:
                self.client = CosmosClient(
                    url=self.settings.cosmos_endpoint,
                    credential=DefaultAzureCredential(),
                    connection_timeout=self.settings.cosmos_connection_timeout,
                )
                self.db = self.client.get_database_client(
                    self.settings.cosmos_database_name
                )
                self.movies_container = self.db.get_container_client(
                    self.settings.cosmos_container_name
                )
                self.cache_container = self.db.get_container_client(
                    self.settings.cosmos_cache_container_name
                )

                self._connected = True
                logger.info("Successfully connected to Cosmos DB")
                return

            except Exception as e:
                last_error = e
                retries += 1
                logger.warning(f"Cosmos DB connection attempt {retries} failed: {e}")

        logger.error(f"Failed to connect to Cosmos DB after {retries} attempts")
        raise DatabaseConnectionError(
            f"Failed to connect to Cosmos DB: {str(last_error)}"
        )

    async def close(self) -> None:
        """Close Cosmos DB connection"""
        if self.client and self._connected:
            await self.client.close()
            self._connected = False
            logger.info("Closed Cosmos DB connection")

    async def health_check(self) -> Dict[str, bool]:
        """Check container connectivity"""
        status = {"movies": False, "cache": False}
        try:
            if self.movies_container:
                await self.movies_container.read()
                status["movies"] = True
        except Exception as e:
            logger.warning(f"Movies container health check failed: {e}")

        try:
            if self.cache_container:
                await self.cache_container.read()
                status["cache"] = True
        except Exception as e:
            logger.warning(f"Cache container health check failed: {e}")

        return status

    @property
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected


class OpenAIClients:
    """Enhanced OpenAI clients with timeout configuration"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.completions_client: AsyncAzureOpenAI = None
        self.embeddings_client: AsyncAzureOpenAI = None

    def initialize(self) -> None:
        """Initialize OpenAI clients with timeout settings"""
        try:
            self.completions_client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.openai_endpoint,
                api_key=self.settings.openai_api_key,
                api_version=self.settings.openai_api_version,
                timeout=self.settings.openai_request_timeout,
            )

            self.embeddings_client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.openai_embeddings_endpoint,
                api_key=self.settings.openai_embeddings_api_key,
                api_version=self.settings.openai_embeddings_api_version,
                timeout=self.settings.openai_request_timeout,
            )
            logger.info("Initialized Azure OpenAI clients")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI clients: {e}")
            raise


async def get_cosmos_client() -> CosmosDBClient:
    """Get Cosmos DB client"""
    settings = get_settings()
    client = ClientFactory.get_cosmos_client(settings)

    if not client.is_connected:
        await client.connect()

    return client


async def get_openai_clients() -> OpenAIClients:
    """Get OpenAI clients"""
    settings = get_settings()
    clients = ClientFactory.get_openai_clients(settings)

    if not clients.completions_client:
        clients.initialize()

    return clients


async def get_settings_dep() -> Settings:
    """Get settings dependency"""
    return get_settings()
