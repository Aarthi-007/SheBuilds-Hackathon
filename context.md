# Klyro — Agentic Brand Intelligence Platform
## context.md — Single Source of Truth for Implementation

> Audience: an AI coding agent (Claude Code, Cursor, Codex, Gemini CLI). This file is the only reference. No other document exists. Build the entire system from this file.

---

## 1. PROJECT OVERVIEW

**Name:** Klyro

**Problem:** Companies produce huge volumes of AI-generated content (web copy, ads, blogs, social posts, video, docs). Existing tools check plagiarism, grammar, compliance, or moderation in isolation. None understand a company's brand identity, track its drift over time, benchmark it against competitors, predict content performance, optimize content while preserving identity, and validate compliance before publishing — all in one agentic pipeline.

**Goal:** Build a fully agentic platform that learns a company's brand identity from all available assets, then continuously protects, analyzes, optimizes, and evolves that identity.

---

## 2. TECH STACK

**Frontend**
- React.js + Vite
- TypeScript
- TailwindCSS
- shadcn/ui
- React Router
- Axios
- Recharts
- Framer Motion

**Backend**
- FastAPI (Python 3.11+)
- Uvicorn (ASGI server)
- Pydantic v2 (schema validation)
- APScheduler (background/cron jobs — trend refresh, drift re-scan, continuous learning)

**AI Framework**
- LangChain (agent tool orchestration, retrievers)
- Custom Python Orchestrator (not LangGraph — a hand-rolled state machine, see §6)

**LLMs**
- Claude Sonnet — all reasoning, semantic understanding, planning, intent/sentiment/emotion detection, audience detection, brand-value extraction, tone/messaging analysis, competitor reasoning, trend reasoning, prediction reasoning, optimization, explainability, report generation.
- Groq Vision Model — universal multimodal perception only. Input: text/image/video. Output: structured JSON. No other agent touches raw images/video.

**Embeddings**
- `BAAI/bge-m3` — runs only on the structured text Groq/Claude produce, never on raw media.

**Databases**
- MongoDB Atlas — system of record
- Pinecone — vector similarity (identity, competitor, campaign embeddings)

**External Services**
- Tavily — web search (trends, competitor discovery)
- Playwright — dynamic web scraping (JS-rendered competitor sites/social)
- BeautifulSoup — static HTML parsing

---

## 3. SYSTEM ARCHITECTURE

```
User
  ↓
React Frontend
  ↓
FastAPI Backend
  ↓
Orchestrator Agent
  ↓
Multimodal Perception Agent (Groq)
  ↓
Structured Universal Content (UniversalContent schema)
  ↓
Brand Identity Agent
  ↓
Identity Drift Agent
  ↓
Trend Intelligence Agent
  ↓
Predictive Intelligence Agent
  ↓
Autonomous Optimization Agent
  ↓
Compliance Agent
  ↓
Copyright/IP Agent
  ↓
Safety Agent
  ↓
Continuous Learning Agent
  ↓
MongoDB + Pinecone
```

The Orchestrator does not always run every agent linearly — it plans a DAG per request type (see §6.2). The diagram above is the default "full ingest" path.

### 3.1 Multimodal Perception Pipeline

```
Text / Image / Video
  ↓
Groq (perception) → Structured JSON
  ↓
Claude (semantic understanding) → enriched structured object
  ↓
Flatten JSON → plain text representation
  ↓
BGE-M3 embeddings
  ↓
Pinecone upsert
  ↓
Remaining agents consume UniversalContent + embeddings
```

Rule: **every** input, regardless of modality, must be converted into a `UniversalContent` object before any downstream agent sees it.

---

## 4. FOLDER STRUCTURE

