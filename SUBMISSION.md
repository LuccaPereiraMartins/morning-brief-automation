# Part 1 — Reply to Tom

Hi Tom — I'd start with a short morning brief for you and Jim: research relevant to the Rates
book, the latest supplied market moves, and DV01 against your limits. Each research view is
attributed and linked by source reference to the positions it concerns. Your risk tables match;
Jim's research coverage reflects his own licences.

**Done for this version:** either of you can generate the brief with one command. It shows signed
USD DV01, utilization and headroom by maturity and in total, with warnings and an inspectable
conversion appendix. A scheduled production job would prepare each user's brief before the
meeting and deliver it through their preferred approved channel. This exercise uses an EOD
snapshot, so its warning describes that snapshot rather than detecting an intraday crossing.

**Warning policy:** the demonstration flags utilization at or above 90% as approaching a limit;
exposure above 100% is a breach. The threshold is configurable and needs your agreement. The
supplied book is at 92.8%, with USD 10,792.88/bp headroom. FX/unit conversions are explicit and
sourced; I assume the supplied absolute-net limits and undated limit configuration apply.

**What follows:** Bloomberg ingestion would be the first content extension, after confirming
approved access, licensing and retention. Broker trade views remain attributed research in this
version. Generating our own trade suggestions and automatic hedging are later projects, with
hedging last and subject to the firm's Controlled Actions sign-off. Investigating execution is
outside this take-home.

**Questions:** what delivery time and research cutoff work for the meeting? Which official risk
source and offset policy should we use? What warning threshold and recipients do you want?
Which delivery channel and broker-chat access arrangements are approved?

**Success:** use your stated 40–45 minutes as the preparation-time baseline. In a short pilot,
measure preparation time, relevant items missed, corrections required, and usefulness of source
references. Agree a time-saving target with you; synthetic output cannot demonstrate that saving.

# Part 3 — Reuse and graduation

Share identity-aware research/book/market access, provenance, the model gateway interface and
audit conventions. `tools.py` outlines typed interfaces suitable for shared MCP hosting; the
prototype calls the same local data methods directly. No MCP transport is implemented. This
uses the paved road's local-version/clean-interface allowance; hosted MCP remains graduation work.
The Rates book adapter currently supports Rates only. EM could reuse research, identity and audit,
then add its hard/local-currency grouping, CS01 and FX exposures.

Keep instrument mappings, DV01 presentation, curve calculations and briefing relevance with the
Rates pod. To extend it, update an adapter/mapping, preserve typed outputs and source references,
add representative tests/evaluation expectations, run checks, and inspect a generated brief. In
production the official risk service would ideally supply documented, normalized exposures.

Before Technology ownership: name the business owner; agree risk/warning definitions and evaluation
thresholds; integrate firm identity, entitlements and gateway; establish official feeds and source
licences; and provide durable restricted audit storage, monitoring, a runbook and incident ownership.
Monitor source freshness, delivery failures, model degradation and audit failures. The local identity
selector and append-only files demonstrate behavior; production authentication and durable storage
are outstanding integrations.

**Future architecture / interview talking points:**

- Schedule the existing per-user briefing workflow in the firm's environment; deliver via an approved
  email, application or Teams adapter. Keep access checks per recipient and audit delivery outcomes.
- Add Bloomberg content first using approved ingestion and retention arrangements. Relevant prior
  experience to discuss: morning brief summarization and Bloomberg ingestion already undertaken.
- At larger volume, use hashes for exact duplicates and embeddings for related/near-duplicate
  candidates; retain versions so changed recommendations survive. A decision model can prioritize
  review, evaluated on missed relevant items, workload, cost and latency. Connect this to prior
  decision-model work. Access restrictions must apply to indexed content too.
- An approved agent could consume hosted MCP research/risk tools for follow-up questions or
  visualization; it would still need the firm's identity, gateway and audit controls.
- Trade suggestions are a later extension needing objectives and evaluation. Automatic hedging
  comes last; feasibility investigation and execution design are outside this project.

# Part 4 — AI assistance and decisions

An AI coding assistant produced the initial implementation. These are actual changes/rejections,
recorded with their reasons rather than invented retrospective examples:

| AI suggestion or initial code | Decision and reason |
|---|---|
| A working MCP subprocess/client/server for every brief | Replaced with typed candidate interfaces and direct local calls, following user review: transport plumbing obscured the core exercise. |
| A DV01 exposure what-if and detailed hedge roadmap | Removed after user review: focus on licensed research and a limit warning; execution investigation is outside scope. |
| Many separate documents and duplicated output summaries | Consolidated into this submission, a short README, two briefs and one evaluation result for easier review. |
| Instrument mappings based on maturity-year suffixes | Changed to supported exposure descriptions so new position IDs and issues can reuse mappings. |
| Catching every model-path exception and falling back | Audit-write failures now propagate; a successful report needs its audit. |

The user required transparent, configurable conversions and separate tests/evaluations, and chose
an explicit offline stub plus a real provider adapter. Samples identify the offline mode; they do
not claim a live model was evaluated. The simplification keeps small integration tests and independent
brief evaluations, while preserving the checks that explain access, calculations and failure handling.
