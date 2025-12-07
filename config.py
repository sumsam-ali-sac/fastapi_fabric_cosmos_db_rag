"""
Configuration management for FastAPI Cosmos DB application
"""

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = Field(
        default="Cosmos DB RAG Chat API", description="Application name"
    )
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment")

    # Cosmos DB Configuration
    cosmos_endpoint: str = Field(
        description="Cosmos DB endpoint URL",
        examples=["https://xxxxx.sql.cosmos.fabric.microsoft.com:443/"],
    )
    cosmos_database_name: str = Field(
        default="VectorCosmosDB", description="Database name"
    )
    cosmos_container_name: str = Field(
        default="vectorstorecontainer", description="Main container name"
    )
    cosmos_cache_container_name: str = Field(
        default="vectorcachecontainer", description="Cache container name"
    )
    cosmos_vector_property_name: str = Field(
        default="vector", description="Vector property name"
    )
    cosmos_max_retries: int = Field(
        default=3, ge=0, description="Max connection retries"
    )
    cosmos_connection_timeout: int = Field(
        default=30, ge=1, description="Connection timeout in seconds"
    )
    # Azure AD Configuration for Service Principal
    azure_tenant_id: str = Field(description="Azure AD Tenant ID")
    azure_client_id: str = Field(description="Azure AD Client ID")
    azure_client_secret: str = Field(description="Azure AD Client Secret")

    # Azure OpenAI Configuration
    openai_endpoint: str = Field(description="Azure OpenAI endpoint URL")
    openai_api_key: str = Field(description="Azure OpenAI API key")
    openai_api_version: str = Field(
        default="2024-02-15-preview", description="OpenAI API version"
    )
    openai_completions_model: str = Field(
        default="gpt-4o", description="Model for completions"
    )
    openai_request_timeout: int = Field(
        default=60, ge=1, description="OpenAI request timeout in seconds"
    )

    # Azure OpenAI Embeddings Configuration
    openai_embeddings_endpoint: str = Field(
        description="Azure OpenAI embeddings endpoint"
    )
    openai_embeddings_api_key: str = Field(
        description="Azure OpenAI embeddings API key"
    )
    openai_embeddings_api_version: str = Field(
        default="2024-05-01-preview", description="Embeddings API version"
    )
    openai_embeddings_model: str = Field(
        default="text-embedding-3-small", description="Embeddings model"
    )
    openai_embeddings_dimensions: int = Field(
        default=1536, description="Embedding dimensions"
    )

    # Application Settings
    max_search_results: int = Field(
        default=20, ge=1, le=100, description="Max search results"
    )
    min_similarity_score: float = Field(
        default=0.02, ge=0.0, le=1.0, description="Minimum similarity score"
    )
    cache_similarity_threshold: float = Field(
        default=0.99, ge=0.0, le=1.0, description="Cache similarity threshold"
    )
    chat_history_limit: int = Field(
        default=3, ge=1, le=10, description="Chat history limit"
    )

    # CORS Configuration
    cors_origins: list = Field(default=["*"], description="CORS allowed origins")
    cors_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_methods: list = Field(default=["*"], description="CORS allowed methods")
    cors_headers: list = Field(default=["*"], description="CORS allowed headers")

    # Monitoring Configuration
    enable_request_logging: bool = Field(
        default=True, description="Enable request logging"
    )
    enable_performance_monitoring: bool = Field(
        default=True, description="Enable performance monitoring"
    )
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
