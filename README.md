# Cosmos DB RAG Chat API - Production-Grade FastAPI

A **production-ready, scalable FastAPI application** for querying Azure Cosmos DB with Retrieval-Augmented Generation (RAG) using Azure OpenAI embeddings and completions.

## 🎯 Key Features

- **Vector Search**: Fast similarity search on Cosmos DB
- **RAG (Retrieval-Augmented Generation)**: Ground responses in actual data
- **Caching**: Smart response caching for frequently asked questions
- **Async/Await**: Full async support for high concurrency
- **API Versioning**: v1 endpoints with future versioning support
- **Structured Logging**: JSON-formatted logs for monitoring
- **Error Handling**: Comprehensive exception hierarchy with error codes
- **Repository Pattern**: Clean data access layer abstraction
- **Dependency Injection**: Factory pattern for client management
- **Request Tracking**: Request IDs for distributed tracing
- **Health Checks**: Container and database status monitoring
- **Performance Metrics**: Built-in operation tracking and reporting

## 📁 Project Structure

\`\`\`
fastapi-cosmos-rag/
├── core/                      # Core utilities and abstractions
│   ├── __init__.py
│   ├── base.py               # Base repository and service classes
│   ├── logger.py             # Structured logging
│   ├── cache.py              # Caching abstractions
│   ├── middleware.py         # Custom middleware
│   ├── pagination.py         # Pagination utilities
│   └── filters.py            # Query filtering
│
├── api/                       # API routes by version
│   └── v1/
│       ├── __init__.py
│       └── routes.py         # v1 endpoint handlers
│
├── database/                  # Data access layer
│   ├── __init__.py
│   ├── cosmos_service.py     # Cosmos DB operations
│   └── repositories.py       # Repository implementations
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── base_chat_service.py # Abstract chat service
│   ├── chat_service.py      # Chat orchestration
│   └── openai_service.py    # OpenAI integration
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── validators.py        # Input validation
│   ├── metrics.py           # Performance tracking
│   └── helpers.py           # Helper functions
│
├── config.py                 # Configuration management
├── models.py                # Pydantic models
├── dependencies.py          # Dependency injection setup
├── exceptions.py            # Custom exceptions
├── main.py                  # Application entry point
│
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration
│   ├── test_endpoints.py   # Endpoint tests
│   └── test_services.py    # Service tests
│
├── scripts/                  # Utility scripts
│   ├── setup_db.py         # Database initialization
│   └── migrate.py          # Database migrations
│
├── .env.example            # Environment template
├── .dockerignore           # Docker ignore file
├── .gitignore              # Git ignore file
├── Dockerfile              # Container image
├── docker-compose.yml      # Container orchestration
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
└── README.md               # This file
\`\`\`

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Azure Cosmos DB account
- Azure OpenAI deployment (completions + embeddings)

### Installation

1. **Clone the repository**
\`\`\`bash
git clone <repo-url>
cd fastapi-cosmos-rag
\`\`\`

2. **Create virtual environment**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Configure environment**
\`\`\`bash
cp .env.example .env
# Edit .env with your Azure credentials
\`\`\`

5. **Run application**
\`\`\`bash
python main.py
\`\`\`

The API is now available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### Health Check
\`\`\`bash
GET /api/v1/health

Response:
{
  "status": "healthy",
  "database": "VectorCosmosDB",
  "containers": {
    "movies": true,
    "cache": true
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
\`\`\`

#### Chat Endpoint
\`\`\`bash
POST /api/v1/chat

Request:
{
  "message": "Find action movies from the 2000s",
  "use_cache": true,
  "num_results": 5
}

Response:
{
  "response": "Here are some great action movies from the 2000s...",
  "from_cache": false,
  "sources": [
    {
      "id": "movie_123",
      "title": "...",
      "similarity_score": 0.92
    }
  ]
}
\`\`\`

#### Clear Cache
\`\`\`bash
POST /api/v1/clear-cache

Response:
{
  "message": "Cache management",
  "info": "Use Cosmos DB portal for bulk cache operations"
}
\`\`\`

## 🏗️ Architecture

### Layered Architecture

\`\`\`
API Layer (routes) → Service Layer → Repository Layer → Database Layer
     ↓                                                          ↓
  FastAPI Routes        Business Logic      Data Access    Cosmos DB
\`\`\`

### Core Components

**1. Repository Pattern**
- `BaseRepository`: Abstract interface for data access
- `DocumentRepository`: Document CRUD operations
- `CacheRepository`: Cache management

**2. Service Layer**
- `BaseChatService`: Abstract chat service interface
- `ChatService`: Orchestrates RAG workflow
- `OpenAIService`: Embedding generation
- `CompletionService`: Response generation

**3. Dependency Injection**
- `ClientFactory`: Singleton pattern for clients
- `CosmosDBClient`: Cosmos DB connection management
- `OpenAIClients`: Azure OpenAI clients

**4. Middleware**
- `RequestIDMiddleware`: Add request tracking IDs
- `RequestLoggingMiddleware`: Log request/response details
- `ErrorHandlingMiddleware`: Global error catching

### Data Flow

\`\`\`
User Request
    ↓
ChatRequest (validation)
    ↓
ChatService.chat()
    ├→ Generate Embedding (OpenAI)
    ├→ Check Cache (CosmosDB)
    ├→ Vector Search (CosmosDB)
    ├→ Get Chat History (CosmosDB)
    ├→ Generate Completion (OpenAI)
    ├→ Cache Response (CosmosDB)
    ↓
ChatResponse
\`\`\`

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COSMOS_ENDPOINT` | Yes | - | Cosmos DB endpoint URL |
| `COSMOS_KEY` | Yes | - | Cosmos DB primary key |
| `OPENAI_ENDPOINT` | Yes | - | Azure OpenAI endpoint |
| `OPENAI_API_KEY` | Yes | - | Azure OpenAI API key |
| `ENVIRONMENT` | No | production | Deployment environment |
| `LOG_LEVEL` | No | INFO | Logging level |
| `MAX_SEARCH_RESULTS` | No | 20 | Max vector search results |
| `MIN_SIMILARITY_SCORE` | No | 0.02 | Minimum similarity threshold |
| `CACHE_SIMILARITY_THRESHOLD` | No | 0.99 | Cache hit similarity |
| `CHAT_HISTORY_LIMIT` | No | 3 | Messages to include in context |