```
klyro/
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── routes/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ContentIngest.tsx
│   │   │   ├── BrandIdentity.tsx
│   │   │   ├── DriftReport.tsx
│   │   │   ├── Competitors.tsx
│   │   │   ├── Trends.tsx
│   │   │   ├── Predictions.tsx
│   │   │   ├── Optimize.tsx
│   │   │   ├── Compliance.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn/ui primitives
│   │   │   ├── charts/
│   │   │   │   ├── DriftScoreChart.tsx
│   │   │   │   ├── PredictionChart.tsx
│   │   │   │   └── CompetitorRadar.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Topbar.tsx
│   │   │   └── forms/
│   │   │       └── ContentUploadForm.tsx
│   │   ├── lib/
│   │   │   ├── api.ts               # axios instance
│   │   │   └── types.ts             # TS mirrors of Pydantic schemas
│   │   ├── hooks/
│   │   │   └── useContentIngest.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/
│   ├── main.py                       # FastAPI app entrypoint
│   ├── config/
│   │   ├── settings.py               # Pydantic BaseSettings, reads .env
│   │   └── constants.py
│   ├── routes/
│   │   ├── content_routes.py
│   │   ├── brand_routes.py
│   │   ├── drift_routes.py
│   │   ├── competitor_routes.py
│   │   ├── trend_routes.py
│   │   ├── prediction_routes.py
│   │   ├── optimization_routes.py
│   │   ├── compliance_routes.py
│   │   └── report_routes.py
│   ├── orchestrator/
│   │   ├── orchestrator_agent.py
│   │   ├── planner.py
│   │   ├── task_graph.py
│   │   └── retry_policy.py
│   ├── agents/
│   │   ├── base_agent.py             # abstract Agent, defines run()
│   │   ├── perception_agent.py
│   │   ├── brand_identity_agent.py
│   │   ├── identity_drift_agent.py
│   │   ├── trend_intelligence_agent.py
│   │   ├── predictive_intelligence_agent.py
│   │   ├── optimization_agent.py
│   │   ├── compliance_agent.py
│   │   ├── copyright_agent.py
│   │   ├── safety_agent.py
│   │   └── continuous_learning_agent.py
│   ├── services/
│   │   ├── claude_service.py
│   │   ├── groq_service.py
│   │   ├── embedding_service.py
│   │   ├── pinecone_service.py
│   │   ├── mongo_service.py
│   │   ├── tavily_service.py
│   │   ├── scraper_service.py
│   │   ├── scoring_service.py
│   │   └── report_service.py
│   ├── schemas/
│   │   ├── universal_content.py
│   │   ├── brand_identity.py
│   │   ├── competitor_profile.py
│   │   ├── trend_knowledge.py
│   │   ├── campaign_memory.py
│   │   ├── drift_report.py
│   │   ├── prediction_report.py
│   │   ├── optimization_report.py
│   │   ├── compliance_report.py
│   │   ├── safety_report.py
│   │   ├── copyright_report.py
│   │   ├── agent_message.py
│   │   └── api_models.py             # request/response wrappers
│   ├── repositories/
│   │   ├── content_repository.py
│   │   ├── brand_repository.py
│   │   ├── competitor_repository.py
│   │   ├── trend_repository.py
│   │   ├── campaign_repository.py
│   │   └── report_repository.py
│   ├── database/
│   │   ├── mongo_client.py
│   │   └── pinecone_client.py
│   ├── prompts/
│   │   ├── brand_identity_extraction.md
│   │   ├── identity_drift_explanation.md
│   │   ├── competitor_industry_detection.md
│   │   ├── trend_reasoning.md
│   │   ├── prediction_reasoning.md
│   │   ├── optimization_rewrite.md
│   │   ├── compliance_check.md
│   │   ├── copyright_check.md
│   │   └── safety_check.md
│   ├── utils/
│   │   ├── json_flatten.py
│   │   ├── text_cleaning.py
│   │   ├── retry.py
│   │   └── logger.py
│   └── tests/
│       ├── test_agents/
│       ├── test_services/
│       ├── test_routes/
│       └── test_schemas/
│
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## 5. ENVIRONMENT VARIABLES

```
# LLMs
ANTHROPIC_API_KEY=
GROQ_API_KEY=

# Embeddings
HUGGINGFACE_API_KEY=          # if using hosted BGE-M3, else blank for local model

# Databases
MONGODB_URI=
MONGODB_DB_NAME=klyro

PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
PINECONE_INDEX_BRAND=klyro-brand-identity
PINECONE_INDEX_COMPETITOR=klyro-competitors
PINECONE_INDEX_CAMPAIGN=klyro-campaigns

# Search / Scraping
TAVILY_API_KEY=
PLAYWRIGHT_HEADLESS=true

# App config
APP_ENV=development
APP_PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
JWT_SECRET=
LOG_LEVEL=INFO
```

---

## 6. ORCHESTRATOR AGENT

File: `backend/orchestrator/orchestrator_agent.py`

Responsibilities: planning, routing, workflow execution, retries, reflection, inter-agent communication.

### 6.1 Class shape

```python
class OrchestratorAgent:
    def __init__(self, agents: dict[str, BaseAgent]): ...
    async def run(self, request: OrchestratorRequest) -> OrchestratorResult: ...
    def _plan(self, request: OrchestratorRequest) -> TaskGraph: ...
    async def _execute_graph(self, graph: TaskGraph) -> dict: ...
    async def _retry(self, agent: BaseAgent, payload, max_attempts=3): ...
    def _reflect(self, results: dict) -> ReflectionNotes: ...
