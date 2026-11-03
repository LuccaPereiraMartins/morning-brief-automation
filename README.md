# Rates morning brief

A small Python take-home implementation for Tom and Jim. It reads the supplied synthetic
pack, checks each user's book/research access, computes USD DV01 and limit headroom,
and generates sourced Markdown through a real local MCP client/server workflow.

The model adapter is implemented. Committed samples use the **explicit offline stub**:
research excerpts are shown without claiming that an LLM summarized them.

## Run

From this repository, with Python 3.13 and [uv](https://docs.astral.sh/uv/) installed:

```sh
uv sync --frozen --extra dev
uv run --frozen python -m rates_brief --user tom --as-of 2026-10-28 --output outputs/tom.md
uv run --frozen python -m rates_brief --user jim --as-of 2026-10-28 --output outputs/jim.md
uv run --frozen python -m rates_brief --user tom --as-of 2026-10-28 --scenario-bucket 10Y --scenario-dv01-usd 20000 --output outputs/tom_scenario.md
```

Examples: [Tom](outputs/tom.md), [Jim](outputs/jim.md), [what-if](outputs/tom_scenario.md).
Tom receives four relevant same-date research notes; Jim receives Bank A and Internal only.
Both see the same book risk. [The comparison](outputs/comparison.md) explains the difference.

Current total DV01 is **USD 139,207.12/bp**, with **USD 10,792.88/bp** headroom.
The scenario adds USD 20,000/bp to 10Y: the total breaches by USD 9,207.12/bp while
10Y remains within its own limit. This is an exposure calculation, not an order.

## Configuration and model access

`.env.example` lists environment variables; the application reads the process environment
and does **not** automatically load `.env` files. In PowerShell use `$env:NAME='value'`;
in a POSIX shell use `export NAME=value`.

| Variable | Default / purpose |
|---|---|
| `DATA_DIR` | `data`; source pack root |
| `SOURCE_CONFIG` | `config/sources.yaml`; unit scales, FX mappings, instrument rules and FX age |
| `AUDIT_DIR` | `audit`; restricted runtime event files |
| `LLM_MODE` | `offline` without a key, otherwise `live`; set explicitly for reproducibility |
| `LLM_MODEL` | Required approved model name in live mode |
| `OPENAI_API_KEY` | Provider credential; never logged or committed |
| `OPENAI_BASE_URL` | Optional OpenAI-compatible endpoint; SDK default otherwise |

For a live run set `LLM_MODE=live`, `LLM_MODEL`, and `OPENAI_API_KEY`, then use the same CLI.
The endpoint must support Chat Completions structured outputs. The adapter follows the
[official structured output interface](https://developers.openai.com/api/docs/guides/structured-outputs).
All calls pass through `llm.summarize` and `ProviderGateway`; a firm gateway adapter can replace it.
Live errors or rejected responses produce a labeled degraded excerpt section and an audit error.
No real provider call was made for this submission because credentials were unavailable.

Conversion uses the **DV01 currency**, preserves its sign, applies the configured unit scale,
and multiplies by USD per currency (or inverts a configured inverse quote). The appendix shows
the raw value, multiplier, FX rate/date/source and result. Missing/invalid/stale required FX fails
the request. Default maximum FX age is zero days; a configured older rate remains visibly dated.
USD is an identity conversion. Source conventions are developer-controlled configuration.

## Architecture and assumptions

```text
CLI + local user context
  -> MCP client -> local typed data server -> entitlement-filtered files
  -> deterministic risk + scenario calculations
  -> one model gateway interface (live or explicit offline stub)
  -> Markdown + append-only request audit
```

Typed MCP tools are `get_book_snapshot(book, as_of)`,
`get_market_snapshot(book, as_of, series)`, and `get_research(book, as_of, regions)`.
User/request context is bound at server startup, not supplied as a tool argument. For an
external local MCP client, start `python -m rates_brief.tools` with `BRIEF_USER` and a UUID
`BRIEF_REQUEST_ID`, plus the normal environment. Stdout is reserved for MCP.
The implementation uses the [official Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk).

- `--user` selects a synthetic local identity. It is **not authentication**; production must
  supply identity from a trusted authenticated session. Anyone with local filesystem access
  can read this synthetic pack. There is no shared service account in the application path.
- The position date must match `--as-of`. Market moves use the previous available close;
  research must have exactly that date. This is an EOD briefing, not a live monitor.
- Research relevance uses configured position regions. It is deliberately simple and does
  not infer trade suitability. Unsupported mappings are flagged while risk remains calculated.
- Limits apply to absolute net USD DV01, including the signed total across all positions.
  Limits are undated in the pack; the report states the assumption that they apply.
- Research is untrusted. HTML comments are removed from model/excerpt text, the system prompt
  rejects embedded instructions, and output IDs/coverage/numerical prose are checked. These
  checks do not prove arbitrary prompt-injection resistance or factual correctness.
- Market/risk tables are deterministic. Numerical statements in offline research excerpts are
  explicitly attributed source claims, not authoritative market observations.
- The MCP book adapter currently supports Rates only. Reusing it for EM requires an adapter
  for that book's different exposure fields.

## Checks and evaluation

```sh
uv run --frozen ruff check rates_brief tests
uv run --frozen ruff format --check rates_brief tests
uv run --frozen mypy rates_brief
uv run --frozen pytest -q
uv run --frozen python -m rates_brief.evaluate
```

[Evaluation cases](evals/cases.json) contain hand-authored scenarios; numerical expectations
are fixed independently of the calculator. The runner uses actual MCP requests and requires
100% passing. [Saved results](outputs/evaluation.md) identify the model mode. Unit tests also
exercise invalid model output, inverse FX, signed limits, and fatal audit failures.

With credentials configured, run `python -m rates_brief.evaluate --mode live --output outputs/live_evaluation.json`.
A degraded response fails live evaluation. Even a passing live run requires qualitative review
of each summary against its source, relevance to positions, and behavior under adversarial
research. Offline evaluation establishes application behavior, not live-model quality.

## Audit and runbook

Each run prints its request UUID and writes `AUDIT_DIR/<UUID>.jsonl`, matching the supplied
schema. Events include tool results, retrieved documents, source hashes, model inputs/results,
configuration, and the exact final Markdown. The response event reconstructs what was shown;
tool events preserve the inputs behind it. The conversion and configuration versions should
be retained with the deployment's Git revision in production.

Audit writes are append-only and flushed locally; these files are **not tamper-resistant**.
Protect their directory in production and replace the sink with approved durable storage.
The current single-request client/server writes sequentially. Runtime logs are excluded from Git.

If a run fails, inspect the request's error events, source dates and mappings, and exit status.
Fix the source/configuration and rerun with a new request UUID. Missing risk data and audit-write
failures stop successful report generation. Model failures show degraded excerpts. Monitor feed
age, failed deliveries, access denials, model degradation and audit failures in a hosted version.

To extend a supported product, edit source mappings, add independent expected test/eval cases,
run the checks and regenerate a sample. New data feeds implement the same typed source contracts.
No execution interface is included: the production hedge path is described in Part 3.

## Container and submission

```sh
docker build -t rates-brief .
docker run --rm -v "${PWD}/outputs:/app/outputs" -v "${PWD}/audit:/app/audit" rates-brief --user tom --as-of 2026-10-28 --output outputs/tom.md
```

Docker installs locked runtime dependencies and defaults to offline mode. CI runs lint,
format/type checks, tests, offline evals, then builds and smoke-runs the image. The local
Docker engine was unavailable during development; the container build has not been verified locally.

- [Part 1: reply to Tom](docs/part1_scope.md)
- [Part 3: reuse, graduation and future hedging](docs/part3_reuse.md)
- [Part 4: AI assistance and actual decisions](docs/part4_ai_use.md)

The repository includes the original pack, scoped implementation commits, sample reports,
and evaluation outputs. It is ready to publish; no GitHub remote has been configured.