## 🧪 Testing

### Run Tests
\`\`\`bash
pytest
\`\`\`

### Run with Coverage
\`\`\`bash
pytest --cov=. --cov-report=html
\`\`\`

### Run Specific Test
\`\`\`bash
pytest tests/test_services.py::TestChatService -v
\`\`\`

## 🐳 Docker Deployment

### Build Image
\`\`\`bash
docker build -t cosmos-rag-api:latest .
\`\`\`

### Run Container
\`\`\`bash
docker run -p 8000:8000 \
  -e COSMOS_ENDPOINT=<your-endpoint> \
  -e COSMOS_KEY=<your-key> \
  -e OPENAI_ENDPOINT=<your-openai> \
  -e OPENAI_API_KEY=<your-api-key> \
  cosmos-rag-api:latest
\`\`\`

### Docker Compose
\`\`\`bash
docker-compose up
\`\`\`

## 📊 Monitoring & Logging

### Structured Logging
All logs are output in JSON format with:
- Timestamp
- Log level
- Logger name
- Message
- Request ID (if applicable)
- Additional context

### Performance Tracking
Operations automatically track:
- Execution duration
- Items scanned/returned
- Query metrics
- Custom metrics

View in logs or integrate with monitoring systems.

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **API Keys**: Use Azure Key Vault in production
3. **CORS**: Configure specific origins in production (not `["*"]`)
4. **Rate Limiting**: Implement in production
5. **Authentication**: Add OAuth/API key authentication
6. **Input Validation**: All inputs validated via Pydantic

## 🚦 Production Deployment Checklist

- [ ] Set `DEBUG=false`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure specific `CORS_ORIGINS`
- [ ] Use Azure Key Vault for secrets
- [ ] Enable request logging and monitoring
- [ ] Configure application insights
- [ ] Set up Azure Container Registry
- [ ] Deploy to Azure Container Instances/App Service
- [ ] Configure health check endpoints
- [ ] Set up CI/CD pipeline
- [ ] Enable HTTPS
- [ ] Configure auto-scaling

## 🛠️ Development

### Adding New Endpoints

1. Create route in `api/v1/routes.py`:
\`\`\`python
@router.post("/new-endpoint", response_model=ResponseModel)
async def new_endpoint(request: RequestModel):
    # Implementation
    pass
\`\`\`

2. Define models in `models.py`

3. Implement business logic in `services/`

### Adding New Services

1. Create abstract base in `services/base_*.py`
2. Implement in `services/*.py`
3. Register in dependency injection

## 📖 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Cosmos DB](https://docs.microsoft.com/azure/cosmos-db/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

## 📧 Support

For issues and questions, please open a GitHub issue or contact the maintainers.