```

### 6.2 Task graphs (workflow types)

- `full_ingest`: perception → brand_identity → drift → trend → prediction → optimization → compliance → copyright → safety → continuous_learning
- `quick_drift_check`: perception → drift (uses existing Brand Identity Model, no re-learning)
- `optimize_only`: optimization → compliance → safety
- `competitor_scan`: trend (competitor discovery) → brand_identity (competitor profile build) → continuous_learning

`TaskGraph` (in `task_graph.py`) is a list of `TaskNode(agent_name, depends_on: list[str])`. The Orchestrator executes nodes whose dependencies are satisfied, in parallel where possible (e.g., compliance/copyright/safety can run concurrently after optimization).

### 6.3 Communication contract

Agents never call each other directly. All inter-agent data passes through `AgentMessage` (schemas/agent_message.py):

```python
class AgentMessage(BaseModel):
    from_agent: str
    to_agent: str
    payload: dict
    trace_id: str
    timestamp: datetime
```

---

## 7. AGENT SPECIFICATIONS

Every agent inherits `BaseAgent` (`backend/agents/base_agent.py`):

```python
class BaseAgent(ABC):
    name: str
    async def run(self, input_data: BaseModel) -> BaseModel: ...
```

One public method: `run()`. All internal helper methods are private (`_method`).

### 7.1 Multimodal Perception Agent
File: `perception_agent.py`
- Input: raw text / image bytes / video bytes + `content_type`
- Calls `GroqService.perceive(content, content_type)` → raw JSON
- Calls `ClaudeService.enrich_perception(raw_json)` → semantic layer (intent, sentiment, emotion, audience)
- Output: `UniversalContent`

### 7.2 Brand Identity Intelligence Agent
File: `brand_identity_agent.py`
- Learns: tone, values, personality, messaging, audience, visual identity, competitors, historical campaigns.
- Uses `ClaudeService.extract_brand_identity(prompt="brand_identity_extraction.md", content_batch)`.
- Detects industry via Claude (`competitor_industry_detection.md`) — output feeds Trend Agent's competitor discovery.
- Persists/updates `BrandIdentityModel` via `brand_repository.py`.
- Upserts identity embedding to Pinecone index `klyro-brand-identity`, namespace = `company_id`.

### 7.3 Identity Drift Intelligence Agent
File: `identity_drift_agent.py`
- Compares new content against: Brand Identity Model, historical campaigns, competitor knowledge.
- Uses `PineconeService.query(index=klyro-brand-identity, namespace=company_id)` for brand similarity.
- Uses `PineconeService.query(index=klyro-competitors)` for competitor similarity.
- Computes: drift_score, brand_similarity, competitor_similarity, distinctiveness_score via `ScoringService`.
- Claude generates explanation + recommendations (`identity_drift_explanation.md`).
- Output: `DriftReport`.

### 7.4 Trend Intelligence Agent
File: `trend_intelligence_agent.py`
- Uses `TavilyService.search()` for industry trends, emerging topics, competitor campaigns, trending hashtags, seasonal events.
- Uses `ScraperService` (Playwright + BeautifulSoup) to pull competitor site/campaign content.
- Categorizes competitors: Primary / Secondary / Emerging (Claude reasoning, `trend_reasoning.md`).
- Persists `CompetitorProfile` per competitor (`competitor_repository.py`), embeds to Pinecone `klyro-competitors`.
- Output: `TrendKnowledge`.

### 7.5 Predictive Intelligence Agent
File: `predictive_intelligence_agent.py`
- Predicts engagement, reach, CTR, virality.
- Uses Claude reasoning (`prediction_reasoning.md`) combined with `ScoringService` heuristics (historical campaign performance, trend alignment, drift score as input features).
- Output: `PredictionReport`.

### 7.6 Autonomous Optimization Agent
File: `optimization_agent.py`
- Rewrites/improves captions, blogs, ads, prompts, content — while preserving Brand Identity Model.
- Uses Claude (`optimization_rewrite.md`) with Brand Identity Model + Drift Report + Prediction Report as context.
- Output: `OptimizationReport` (original, optimized, diff explanation, preserved-identity checklist).

### 7.7 Compliance Agent
File: `compliance_agent.py`
- Checks regulations, brand guidelines, platform policies (Claude, `compliance_check.md`).
- Output: `ComplianceReport`.

### 7.8 Copyright/IP Agent
File: `copyright_agent.py`
- Checks copyright, trademark, logo misuse, plagiarism.
- Uses Tavily for external similarity search + Claude reasoning (`copyright_check.md`).
- Output: `CopyrightReport`.

### 7.9 Safety Agent
File: `safety_agent.py`
- Checks toxicity, hate speech, misinformation, bias, appropriateness (Claude, `safety_check.md`).
- Output: `SafetyReport`.

### 7.10 Continuous Learning Agent
File: `continuous_learning_agent.py`
- After each full ingest, updates: Brand Identity Model, Competitor Knowledge, Trend Knowledge, Campaign Memory.
- Runs on a schedule too (APScheduler job, daily) to refresh Trend Knowledge and re-scan Competitor Profiles even without new content.

---

## 8. COMPETITOR DISCOVERY FLOW

1. Brand Identity Agent determines industry via Claude.
2. Trend Intelligence Agent calls Tavily with industry + company name to discover competitors.
3. Claude categorizes each into Primary / Secondary / Emerging.
4. Each competitor gets a `CompetitorProfile` document in MongoDB (`competitor_profiles` collection) and a vector in Pinecone `klyro-competitors` index, namespace = `company_id`, metadata `{competitor_id, tier, industry}`.
5. Identity Drift Agent always compares content against both the company's own Brand Identity Model AND all competitor profiles in that company's namespace.

---

## 9. PYDANTIC SCHEMAS

All in `backend/schemas/`. Use Pydantic v2 (`BaseModel`, `Field`).

```python
# universal_content.py
class UniversalContent(BaseModel):
    content_id: str
    company_id: str
    modality: Literal["text", "image", "video"]
    raw_reference: str              # storage path/URL of original asset
    structured_description: dict    # Groq output
    semantic_layer: dict            # Claude enrichment: intent, sentiment, emotion, audience
    flattened_text: str             # for embedding
    created_at: datetime

