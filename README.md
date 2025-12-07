# Cosmos DB RAG Chat API — FastAPI example for Fabric's native Cosmos DB

This repository demonstrates a production-minded FastAPI application that connects to Azure Fabric's native Cosmos DB and performs Retrieval-Augmented Generation (RAG) using Azure OpenAI embeddings and completions. It includes examples for building a vector store, caching strategy, and orchestrating a RAG pipeline.

**Highlights:**

- **Purpose:** Show how to connect to Fabric's Cosmos DB, store/retrieve vectors, and generate grounded responses.
- **Stack:** FastAPI, Azure Cosmos DB (native Fabric integration), Azure OpenAI (embeddings + completions), PDM for dependency management.

**Table of contents**

- **Installation & Quick Start**
- **Environment & Service Principal setup**
- **How the RAG flow works**
- **Running with Docker / PDM**
- **Testing**
- **Security & production notes**

---

**Installation & Quick Start**

1. Clone the repository:

```bash
git clone <repo-url>
cd fastapi_fabric_cosmos_db_rag
```

2. Use PDM (recommended) or your preferred environment manager:

```bash
# Install PDM if you don't have it
pip install pdm
# Install production dependencies
pdm install --prod
# Run app in dev
pdm run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. API will be available at `http://localhost:8000`.

Environment file

- Copy `./.env.example` to `./.env` and set secrets. This repo includes `.env.example` with the required keys.

---

**Service Principal & Fabric (Cosmos DB) access**
To authenticate from this service to Fabric's native Cosmos DB it's typical to use an Azure AD Service Principal. High-level steps:

1. Go to MS Fabric and enable use of service principles:

<img width="896" height="525" alt="image" src="https://github.com/user-attachments/assets/c7aaab9f-4c39-4a82-bc53-0b0bc2232015" />



2. Create an Azure AD App (Service Principal):

```bash
# Use Azure CLI (example):
az ad app create --display-name my-fabric-app
az ad sp create --id <app-id>
# Create a client secret:
az ad app credential reset --id <app-id> --append --display-name "pymgmt-secret"
```

4. Grant workspace access to the service principal in Fabric (DB based access does not allow writes as of now:

- Navigate to your **Fabric workspace** and open it.
- Click **Manage workspace access** (gear icon or workspace settings).
- Click **Add user** and search for your service principal by its **App (Client) ID** or display name.
- Select the service principal and assign the role **Contributor** (or the necessary role with read/write access to Cosmos DB resources).
- Click **Add** to confirm.

This grants the service principal workspace-level access to manage Cosmos DB operations within Fabric.

3. Capture the following values and add them to your `.env`:

- `AZURE_TENANT_ID` — Tenant ID
- `AZURE_CLIENT_ID` — App (client) ID
- `AZURE_CLIENT_SECRET` — Client secret
- `COSMOS_ENDPOINT` — Cosmos DB endpoint URL
- `COSMOS_DATABASE_NAME` and container names

4. The application uses `azure-identity` to obtain tokens via `DefaultAzureCredential` if deployed to Azure services, or uses explicit client credentials in local/dev environments.

---

**RAG Flow (how this repo organizes it)**

- Client calls `POST /api/v1/chat` with `message`, optionally `use_cache` and `num_results`.
- The app generates an embedding (Azure OpenAI embeddings API).
- A vector similarity search is performed against Cosmos DB (vectors stored on documents in a container property).
- If a cached response with high similarity exists, it may be returned (cache hit threshold controlled in settings).
- Otherwise the top documents are used to build context and the OpenAI completions API generates the final assistant response.
- Successful responses can be cached in a separate cache container for future reuse.

---

Files of interest

- `main.py` — Application entry with lifespan that initializes the Cosmos + OpenAI clients.
- `config.py` — All configuration loaded from environment variables.
- `dependencies.py` — Factory for `CosmosDBClient` and OpenAI client wrappers.
- `database/cosmos_service.py` — Cosmos DB wrapper: connect, vector search, cache operations.
- `services/chat_service.py` — Orchestrates embeddings, search, completions, and caching.
- `notebooks/InsertDataIntoCosmosDB.ipynb` — Fabric notebook to populate Cosmos DB with sample data.

---

**Populating Cosmos DB with Data (Fabric Notebook)**

Before running the FastAPI service, you need to insert sample data into your Cosmos DB. Use the provided Fabric notebook:

1. **Navigate to your Fabric workspace** and create a new notebook or open the existing `InsertDataIntoCosmosDB.ipynb`.

2. **Download the dataset**:
   - Download the ZIP file from: [AzureDataRetrievalAugmentedGenerationSamples/DataSet/Movies](https://github.com/microsoft/AzureDataRetrievalAugmentedGenerationSamples/blob/main/DataSet/Movies/MovieLens-4489-256D.zip)
   - Extract `MovieLens-4489-256D.json` from the ZIP.

3. **Upload to Lakehouse**:
   - In your Fabric workspace, upload the JSON file to the lakehouse at:
   ```
   /lakehouse/default/Files/MovieLens-4489-256D/MovieLens-4489-256D.json
   ```

4. **Attach the Lakehouse** to the notebook (via notebook settings).

5. **Run the notebook**:
   - The notebook will:
     - Connect to your Cosmos DB using credentials from Fabric (environment/managed identity).
     - Create containers (`vectorstorecontainer`, `vectorcachecontainer`).
     - Parse the JSON dataset.
     - Generate vector embeddings for each record using Azure OpenAI embeddings.
     - Insert documents with vectors into the Cosmos DB.
   - Click **Run All** to execute all cells.

6. **Verify data insertion**:
   - Open the Fabric Cosmos DB explorer and check that documents are present in `vectorstorecontainer`.
   - Alternatively, run a health check: `GET /api/v1/health` (see section below).

Once data is populated, the FastAPI service can query and perform RAG on the indexed documents.

Running with Docker (PDM-based image)

Build and run using the included `Dockerfile` (PDM setup):

```bash
docker-compose up --build
```

---

Health checks & observability

- Health endpoint: `GET /api/v1/health` — returns `status`, `database`, `containers`, and `timestamp`.
- Structured logs (JSON) and request IDs are enabled via `core/logger.py` and middleware.

---

Testing

Run tests with pytest (PDM):

```bash
pdm run pytest -q
# or
pytest -q
```

---

`.env.example` (reference)

This repo contains `./.env.example`. Key entries you will typically set (trimmed):

```
APP_NAME=Cosmos DB RAG Chat API
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
COSMOS_ENDPOINT=https://<your-cosmos-account>.documents.azure.com:443/
COSMOS_DATABASE_NAME=VectorCosmosDB
COSMOS_CONTAINER_NAME=vectorstorecontainer
COSMOS_CACHE_CONTAINER_NAME=vectorcachecontainer
OPENAI_ENDPOINT=https://<your-openai-endpoint>/
OPENAI_API_KEY=<your-openai-key>
OPENAI_EMBEDDINGS_MODEL=text-embedding-3-small
OPENAI_EMBEDDINGS_DIMENSIONS=1536
```

Shoutout to MS for this tutorial: [Tutorial](https://learn.microsoft.com/en-us/azure/cosmos-db/gen-ai/rag-chatbot)

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
