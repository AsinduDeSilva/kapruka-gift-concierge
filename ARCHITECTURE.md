# Architecture & Diagrams — Kapruka Gift Concierge

This document contains comprehensive architectural diagrams for the Kapruka Gift Concierge system. For a high-level overview, see the [main README](./README.md).

---

## Table of Contents

1. [High-Level System Architecture](#1-high-level-system-architecture)
2. [Multi-Agent Orchestration Flow](#2-multi-agent-orchestration-flow)
3. [Router Decision Logic](#3-router-decision-logic)
4. [Reflection Safety Loop (Detailed)](#4-reflection-safety-loop-detailed)
5. [Memory Architecture](#5-memory-architecture)
6. [Hybrid RAG Pipeline](#6-hybrid-rag-pipeline)
7. [Hybrid Search Architecture (Qdrant)](#7-hybrid-search-architecture-qdrant)
8. [Data Ingestion Pipeline](#8-data-ingestion-pipeline)
9. [Class & Component Interaction Map](#9-class--component-interaction-map)
10. [Full Request Lifecycle (End-to-End)](#10-full-request-lifecycle-end-to-end)
11. [Technology Stack Breakdown](#11-technology-stack-breakdown)

---

## 1. High-Level System Architecture

A complete overview of every layer — from the Next.js frontend through FastAPI, the agent orchestration layer, memory systems, and external APIs.

```mermaid
graph TB
    subgraph "Frontend - Next.js"
        UI["Chat UI"]
        Auth["Auth Pages"]
        API_SVC["API Service<br/>(axios + fetch SSE)"]
    end

    subgraph "Backend - FastAPI"
        subgraph "API Layer"
            AUTH_R["Auth Router<br/>/auth/signup, /auth/signin"]
            CHAT_R["Chat Router<br/>/chat, /chat/session, /chat/profile"]
            DEPS["Dependencies<br/>(JWT validation, orchestrator singleton)"]
        end

        subgraph "Agent Layer"
            ORCH["AgentOrchestrator"]
            ROUTER["Router<br/>(Intent Classifier)"]
            TOOLS["Tool Suite"]
            REFLECT["ReflectionAgent<br/>(Safety Loop)"]
        end

        subgraph "Infrastructure"
            LLM["LLM Provider<br/>(ChatOpenAI via OpenRouter)"]
            EMB["Embeddings<br/>(Dense + Sparse)"]
            OBSERVABILITY["Langfuse<br/>(Tracing & Metrics)"]
            CONFIG["Config Manager<br/>(YAML + .env)"]
        end

        subgraph "Data Layer"
            QDRANT["Qdrant Vector DB"]
            POSTGRESQL["PostgreSQL<br/>(Users, Sessions, Messages)"]
            SEM_MEM["Semantic Memory<br/>(profiles.json)"]
            ST_MEM["Short-Term Memory<br/>(in-memory buffer)"]
        end
    end

    subgraph "External"
        LLM_API["OpenRouter / OpenAI API"]
        KAPRUKA["Kapruka.com<br/>(Web Crawler Source)"]
    end

    UI --> API_SVC
    Auth --> API_SVC
    API_SVC -->|"HTTP/SSE"| AUTH_R
    API_SVC -->|"HTTP/SSE"| CHAT_R
    CHAT_R --> DEPS
    DEPS --> ORCH
    ORCH --> ROUTER
    ORCH --> TOOLS
    ORCH --> REFLECT
    ROUTER --> LLM
    TOOLS --> LLM
    TOOLS --> QDRANT
    REFLECT --> LLM
    REFLECT --> SEM_MEM
    LLM --> LLM_API
    EMB --> LLM_API
    ORCH -.->|"Traces"| OBSERVABILITY
    CHAT_R --> POSTGRESQL
    ORCH --> SEM_MEM
    ORCH --> ST_MEM
    KAPRUKA -.->|"Playwright Crawl"| QDRANT
```

---

## 2. Multi-Agent Orchestration Flow

The core `AgentOrchestrator.chat()` method implements a **route → parallel execute → reflect** pipeline.

```mermaid
flowchart TD
    START(["User Query Arrives"]) --> ROUTE

    subgraph "Phase 1: Routing"
        ROUTE["Router.route()<br/>LLM classifies intent via<br/>structured output → RouterDecision"]
    end

    ROUTE --> DECISION{{"RouterDecision<br/>Flags"}}

    DECISION -->|"direct_chat = true"| DC_PATH
    DECISION -->|"direct_chat = false"| TOOL_PATH

    subgraph "Path A: Direct Chat"
        DC_PATH["DirectChatTool.chat()<br/>Small talk handler with<br/>chat history context"]
        DC_PATH --> DC_RETURN["Return response directly<br/>(no reflection needed)"]
    end

    subgraph "Path B: Tool Execution (ThreadPoolExecutor)"
        TOOL_PATH --> PARALLEL{{"Parallel Dispatch<br/>(concurrent.futures)"}}
        
        PARALLEL -->|"update_profile = true"| PREF["PreferenceUpdateTool<br/>Extract & merge recipient<br/>profile into semantic memory"]
        PARALLEL -->|"search_catalog = true"| CAT["CatalogSearchTool<br/>Hybrid search (dense + sparse)<br/>via Qdrant RRF fusion"]
        PARALLEL -->|"check_logistics = true"| LOG["LogisticsTool<br/>LLM evaluates delivery<br/>feasibility to target district"]
    end

    PREF --> COLLECT["Collect Results"]
    CAT --> COLLECT
    LOG --> COLLECT

    COLLECT --> REFLECT_LOOP

    subgraph "Phase 3: Reflection Loop"
        REFLECT_LOOP["ReflectionAgent.run()<br/>max_iterations = 3"]
        REFLECT_LOOP --> DRAFT["Draft Chain<br/>Synthesize tool results +<br/>profile + history → recommendation"]
        DRAFT --> CRITIQUE["Reflection Chain<br/>Check draft against allergies<br/>& restrictions → ReflectionCritique"]
        CRITIQUE --> SAFE{{"is_safe?"}}
        SAFE -->|"Yes"| FINAL["Return Final Draft"]
        SAFE -->|"No (violations found)"| REVISE["Revision Chain<br/>Fix violations while keeping<br/>warm, personalized tone"]
        REVISE --> CRITIQUE
    end

    DC_RETURN --> MEMORY["Save to Short-Term Memory"]
    FINAL --> MEMORY
    MEMORY --> END(["Response Sent to User"])
```

### Key Design Decisions

- **Parallel tool execution**: Profile update, catalog search, and logistics check run simultaneously in a `ThreadPoolExecutor`, reducing latency when multiple tools are needed.
- **Mutual exclusion**: `direct_chat` is mutually exclusive with catalog/logistics tools — if the user is just chatting, no heavy tools are invoked.
- **Profile update is fire-and-forget**: It runs in parallel but its result isn't used in the current response — it updates semantic memory for *future* queries.

---

## 3. Router Decision Logic

The Router is the **brain** of the system — an LLM-powered intent classifier that outputs structured JSON via `with_structured_output(RouterDecision)`.

```mermaid
flowchart LR
    INPUT["User Query +<br/>Semantic Profile +<br/>Chat History"]
    
    INPUT --> LLM_CALL["LLM with Structured Output<br/>(RouterDecision schema)"]
    
    LLM_CALL --> OUTPUT

    subgraph OUTPUT ["RouterDecision - Pydantic Schema"]
        direction TB
        F1["update_profile: bool<br/><i>New preferences/allergies?</i>"]
        F2["search_catalog: bool<br/><i>Wants gifts/recommendations?</i>"]
        F3["check_logistics: bool<br/><i>Delivery question?</i>"]
        F4["direct_chat: bool<br/><i>Small talk only?</i>"]
        F5["target_location: str | null<br/><i>District/City for logistics</i>"]
        F6["vector_query: str<br/><i>Semantic search query</i>"]
        F7["keyword_query: str<br/><i>BM25 keyword query</i>"]
    end
```

### Router Prompt Intelligence

The router prompt contains sophisticated instructions:
- **vector_query**: Enriched with recipient's preferences for semantic relevance
- **keyword_query**: Compressed keywords that *exclude* "gifts" and *exclude* recipient's allergies (pre-filtering unsafe items at search time)
- **Mutual exclusion**: When `direct_chat = true`, other flags are generally `false`

---

## 4. Reflection Safety Loop (Detailed)

The ReflectionAgent implements a **critique-and-revise loop** — a key safety mechanism that ensures no allergy-violating recommendations reach the user.

```mermaid
flowchart TD
    START(["Tool Results + User Query"]) --> FETCH_PROFILE["Fetch Recipient Profile<br/>from Semantic Memory"]
    
    FETCH_PROFILE --> DRAFT_CHAIN

    subgraph "Iteration Loop - max 3 iterations"
        DRAFT_CHAIN["Draft Chain<br/><b>draft_system_prompt</b><br/>Synthesize catalog results,<br/>logistics data, profile, history<br/>into warm recommendation"]
        
        DRAFT_CHAIN --> REFLECT_CHAIN["Reflection Chain<br/><b>reflection_system_prompt</b><br/>Review draft against<br/>recipient allergies/restrictions<br/>→ ReflectionCritique"]
        
        REFLECT_CHAIN --> CHECK{{"is_safe?"}}
        
        CHECK -->|"true"| RETURN["Return current draft"]
        CHECK -->|"false<br/>violations detected"| LOG_WARN["Log violations"]
        
        LOG_WARN --> REVISE_CHAIN["Revision Chain<br/><b>revision_system_prompt</b><br/>Fix violations while<br/>maintaining tone<br/>(no mention of revision)"]
        
        REVISE_CHAIN -->|"Loop back"| REFLECT_CHAIN
    end
    
    RETURN --> END(["Final Safe Response"])
```

### Three Distinct LLM Chains in the Loop

| Chain | Prompt | Input | Output |
|---|---|---|---|
| **Draft** | `draft_system_prompt` + `draft_user_prompt` | query, tool_results, profile, chat history | Natural language recommendation |
| **Reflection** | `reflection_system_prompt` + `reflection_user_prompt` | proposed recommendation, profile | `ReflectionCritique` (is_safe, violations) |
| **Revision** | `revision_system_prompt` + `revision_user_prompt` | current draft, violation list | Revised recommendation |

---

## 5. Memory Architecture

The system uses a **dual-memory architecture** — long-term semantic memory for user profiles and short-term buffer memory for conversation context.

```mermaid
flowchart LR
    subgraph "Short-Term Memory - Per Session"
        STM["ShortTermMemoryManager<br/><i>In-memory list buffer</i>"]
        STM_DATA["Messages array:<br/>role + content pairs<br/>Rebuilt from DB on each request"]
    end

    subgraph "Semantic Memory - Persistent"
        SEM["SemanticMemoryManager<br/><i>JSON file: profiles.json</i>"]
        SEM_DATA["user_id → <br/>  recipient_name:<br/>    preferences: list<br/>    allergies: list"]
    end

    subgraph "Relational DB - Persistent"
        SQL["PostgreSQL via SQLAlchemy"]
        USERS["Users Table"]
        SESSIONS["ChatSessions Table"]
        MSGS["Messages Table"]
    end

    STM --> STM_DATA
    SEM --> SEM_DATA

    SQL --> USERS
    SQL --> SESSIONS
    SQL --> MSGS

    MSGS -->|"Loaded into"| STM
    STM_DATA -->|"Used by"| ROUTER_USE["Router, DirectChat,<br/>Draft Chain"]
    SEM_DATA -->|"Used by"| REFLECT_USE["Router, Reflection,<br/>Draft Chain,<br/>PreferenceUpdate"]
```

### Memory Flow Per Request

1. **Load**: Previous messages for the session are loaded from PostgreSQL → `ShortTermMemoryManager`
2. **Use**: Router and tools read from both memory types
3. **Update**: After response, new user/assistant messages are added to both short-term buffer and PostgreSQL
4. **Profile Update**: `PreferenceUpdateTool` may asynchronously update semantic memory (profiles.json)

---

## 6. Hybrid RAG Pipeline

The system implements a **Hybrid Retrieval-Augmented Generation (RAG)** pipeline. Unlike monolithic RAG systems, the retrieval and generation phases are distributed across two separate agent components, connected through the orchestrator.

```mermaid
flowchart LR
    subgraph "R — Retrieval (CatalogSearchTool)"
        Q["Router-optimized queries"] --> D["Dense Search<br/>(Semantic Embeddings)"]
        Q --> S["Sparse Search<br/>(BM25 Keywords)"]
        D --> RRF["RRF Fusion"]
        S --> RRF
        RRF --> PRODUCTS["Top-K Products<br/>(title, price, description, url)"]
    end

    subgraph "A+G — Augmentation & Generation (Draft Chain)"
        PRODUCTS --> CONTEXT["Augmented Context:<br/>• Retrieved products<br/>• Recipient profile<br/>• Chat history<br/>• Logistics results"]
        CONTEXT --> LLM["LLM (GPT-4o-mini)<br/>Generates personalized<br/>gift recommendation"]
        LLM --> OUTPUT["Natural language<br/>recommendation with<br/>product links"]
    end
```

### RAG Phase Mapping

| RAG Phase | Component | Implementation Details |
|---|---|---|
| **Retrieval** | `CatalogSearchTool` → Qdrant | Hybrid search combining dense (semantic cosine similarity) and sparse (BM25 keyword matching) via Reciprocal Rank Fusion. Returns top-5 products with title, description, price, URL, and availability. |
| **Augmentation** | `ReflectionAgent.run()` | The retrieved products are combined with the recipient's semantic profile (preferences/allergies), the session's chat history, and any logistics feasibility results into a rich, multi-source context. |
| **Generation** | Draft Chain (LLM) | The LLM (GPT-4o-mini) synthesizes the augmented context into a warm, personalized gift recommendation. The response includes real product URLs — the LLM never hallucinate product names or prices because it is grounded in retrieved catalog data. |

---

## 7. Hybrid Search Architecture (Qdrant)

The catalog search uses **Reciprocal Rank Fusion (RRF)** to combine dense semantic search with sparse keyword (BM25) search.

```mermaid
flowchart TD
    QUERY["Router generates:<br/>• vector_query - semantic<br/>• keyword_query - BM25"]

    QUERY --> DENSE_EMB["Dense Embedding<br/>OpenAI text-embedding-3-small<br/>(1536 dimensions)"]
    QUERY --> SPARSE_EMB["Sparse Embedding<br/>FastEmbed BM25<br/>(Qdrant/bm25 model)"]

    DENSE_EMB --> PREFETCH_D["Prefetch: Dense Search<br/>Top 20 by cosine similarity"]
    SPARSE_EMB --> PREFETCH_S["Prefetch: Sparse Search<br/>Top 20 by BM25 score"]

    PREFETCH_D --> RRF["Reciprocal Rank Fusion<br/>RRF Merge"]
    PREFETCH_S --> RRF

    RRF --> TOP_K["Return Top 5 Products"]
    TOP_K --> RESULTS["title, description,<br/>price, url, availability"]
```

### Why Hybrid Search?

| Search Type | Strength | Weakness |
|---|---|---|
| **Dense (Semantic)** | Understands meaning, synonyms, intent | May miss exact keyword matches |
| **Sparse (BM25)** | Exact keyword matching, product names | Misses semantic similarity |
| **Hybrid (RRF)** | Best of both worlds | Slightly more compute |

The `keyword_query` is intelligently crafted by the Router to **exclude allergens** and **exclude the word "gifts"** (which would dilute search results), while the `vector_query` is enriched with recipient preferences for personalized semantic matching.

---

## 8. Data Ingestion Pipeline

The pipeline scrapes product data from Kapruka.com, generates dual embeddings, and indexes everything into Qdrant.

```mermaid
flowchart LR
    subgraph "Phase 1: Web Crawling"
        CRAWLER["KaprukaWebCrawler<br/>(Playwright, headless)"]
        CATEGORIES["Scrape category URLs<br/>from kapruka.com"]
        PRODUCTS["Scrape each product:<br/>title, price, description,<br/>availability, URL"]
        CF["Cloudflare bypass<br/>(wait + retry)"]
        JSON_SAVE["Save to catalog.json"]
    end

    subgraph "Phase 2: Ingestion Pipeline"
        LOAD["Load catalog.json"]
        CHUNK["Build text chunks<br/>(title + description + price)"]
        DENSE["Generate dense embeddings<br/>(OpenAI, batched)"]
        SPARSE["Generate sparse embeddings<br/>(BM25)"]
        UPSERT["Upsert to Qdrant<br/>(dual-vector points)"]
    end

    CRAWLER --> CATEGORIES --> PRODUCTS --> CF --> JSON_SAVE
    JSON_SAVE -.-> LOAD --> CHUNK --> DENSE --> UPSERT
    CHUNK --> SPARSE --> UPSERT
```

### Each Qdrant Point Contains

| Field | Type | Description |
|---|---|---|
| **Dense vector** | `float[1536]` | Semantic representation of product text |
| **Sparse vector** | BM25 | Keyword-based representation |
| **Payload: title** | `string` | Product name |
| **Payload: description** | `string` | Product description |
| **Payload: price** | `string` | Product price |
| **Payload: url** | `string` | Product page URL on Kapruka.com |
| **Payload: availability** | `bool` | Whether the product is in stock |

---

## 9. Class & Component Interaction Map

```mermaid
classDiagram
    class AgentOrchestrator {
        +llm: ChatOpenAI
        +semantic_memory: SemanticMemoryManager
        +router: Router
        +preference_tool: PreferenceUpdateTool
        +catalog_tool: CatalogSearchTool
        +logistics_tool: LogisticsTool
        +direct_chat_tool: DirectChatTool
        +reflection_agent: ReflectionAgent
        +chat(user_id, query, st_memory, callback) str
    }

    class Router {
        +llm: ChatOpenAI
        +semantic_memory: SemanticMemoryManager
        +route(query, st_memory, user_id) RouterDecision
    }

    class ReflectionAgent {
        +llm: ChatOpenAI
        +semantic_memory: SemanticMemoryManager
        +draft_prompt: ChatPromptTemplate
        +reflection_prompt: ChatPromptTemplate
        +revision_prompt: ChatPromptTemplate
        +run(query, results, user_id, st_memory) str
    }

    class CatalogSearchTool {
        +search(vector_query, keyword_query) List
    }

    class DirectChatTool {
        +llm: ChatOpenAI
        +chat(query, st_memory) str
    }

    class LogisticsTool {
        +llm: ChatOpenAI
        +check_delivery_feasibility(location, query) LogisticsFeasibility
    }

    class PreferenceUpdateTool {
        +llm: ChatOpenAI
        +semantic_memory: SemanticMemoryManager
        +update_semantic_memory(user_id, msg) void
    }

    class RouterDecision {
        +update_profile: bool
        +search_catalog: bool
        +check_logistics: bool
        +direct_chat: bool
        +target_location: str?
        +vector_query: str
        +keyword_query: str
    }

    class ReflectionCritique {
        +is_safe: bool
        +violations: str
    }

    class LogisticsFeasibility {
        +deliverable: bool
        +reason: str
    }

    class SemanticMemoryManager {
        +file_path: str
        +get_profile(user_id) dict
        +save_profile(user_id, data) void
    }

    class ShortTermMemoryManager {
        +buffer: list
        +add_message(role, content) void
        +get_history() str
        +get_raw_history() list
    }

    AgentOrchestrator --> Router
    AgentOrchestrator --> ReflectionAgent
    AgentOrchestrator --> CatalogSearchTool
    AgentOrchestrator --> DirectChatTool
    AgentOrchestrator --> LogisticsTool
    AgentOrchestrator --> PreferenceUpdateTool
    AgentOrchestrator --> SemanticMemoryManager
    AgentOrchestrator --> ShortTermMemoryManager

    Router ..> RouterDecision : produces
    ReflectionAgent ..> ReflectionCritique : uses
    LogisticsTool ..> LogisticsFeasibility : produces

    Router --> SemanticMemoryManager
    ReflectionAgent --> SemanticMemoryManager
    PreferenceUpdateTool --> SemanticMemoryManager
```

---

## 10. Full Request Lifecycle (End-to-End)

The complete journey of a single user message through every layer of the system.

```mermaid
flowchart TD
    A["User types message in chat UI"] --> B["Frontend sends POST /chat<br/>with JWT + session_id"]
    B --> C["FastAPI validates JWT,<br/>loads session from PostgreSQL"]
    C --> D["Load message history<br/>into ShortTermMemoryManager"]
    D --> E["Start background thread<br/>with AgentOrchestrator.chat()"]
    E --> F["Router classifies intent<br/>(LLM structured output)"]
    F --> G{{"Route Decision"}}
    
    G -->|"Small Talk"| H["DirectChatTool<br/>(LLM chat with history)"]
    G -->|"Gift Query"| I["Parallel Execution"]
    
    I --> I1["PreferenceUpdate<br/>(if new prefs)"]
    I --> I2["CatalogSearch<br/>(hybrid Qdrant)"]
    I --> I3["LogisticsCheck<br/>(if location mentioned)"]
    
    I1 --> J["Collect results"]
    I2 --> J
    I3 --> J
    
    J --> K["ReflectionAgent loops:<br/>Draft → Critique → Revise"]
    
    H --> L["Save to memory + DB"]
    K --> L
    
    L --> M["Stream final response<br/>via SSE to frontend"]
    M --> N["UI renders markdown<br/>response with product links"]
```

---

## 11. Technology Stack Breakdown

```mermaid
graph LR
    subgraph "Frontend Stack"
        NEXT["Next.js"]
        REACT["React"]
        TAILWIND["TailwindCSS"]
        SHADCN["shadcn/ui"]
        AXIOS["Axios"]
        FETCH["Fetch API - SSE"]
    end

    subgraph "Backend Stack"
        FASTAPI["FastAPI"]
        SQLA["SQLAlchemy"]
        PYDANTIC["Pydantic"]
        LANGCHAIN["LangChain"]
        LANGFUSE["Langfuse - Tracing"]
        JOSE["python-jose - JWT"]
        BCRYPT["bcrypt"]
    end

    subgraph "AI/ML Stack"
        OPENAI_LLM["GPT-4o-mini - Chat"]
        OPENAI_EMB["text-embedding-3-small - Dense"]
        BM25["FastEmbed BM25 - Sparse"]
        QDRANT_DB["Qdrant - Vector DB"]
    end

    subgraph "Data Pipeline"
        PLAYWRIGHT["Playwright - Crawler"]
        POSTGRES["PostgreSQL - User Data"]
        JSON_FILES["JSON - Profiles + Catalog"]
    end
```

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js + React | Server-side rendered chat UI |
| **Styling** | TailwindCSS + shadcn/ui | Utility-first CSS with accessible components |
| **HTTP Client** | Axios + Fetch API | REST calls + SSE streaming |
| **Backend API** | FastAPI | Async Python web framework |
| **ORM** | SQLAlchemy | Database abstraction for PostgreSQL |
| **Validation** | Pydantic | Request/response schema validation |
| **Auth** | python-jose + bcrypt | JWT tokens + password hashing |
| **Agent Framework** | LangChain | Prompt templates, chains, structured output |
| **Observability** | Langfuse | End-to-end tracing of agent and LLM execution |
| **Chat LLM** | GPT-4o-mini (OpenRouter) | Intent classification, chat, recommendations |
| **Dense Embeddings** | text-embedding-3-small | 1536-dim semantic vectors |
| **Sparse Embeddings** | FastEmbed BM25 | Keyword-based sparse vectors |
| **Vector Database** | Qdrant (local) | Hybrid search with RRF fusion |
| **Relational DB** | PostgreSQL | User accounts, sessions, message persistence |
| **Web Scraping** | Playwright | Automated Kapruka.com product crawling |