# brand_identity.py
class BrandIdentityModel(BaseModel):
    company_id: str
    industry: str
    tone: list[str]
    core_values: list[str]
    personality_traits: list[str]
    messaging_pillars: list[str]
    target_audience: dict
    visual_identity: dict           # colors, typography, logo usage rules
    historical_campaign_ids: list[str]
    version: int
    updated_at: datetime

# competitor_profile.py
class CompetitorProfile(BaseModel):
    competitor_id: str
    company_id: str                 # owning company this profile is tracked for
    name: str
    tier: Literal["primary", "secondary", "emerging"]
    industry: str
    tone: list[str]
    messaging_pillars: list[str]
    sample_content_refs: list[str]
    last_scanned_at: datetime

# trend_knowledge.py
class TrendKnowledge(BaseModel):
    company_id: str
    industry_trends: list[str]
    emerging_topics: list[str]
    competitor_campaigns: list[dict]
    trending_hashtags: list[str]
    seasonal_events: list[dict]
    fetched_at: datetime

# campaign_memory.py
class CampaignMemory(BaseModel):
    campaign_id: str
    company_id: str
    content_ids: list[str]
    performance_actuals: dict | None
    drift_report_id: str | None
    prediction_report_id: str | None
    created_at: datetime

# drift_report.py
class DriftReport(BaseModel):
    report_id: str
    content_id: str
    company_id: str
    drift_score: float
    brand_similarity: float
    competitor_similarity: dict[str, float]   # competitor_id -> score
    distinctiveness_score: float
    explanation: str
    recommendations: list[str]
    created_at: datetime

# prediction_report.py
class PredictionReport(BaseModel):
    report_id: str
    content_id: str
    predicted_engagement: float
    predicted_reach: float
    predicted_ctr: float
    predicted_virality: float
    reasoning: str
    created_at: datetime

# optimization_report.py
class OptimizationReport(BaseModel):
    report_id: str
    content_id: str
    original_text: str
    optimized_text: str
    diff_explanation: str
    identity_preserved: bool
    created_at: datetime

# compliance_report.py
class ComplianceReport(BaseModel):
    report_id: str
    content_id: str
    passed: bool
    violations: list[str]
    notes: str
    created_at: datetime

