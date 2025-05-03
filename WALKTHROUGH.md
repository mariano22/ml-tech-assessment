# Repository Walkthrough: Transcript Analysis API

Below is a progressive, "big-picture-to-details" walkthrough of the entire repository.  
If you read it top-to-bottom you will first understand the overall architecture and the main runtime flow; afterwards each directory / file is explained so you can dive as deep as you like.

--------------------------------------------------------------------
## 1. HIGH-LEVEL OVERVIEW
--------------------------------------------------------------------
• **Goal** A FastAPI micro-service that receives raw text transcripts, sends them to an LLM (OpenAI) and returns a summary plus next-action list.

• **Architectural style** Hexagonal Architecture (aka Ports & Adapters, a flavour of Clean Architecture).

• **Guiding principles**  
  – Modularity and single responsibility for each component.  
  – Layer decoupling through explicit Python protocols / ABC interfaces (the *ports*).  
  – Domain objects are pure business entities; they do not depend on FastAPI, OpenAI, databases, etc.  
  – All cross-layer data is carried by DTOs (Data-Transfer Objects) so that the domain layer never "sees" raw JSON or OpenAI python-objects.  
  – Async-first where I/O may block (OpenAI calls) + ability to run many analyses concurrently (`asyncio.gather`).  

**Runtime flow in 10 seconds**  

```
REST request  -->  Adapters.Inbound (FastAPI)
                 -> Application service (business orchestration)
                 -> Port   (LLm) -----------> Adapter.Outbound (OpenAI)
                 -> Port   (Repository) ----> Infrastructure (in-memory store)
                 <- Domain model -----------/
                 <- Serializer DTO ---------/
                 -> HTTP response
```

--------------------------------------------------------------------
## 2. KEY CONCEPTS (DTO & Hexagonal Architecture)
--------------------------------------------------------------------
**DTO (Data Transfer Object)**  
A small, immutable object used purely to pass data between layers/bounded contexts.  
Here: `AnalysisDTO` is the exact shape the LLM returns (`summary`, `action_items`).  
The application converts it to a `TranscriptAnalysis` domain entity through
`AnalysisDTO.to_domain_model()`.

**Hexagonal / Ports & Adapters**  
Think of the application core as a hexagon with *ports* (interfaces).  
• Inside: pure domain logic & use-cases.  
• Outside: adapters implement the ports (HTTP controllers, OpenAI client, DB).  
Benefits: swap any adapter without touching business code, test each piece in isolation.

--------------------------------------------------------------------
## 3. REPOSITORY TOUR
--------------------------------------------------------------------
### 3.1 Entrypoint & Dependency wiring
```
app/main.py
```
• Builds the FastAPI app.  
• Creates an `OpenAIAdapter` (unless a mock is injected by tests).  
• Uses `app/container.py` as a tiny **DI factory** to assemble the `TranscriptAnalyzerService` with an `LLm` and `TranscriptRepository`.

### 3.2 Domain Layer (pure business structures)
```
app/domain/models.py         # TranscriptAnalysis entity (id, summary, action_items)
app/domain/exceptions.py     # Domain-specific errors (EmptyTranscriptError, ...)
```
No external imports except `uuid` & `pydantic` for validation.

### 3.3 Ports (interfaces = boundaries)
```
app/ports/llm.py             # LLm protocol: sync & async completion
app/ports/repository.py      # TranscriptRepository CRUD interface
app/ports/service.py         # TranscriptAnalyzer use-case interface
app/ports/__init__.py        # re-exports to shorten import paths
```
Any layer that wants "an LLM" only depends on these ABCs.

### 3.4 Application Layer (use-case orchestration)
```
app/application/analyze_service.py
```
Responsibilities:
1. Validate input (raise `EmptyTranscriptError`, `InvalidBatchError`).
2. Build prompts (`app/prompts.py`).
3. Call the LLM port (sync or async).
4. Convert `AnalysisDTO` ➜ `TranscriptAnalysis`.
5. Persist to repository.
6. Provide async batch analysis with `asyncio.gather`.

No mention of FastAPI or OpenAI here—the service has **no idea** where the request came from nor where it will be stored.

### 3.5 Adapters
• **Outbound**  
```
app/adapters/openai.py       # Implements LLm port using openai SDK
```
Wraps both sync and async client, returns parsed DTO defined by caller.

