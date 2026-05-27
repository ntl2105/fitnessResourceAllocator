# Deployment

This app is a FastAPI dashboard intended to deploy on Vercel.

Vercel now recognizes FastAPI apps exported from `src/app.py`, so no legacy
`api/index.py` rewrite is required. The deployed app is read-only: it serves the
committed JSON, Markdown, static CSS/JS, and templates from this repository.

## Pre-Deploy Checklist

1. Finish the Marcus data generation pipeline.
2. Run the demo build so `data/runs/demo-run` is current.
3. Confirm the key local pages load:
   - `/calendar`
   - `/pipeline`
   - `/profile`
   - `/summary`
   - `/audit`
4. Run focused tests:

```bash
pytest tests/test_app.py tests/test_pipeline_story.py -q
```

## Local Vercel Smoke Test

```bash
vercel dev
```

Then open:

```text
http://localhost:3000/pipeline
```

## Deploy

Preview deployment:

```bash
vercel deploy
```

Production deployment:

```bash
vercel deploy --prod
```

## Notes

- `requirements.txt` defines the Python runtime dependencies.
- `vercel.json` is intentionally minimal because Vercel auto-detects FastAPI at
  `src/app.py`.
- `.vercelignore` excludes local-only assets while keeping the runtime `data/`
  artifacts needed by the dashboard.
- Do not depend on runtime generation in production. Commit the final
  `data/runs/demo-run` artifacts before deploying.
