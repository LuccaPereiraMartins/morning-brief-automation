# Morning brief automation

Generate Rates research briefs with per-user licences, sourced DV01 calculations and limit warnings.
Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

## Run

```sh
uv sync --frozen --extra dev
uv run --frozen python -m rates_brief --user tom --as-of 2026-10-28 --output outputs/tom.md
uv run --frozen python -m rates_brief --user jim --as-of 2026-10-28 --output outputs/jim.md
```

Without an API key, the explicit offline stub shows permitted source excerpts. For live summaries,
set `LLM_MODE=live`, `LLM_MODEL` and `OPENAI_API_KEY` in the process environment. An optional
`OPENAI_BASE_URL` selects an approved compatible endpoint. Set `LLM_MODE=offline` to force offline mode.
See `.env.example` for settings. To load `.env`, add `--env-file .env` after `uv run`.

`LIMIT_WARNING_UTILIZATION` defaults to `0.90`, a demonstration assumption to confirm with the PM.
Warnings reflect the supplied EOD snapshot. Audit events are written to `audit/<request-id>.jsonl`.

## Tests and evaluation

```sh
uv run --frozen pytest -q
uv run --frozen python -m rates_brief.evaluate
```

Examples: [Tom](outputs/tom.md), [Jim](outputs/jim.md), and the
[saved evaluation run](outputs/evaluation.json). The evaluation command regenerates that JSON;
offline checks do not assess live model quality.

## Docker

```sh
docker build -t rates-brief .
docker run --rm -v "${PWD}/outputs:/app/outputs" -v "${PWD}/audit:/app/audit" rates-brief --user tom --as-of 2026-10-28 --output outputs/tom.md
```
