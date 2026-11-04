# Morning brief automation

A Rates take-home: selected research for each user, a deterministic USD DV01 calculation,
and a warning when risk approaches or exceeds a limit. [Submission and talking points](SUBMISSION.md)
contain Parts 1, 3 and 4. Samples: [Tom](outputs/tom.md) and [Jim](outputs/jim.md).

## Run

From the repository with Python 3.13 and [uv](https://docs.astral.sh/uv/):

```sh
uv sync --frozen --extra dev
uv run --frozen python -m rates_brief --user tom --as-of 2026-10-28 --output outputs/tom.md
uv run --frozen python -m rates_brief --user jim --as-of 2026-10-28 --output outputs/jim.md
```

Samples use the explicit **offline stub**: permitted source excerpts and position references,
with no model call. Live mode uses an OpenAI-compatible structured-output adapter behind one
interface; set `LLM_MODE=live`, `LLM_MODEL`, and `OPENAI_API_KEY` to use it. Live failure produces
labeled excerpts. Live model quality has not been evaluated without credentials.

## Read the code

Start with `cli.generate`: read permitted data → calculate risk → summarize → render → audit.
Then read `risk.py` and `data.py`. `llm.py` owns model access and validation; `report.py` formats
Markdown. `tools.py` contains typed candidate MCP interfaces only. Shared access runs locally;
there is no MCP server or subprocess. This uses the exercise's allowance for clean interfaces
where firm shared services would go. A real server remains graduation work.

## Configuration and assumptions

The application reads the process environment; it does not load `.env` automatically.
`.env.example` lists the settings. In PowerShell use `$env:NAME='value'`; in POSIX use `export NAME=value`.

| Setting | Default / purpose |
|---|---|
| `DATA_DIR` | `data`; supplied synthetic pack |
| `SOURCE_CONFIG` | `config/sources.yaml`; units, FX pairs, instrument mappings, allowed FX age |
| `AUDIT_DIR` | `audit`; one append-only JSONL file per request |
| `LIMIT_WARNING_UTILIZATION` | `0.90`; demonstration assumption to agree with the PM; accepts (0, 1] |
| `LLM_MODE` | `offline` without a key, otherwise `live`; set explicitly for repeatable samples |
| `LLM_MODEL`, `OPENAI_API_KEY` | Required in live mode |
| `OPENAI_BASE_URL` | Optional approved OpenAI-compatible endpoint |

- DV01 uses its supplied currency and sign, multiplied by unit scale and USD per currency.
  Each position's conversion inputs, FX date and source appear in the report. Missing/stale FX fails.
- Limit utilization is absolute net USD DV01 / limit. At the warning threshold the report flags
  **approaching limit**; above the limit it flags **breached**. A threshold crossing sends no notification.
- CLI identity is a synthetic local selection, not authentication. Book and research permissions
  are checked before document bodies reach the model. Tom gets four relevant notes; Jim gets two.
- The snapshot must match the date. Market moves are close-to-close; research is same-date and
  region-matched. Unsupported mappings are flagged. Limits are undated and assumed applicable.
- Research is untrusted: model inputs exclude HTML comments, and outputs must reference permitted
  IDs and contain qualitative prose. These checks do not prove arbitrary injection resistance.
- All market/risk tables are deterministic. Quoted source figures may differ from the official closes.

## Checks

Tests and evaluations are separate: tests exercise calculations, access, validation and failure
handling; evaluations check complete briefs against a small hand-authored set with a 100% threshold.
CI runs both, plus lint/type checks and a Docker smoke run.

```sh
uv run --frozen ruff check rates_brief tests
uv run --frozen ruff format --check rates_brief tests
uv run --frozen mypy rates_brief
uv run --frozen pytest -q
uv run --frozen python -m rates_brief.evaluate
```

[Saved evaluation results](outputs/evaluation.json) identify offline mode. For live evaluation,
configure credentials and add `--mode live --output outputs/live_evaluation.json`; degradation
fails that run. Live summaries also need qualitative review against their sources.

## Audit and packaging

The printed UUID identifies `AUDIT_DIR/<UUID>.jsonl`. Schema-validated events retain sources/hashes,
tool results, model inputs/results, settings and the exact report. Missing risk data or audit-write
failure stops the request. Inspect error events, correct the input/config, and rerun with a new UUID.
Local audit files are excluded from Git and are not tamper-resistant production storage.

```sh
docker build -t rates-brief .
docker run --rm -v "${PWD}/outputs:/app/outputs" -v "${PWD}/audit:/app/audit" rates-brief --user tom --as-of 2026-10-28 --output outputs/tom.md
```

The container uses locked dependencies and offline mode. The scheduled deployment, delivery channels,
firm authentication/gateway, and hosted MCP integration are discussion points in the submission.
Repository: [morning-brief-automation](https://github.com/LuccaPereiraMartins/morning-brief-automation).
