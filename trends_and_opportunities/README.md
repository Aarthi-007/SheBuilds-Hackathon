# Trends & Opportunities Layer

Implements the flow from the note:

```
Keep tracking trends using News API
        ↓
Trend seems similar (similarity search) → pass to Claude
        ↓
Claude judges: is this a good opportunity?
        ↓
Claude recommends campaigns accordingly
```

## How it works

1. **Track** — `NewsService.fetch_trending()` pulls recent articles for a company's
   industry keywords. Runs every 6 hours per company via `orchestrator/scheduler.py`
   (an APScheduler job, same pattern as the Continuous Learning Agent's daily refresh
   in context.md §7.10).
2. **Match** — each article is embedded (`EmbeddingService`, bge-m3) and compared against
   that company's `klyro-brand-identity` and `klyro-campaigns` Pinecone vectors
   (`PineconeService.query`). Only trends scoring above `similarity_threshold` (default
   0.75) go further — this is the "trend seems similar" filter.
2. **Judge** — matches are sent to Claude with the prompt `prompts/opportunity_evaluation.md`,
   which returns a structured `OpportunityReport`: is it a real opportunity, how well does
   it fit the brand, and why.
3. **Recommend** — if it's a good fit, the same Claude call returns 1-3
   `CampaignRecommendation`s (title, creative angle, formats, urgency).

## New files

```
backend/
├── agents/opportunity_agent.py        # the agent — one run() method, per BaseAgent contract
├── schemas/
│   ├── trend_knowledge.py             # + TrendSignal, TrendMatch
│   └── opportunity_report.py          # OpportunityReport, TrackOpportunitiesRequest/Result
├── services/
│   ├── news_service.py                # News API wrapper (new)
│   ├── claude_service.py              # generate_structured() (shown here for context)
│   ├── pinecone_service.py            # query()/upsert() (shown here for context)
│   └── embedding_service.py           # embed() (shown here for context)
├── repositories/
│   ├── opportunity_repository.py      # trend_signals + opportunity_reports collections
│   ├── brand_repository.py            # get() (shown here for context)
│   └── company_repository.py          # list_all() — feeds the scheduler
├── prompts/opportunity_evaluation.md  # Claude's judgment prompt
├── routes/opportunity_routes.py       # POST /scan (on-demand), GET /{company_id} (history)
├── orchestrator/scheduler.py          # the "keep tracking" background job
└── config/{settings.py,constants.py}  # + NEWS_API_KEY
```

## New MongoDB collections

| Collection | Key fields | Notes |
|---|---|---|
| `trend_signals` | `signal_id`, `company_id` | every news article fetched, whether or not it matched |
| `opportunity_reports` | `report_id`, `company_id`, `signal_id` | Claude's judgment + campaign recommendations |

## Wiring into the existing app

- Add `NEWS_API_KEY=` to `.env` / `.env.example`.
- `pip install -r backend/requirements-opportunities.txt` (merge into the main requirements.txt).
- In `main.py`: `from orchestrator.scheduler import scheduler, register_opportunity_scan_job` →
  build an `OpportunityAgent` instance → `register_opportunity_scan_job(agent, CompanyRepository())`
  → `scheduler.start()` on app startup.
- Add `router` from `routes/opportunity_routes.py` to the FastAPI app the same way the other
  routers are included.

## One assumption made

The `companies` collection (context.md §10) didn't have a field for News API search terms,
so I added `industry_keywords: list[str]` to the `Company` doc — used to build each
company's News API query. If you'd rather derive these automatically from the
`BrandIdentityModel.industry` field instead of storing them separately, that's a small
change in `company_repository.py`.