# safety_report.py
class SafetyReport(BaseModel):
    report_id: str
    content_id: str
    toxicity_flag: bool
    bias_flag: bool
    misinformation_flag: bool
    notes: str
    created_at: datetime

# copyright_report.py
class CopyrightReport(BaseModel):
    report_id: str
    content_id: str
    plagiarism_flag: bool
    trademark_conflicts: list[str]
    sources_matched: list[str]
    notes: str
    created_at: datetime

# agent_message.py
class AgentMessage(BaseModel):
    from_agent: str
    to_agent: str
    payload: dict
    trace_id: str
    timestamp: datetime

# api_models.py
class IngestContentRequest(BaseModel):
    company_id: str
    modality: Literal["text", "image", "video"]
    payload: str          # raw text or base64/URL depending on modality

class IngestContentResponse(BaseModel):
    content_id: str
    universal_content: UniversalContent
    drift_report: DriftReport | None = None
    prediction_report: PredictionReport | None = None
    optimization_report: OptimizationReport | None = None
    compliance_report: ComplianceReport | None = None
    safety_report: SafetyReport | None = None
    copyright_report: CopyrightReport | None = None
```

---

## 10. DATABASE — MongoDB Atlas

Database: `klyro`

| Collection | Key fields | Indexes | Notes |
|---|---|---|---|
| `universal_content` | `content_id` (PK), `company_id`, `modality`, `created_at` | `company_id`, `created_at` | one doc per ingested asset |
| `brand_identity_models` | `company_id` (PK), `version` | unique `company_id` | latest version per company; keep history in `brand_identity_history` |
| `brand_identity_history` | `company_id`, `version`, `snapshot` | `company_id + version` | append-only versioning |
| `competitor_profiles` | `competitor_id` (PK), `company_id`, `tier` | `company_id`, `tier` | one profile per competitor per tracked company |
| `trend_knowledge` | `company_id`, `fetched_at` | `company_id + fetched_at desc` | keep last N snapshots |
| `campaign_memory` | `campaign_id` (PK), `company_id` | `company_id`, `created_at` | groups related content_ids |
| `drift_reports` | `report_id` (PK), `content_id`, `company_id` | `content_id`, `company_id` | |
| `prediction_reports` | `report_id` (PK), `content_id` | `content_id` | |
| `optimization_reports` | `report_id` (PK), `content_id` | `content_id` | |
| `compliance_reports` | `report_id` (PK), `content_id` | `content_id` | |
| `safety_reports` | `report_id` (PK), `content_id` | `content_id` | |
| `copyright_reports` | `report_id` (PK), `content_id` | `content_id` | |
| `companies` | `company_id` (PK), `name`, `industry` | unique `company_id` | tenant root document |

Relationships: `universal_content.company_id → companies`, all report collections reference `content_id → universal_content`, `competitor_profiles.company_id → companies`.

---

## 11. VECTOR DATABASE — Pinecone

Three indexes (dimension = 1024 for `bge-m3`, metric = cosine):

- `klyro-brand-identity` — one vector per company's current Brand Identity Model (namespace = `company_id`). Metadata: `{company_id, version, updated_at}`.
- `klyro-competitors` — one vector per competitor profile (namespace = `company_id`). Metadata: `{competitor_id, tier, industry}`.
- `klyro-campaigns` — one vector per content item / campaign asset (namespace = `company_id`). Metadata: `{content_id, campaign_id, modality, created_at}`.

**Embedding workflow:** `flattened_text` from `UniversalContent` → `EmbeddingService.embed(text)` (bge-m3) → upsert to `klyro-campaigns`. Brand Identity and Competitor Profile text summaries are embedded the same way and upserted to their respective indexes whenever the underlying Mongo doc changes.

**Retrieval workflow:** `PineconeService.query(index, namespace, vector, top_k)` → returns matches with similarity scores → `ScoringService` converts scores into drift/similarity metrics.

---

## 12. API — FastAPI Routes

Base prefix: `/api/v1`

| Method | Path | Request model | Response model | Calls |
|---|---|---|---|---|
| POST | `/content/ingest` | `IngestContentRequest` | `IngestContentResponse` | Orchestrator (`full_ingest` graph) |
| GET | `/content/{content_id}` | — | `UniversalContent` | `content_repository` |
| GET | `/brand/{company_id}` | — | `BrandIdentityModel` | `brand_repository` |
| POST | `/brand/{company_id}/relearn` | — | `BrandIdentityModel` | Orchestrator (`competitor_scan` + brand relearn) |
| GET | `/drift/{content_id}` | — | `DriftReport` | `report_repository` |
| POST | `/drift/check` | `IngestContentRequest` | `DriftReport` | Orchestrator (`quick_drift_check`) |
| GET | `/competitors/{company_id}` | — | `list[CompetitorProfile]` | `competitor_repository` |
| POST | `/competitors/{company_id}/scan` | — | `list[CompetitorProfile]` | Orchestrator (`competitor_scan`) |
| GET | `/trends/{company_id}` | — | `TrendKnowledge` | `trend_repository` |
| POST | `/predict` | `IngestContentRequest` | `PredictionReport` | Predictive Agent |
| POST | `/optimize` | `IngestContentRequest` | `OptimizationReport` | Orchestrator (`optimize_only`) |
| GET | `/compliance/{content_id}` | — | `ComplianceReport` | `report_repository` |
| GET | `/reports/{content_id}` | — | `IngestContentResponse` (all reports) | `report_repository` |

Routes never call `ClaudeService`/`GroqService` directly — they only call the Orchestrator or a specific Agent's `run()`, or a repository for reads.

---

## 13. SERVICES

`backend/services/`

- **ClaudeService** — `generate(prompt, variables) -> str`, `generate_structured(prompt, variables, schema) -> BaseModel`, `extract_brand_identity(...)`, `enrich_perception(...)`. Wraps Anthropic SDK, loads prompt Markdown files from `prompts/`.
- **GroqService** — `perceive(content, content_type) -> dict`. Wraps Groq vision API.
- **EmbeddingService** — `embed(text: str) -> list[float]`. Wraps BAAI/bge-m3.
- **PineconeService** — `upsert(index, namespace, id, vector, metadata)`, `query(index, namespace, vector, top_k)`.
- **MongoService** — thin wrapper around Motor/PyMongo client; used only by repositories, never by agents directly.
- **TavilyService** — `search(query, max_results) -> list[dict]`.
- **ScraperService** — `scrape_static(url) -> str` (BeautifulSoup), `scrape_dynamic(url) -> str` (Playwright).
- **ScoringService** — `compute_drift_score(...)`, `compute_similarity(...)`, `compute_prediction_features(...)`.
- **ReportService** — assembles/persists final report bundles, calls `report_repository`.

---

## 14. PROMPT FILES

All in `backend/prompts/`, plain Markdown, loaded and templated (Jinja-style `{{variable}}`) by `ClaudeService`.

- `brand_identity_extraction.md` — instructs Claude to extract tone, values, personality, messaging pillars, audience, visual identity from a batch of `UniversalContent`; must output JSON matching `BrandIdentityModel`.
- `identity_drift_explanation.md` — given drift/similarity scores, produce human-readable explanation + actionable recommendations.
- `competitor_industry_detection.md` — given company description/content samples, output industry label + confidence.
- `trend_reasoning.md` — given raw Tavily results, categorize competitors (primary/secondary/emerging) and summarize trends.
- `prediction_reasoning.md` — given content + historical performance + trend alignment, reason about predicted engagement/reach/CTR/virality with justification.
- `optimization_rewrite.md` — given content + Brand Identity Model + drift/prediction context, rewrite content to improve performance while preserving identity; must list what was preserved.
- `compliance_check.md` — given content + jurisdiction/platform context, check against regulations/guidelines/platform policy, output pass/fail + violations.
- `copyright_check.md` — given content + Tavily similarity search results, assess plagiarism/trademark/logo-misuse risk.
- `safety_check.md` — given content, flag toxicity, hate speech, misinformation, bias, appropriateness.

---

## 15. PROJECT RULES

1. Never call Claude or Groq directly from route handlers — only via Agents/Orchestrator through Services.
2. Every LLM output must be validated against a Pydantic model before being persisted or returned.
3. Every agent exposes exactly one public method: `run()`.
4. Agents communicate only through typed models (`AgentMessage`, or the specific report/schema types) — never raw dicts across agent boundaries.
5. Prompts are stored as Markdown files in `backend/prompts/`, never inlined as Python strings.
6. Database access happens only through repository classes (`backend/repositories/`) — services and agents never import `mongo_client` or `pinecone_client` directly.
7. Pinecone access happens only through `PineconeService`.
8. Never duplicate business logic between agents and services — scoring/formatting logic lives in `ScoringService`/`ReportService`, not copy-pasted into agents.
9. All timestamps stored in UTC.
10. All IDs are UUIDv4 strings generated at creation time, never database-assigned.
