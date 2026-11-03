# AI applications: the paved road (summary)

These are the firm's standards for AI applications built in the pods. They exist so that what one pod builds can be
run, audited and reused by Technology. In the real environment most of these are provided by shared services; for
this exercise, implement a minimal local version of each or a clean interface where the shared service would go.

1. **Per-user identity.** Every request runs as the end user who made it, not as a shared service account.
   Entitlement checks (books, research licences) happen in the data and tool layer, using that identity.
2. **LLM access through the gateway.** All model calls go through the firm's LLM gateway. In this exercise, put
   every model call behind a single interface so the gateway can be swapped in. Any provider is fine.
3. **Audit.** Each user request, tool call, document retrieved, model call and final response is recorded as an
   append-only event matching `audit_event.schema.json`. It must be possible to reconstruct exactly what a user was
   shown and why.
4. **Numbers come from data.** Any market level, risk number or calculation shown to a user comes from a data source
   or a deterministic calculation, with its source and as-of time. Models may explain numbers but not produce them.
5. **Shared tools as MCP servers.** Capabilities that more than one pod could use are exposed as MCP servers with
   typed inputs and outputs.
6. **Evaluation.** Every application ships an evaluation set and a runner, with thresholds, run in CI. Evals are
   required for graduation to Technology ownership.
7. **Packaging.** Container image, configuration through environment variables, no secrets in code or images,
   and a CI pipeline (lint, type checks, tests, evals).
8. **Controlled actions.** Anything with an effect outside the application, such as order entry, booking trades or
   external communications, goes through the firm's Controlled Actions process with Compliance and Technology sign-off.
9. **Graduation.** To move to Technology ownership an application needs: a named business owner, a runbook,
   evals with agreed thresholds, monitoring, and documented data sources and licences.