• **Inbound**  
```
app/adapters/inbound/rest.py
```
Builds a FastAPI `APIRouter`:
  – `/transcripts/analyze` GET+POST  
  – `/transcripts/analyze/batch`  
  – `/transcripts/{id}`  
  – `/health`  
Each handler catches domain errors and maps them to proper HTTP codes.

### 3.6 Infrastructure
```
app/infrastructure/repositories.py
```
In-memory dict `{uuid: TranscriptAnalysis}` implementing `TranscriptRepository`.  
Easy to replace with PostgreSQL, Redis, etc. by writing another adapter that fulfils the same port interface.

### 3.7 DTOs
```
app/dto/analysis.py
```
Pydantic model that exactly mirrors the structured JSON returned by OpenAI.  
Method `to_domain_model()` insulates the domain from LLM data quirks.

### 3.8 Config & helpers
```
app/configurations.py        # Reads .env via pydantic-settings
app/prompts.py               # System & user prompts
app/container.py             # DI composition root
```

--------------------------------------------------------------------
## 4. ASYNCHRONOUS IMPLEMENTATION DETAILS
--------------------------------------------------------------------
Why async? OpenAI requests are network-bound; we can free the event-loop while waiting.

**Key points**  
• `LLm.run_completion_async()` returns the parsed DTO.  
• `TranscriptAnalyzerService.analyze_async()` awaits the adapter and then persists.  
• `TranscriptAnalyzerService.analyze_many()` creates a list of coroutines and calls `asyncio.gather` to run them in parallel.  
• FastAPI endpoints are all *async def* so they can await the service without blocking.

--------------------------------------------------------------------
## 5. TEST INFRASTRUCTURE
--------------------------------------------------------------------
Directory `tests/` contains:

• Mock classes (`MockLLM`, `MockDTO`) so **no real API key** is required.  
• Fixtures for sync/async services with dependency injection.  
• Coverage (> 95 %).  
• Docker-based runner:  
  – `docker-compose.test.yml test`   → regular tests  
  – `docker-compose.test.yml test-coverage` → coverage HTML in `htmlcov/`

```bash
docker-compose -f docker-compose.test.yml run test
```

--------------------------------------------------------------------
## 6. DOCKER & DEVOPS FILES
--------------------------------------------------------------------
• `Dockerfile` multi-stage; installs prod deps, then optionally test deps when `BUILD_ENV=dev`.  
• `.dockerignore` excludes caches, tests, pyc etc.  
• `docker-compose.yml` runs the web API + reverse-proxy if needed.  
• `docker-compose.test.yml` single "test" service mounting source & tests.  
• `setup.sh` helper that writes a `.env` from `env.example`.

--------------------------------------------------------------------
## 7. DECISION LOG (WHY THINGS ARE THIS WAY)
--------------------------------------------------------------------
1. **Hexagonal > classic MVC** so we can swap OpenAI for Anthropic or a local LLM without touching domain code.  
2. **DTO layer** keeps LLM JSON mistakes out of domain objects; also ensures schema validation.  
3. **In-memory repo first** fast dev; future DB integration only needs one new adapter.  
4. **FastAPI routers placed in adapters/inbound** Web framework is an outer concern, fits hexagonal radius.  
5. **Dependency factory (`container.py`)** tests can inject mocks, main app uses real adapter.  
6. **Async by default** more throughput with minimal added complexity, important for batch endpoint.  
7. **Tests run in Docker** exact parity CI environment, no dev machine pollution.  
8. **Pydantic everywhere** runtime data validation is priceless for external APIs, and gives automatic OpenAPI docs.  

--------------------------------------------------------------------
## 8. WHERE TO START READING CODE
--------------------------------------------------------------------
1. `app/main.py` (bootstrap)  
2. `app/adapters/inbound/rest.py` (HTTP layer)  
3. `app/application/analyze_service.py` (core business logic)  
4. `app/domain/` and `app/dto/` (data shapes)  
5. `app/adapters/openai.py` and `app/infrastructure/repositories.py` (ports implementations)  

With this progression you continuously expand your mental model without being overwhelmed.

--------------------------------------------------------------------
## 9. NEXT STEPS / EXTENSIONS
--------------------------------------------------------------------
• Add a SQL or NoSQL repository adapter implementing `TranscriptRepository`.  
• Swap `OpenAIAdapter` for a huggingface-based adapter—no business code change required.  
• Move prompts to a configurable prompt-library.  
• Use a message queue + worker for heavy batch processing but the service interface stays. 