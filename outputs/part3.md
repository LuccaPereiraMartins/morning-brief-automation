# sharing:

- realistically, most interesting bits here would be an MCP server (or adding to an existing one) with a tool for identity-aware data/research access, espcially once bloomberg is included. then users could go from their typical flow, eg Codex, and after auth, benefit from it seamlessly. or build agents that do other things (weekly summaries, historical research)
- maybe the book/market read could become an MCP-exposed tool too, but that is likely too variable/sensitive across pods to be easily generalised. 
- pretty much everything else is simple/custom, with little value to generalise (as I understand it)

# extending or graduating

- a fair few things are required (the technical detail) (* denotes what I would expect to deliver, rest would be pod dev/Tech):
- *proper llm adapter, use the firms gateway (from paved road), securely calling cloud or local model, preferably provider agnostic
- *scheduling, lambda, ECS/EventBridge, pipelines, whatever flow is used, with appropriate provisioning and runtime perms (like env vars for LLM calls)
- *user authentication, ideally calls data sources on-behalf-of, rather than service principle then in-repo filtering/mapping. might have to be a mix of both to cover all sources
- *need a named business owner to agree scope and sign off/justify costs
- *runbook/handover guide for deployment and general who-to-contact
- *some evaluation thresholds that we monitor against, eg for miss-rate or research leakage
- monitoring and logging: sources are ingested okay and timely, failed deliveries, access denials, audit failures, audits are going to the right place, token costs are documented (assuming these are already common patterns)
- Bloomberg is possible, but can be tricky, depends on what firm already has
- if research volume greatly increases, consider vectors for deduplication, or decision models for prioritization/relevancy (also more cost and latency efficient)

