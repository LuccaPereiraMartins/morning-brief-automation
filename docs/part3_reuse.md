# Reuse and graduation

**Shared capabilities.** Identity-aware access to research and book data, source references,
the model gateway contract, audit events, and typed MCP tools should be reusable services.
The local server exposes book snapshots, market observations, and licensed research. Its current
book adapter supports Rates only; an EM adapter must be added rather than pretending the Rates
DV01 contract covers all EM risks. EM can reuse identity, research, provenance, and audit while
adding hard/local-currency grouping, CS01, FX exposure, and its country report.

**Pod ownership.** Rates retains instrument mappings, curve/spread calculations, DV01 limit
presentation, research relevance, the morning workflow, and any future hedge policy. Official
upstream risk data would ideally already have documented, normalized units. The configurable
local conversion adapter exists to handle this supplied pack transparently.

**Extending it.** A developer adds a source adapter or mapping while preserving typed outputs
and source references, adds representative inputs and independent expected results, runs the
tests and evaluation, and generates a brief. The README describes local MCP startup, model
configuration, auditing, and checks. Source configuration and dependencies are versioned.

**Before Technology ownership:** name a business owner; agree risk definitions and evaluation
thresholds; integrate firm authentication and centrally managed entitlements; establish official
position, market, and research feeds with freshness/licensing agreements; approve model/data
handling; and provide durable restricted audit storage, monitoring, a runbook, and incident
ownership. CLI-selected identity and local append-only files demonstrate boundaries, not
production authentication or tamper-resistant storage.

**Automatic hedging path.** Consume current timestamped risk updates; apply approved thresholds,
buffers and repeat-trigger controls; evaluate approved hedge instruments with current sensitivities;
check cross-curve/currency effects, liquidity, costs and other limits; then route through Controlled
Actions under the approved authorization policy. Execution needs order/fill tracking, idempotency,
position reconciliation, and a stop mechanism. A net USD DV01 offset alone does not establish an
effective hedge. The current implementation supplies risk and exposure what-ifs only.

**Operations.** Monitor feed age, report delivery, missing data, access denials, model degradation,
audit failures and evaluation results. Stop successful report generation on missing risk inputs or
audit failure. On a model failure, show labeled source excerpts and retain the error. A live model
needs qualitative evaluation in addition to deterministic checks before operational use.
