# Klyro — Impact Simulation

This slice implements the "Impact Simulation" feature:
content in → Claude researches + reasons → comprehensive future-impact analysis.

## Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```
Run from the `klyro/` root as `uvicorn backend.main:app --reload` if you keep
the package layout shown here.

Also add `GROQ_API_KEY` to `.env` — it's used for the image/video perception step.

API: `POST /api/v1/impact-simulation`

Text:
```json
{
  "company_id": "demo-co",
  "modality": "text",
  "content": "your AI-generated content here",
  "content_type": "social_post",
  "horizon": "90d",
  "extra_context": "optional"
}
```

Image:
```json
{
  "company_id": "demo-co",
  "modality": "image",
  "media": ["data:image/jpeg;base64,...."],
  "content": "optional caption",
  "content_type": "ad",
  "horizon": "90d"
}
```

Video: same as image, but `media` is a list of base64 frame images extracted
from the video, in chronological order (the frontend does this in-browser
with a `<canvas>`, so the raw video file is never uploaded).

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Opens at http://localhost:5173/impact-simulation

## How it works
1. You give the form text, an image, or a video.
   - Text goes straight through.
   - Image: the browser reads the file as base64 and sends one frame.
   - Video: the browser extracts 4 evenly-spaced frames (canvas snapshots)
     and sends those, in order — the raw video file itself is never uploaded.
2. If it's image/video, `ImpactSimulationAgent` first sends the frame(s) to
   `GroqService` (Groq vision), which returns a structured text description
   — this matches context.md's rule that only Groq touches raw media.
3. That description (or the raw text) is sent to Claude via `ClaudeService`,
   with the `web_search` tool enabled, so it can research current trends
   before reasoning about how the content will perform over the chosen
   time horizon.
4. Claude returns structured JSON (trajectory, trend signals, risks,
   opportunities, recommendations, citations), validated against
   `ImpactSimulationReport` and rendered in the UI.

This follows the same agent/service/schema/route pattern as the rest of the
Klyro architecture in `context.md`, so it can be dropped straight into the
full repo.
