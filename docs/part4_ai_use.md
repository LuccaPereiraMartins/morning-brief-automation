# AI assistance and decisions

This implementation was developed with an AI coding assistant. These examples distinguish
the user's choices from corrections made during implementation; they do not claim that the
user manually wrote or reviewed every line.

| Suggestion or first implementation | Change or decision | Reason and evidence |
|---|---|---|
| The early discussion proposed a morning risk monitor with future hedging stages. | The user selected risk plus a deterministic what-if, with instrument selection/execution documented as future work. | The supplied data cannot support real-time execution. `risk.scenario` changes signed DV01 only. |
| The assistant presented CLI, web, or combined delivery options. | The user selected CLI plus Markdown. | Keeps the four-hour scope focused on the required controls and inspectable outputs. |
| Initial AI-written instrument mappings matched bond maturity-year suffixes. | Changed them before the feature commit to match supported exposure descriptions. | New issues and position IDs should reuse a supported mapping. A test changes both the position ID and bond maturity. |
| The first model error handler caught all exceptions and fell back to excerpts. | Added a dedicated audit-write exception which propagates as fatal. | An audit failure must not become a successful degraded report. A test covers that failure. |
| The first model tests substituted the gateway interface only. | Added a direct provider-adapter contract test with a mocked SDK client. | Checks structured output arguments, response parsing, and auditing without pretending a paid API call occurred. |
| A real model adapter alone would leave an unconfigured local demo unusable. | The user selected a real adapter plus explicitly labeled offline fallback. | The brief permits a stub when API access is unavailable. Sample outputs and evaluation identify offline mode; no live-model quality claim is made. |

The user also explicitly required transparent, configurable conversion. The implementation
therefore exposes unit/FX conventions and prints each position's conversion inputs and result.
This was a user requirement, not a fabricated story about rejecting hidden calculations.

Useful prompt/context excerpts were: “stick to the requirements laid out in BRIEF.md”,
“the conversion should definitely be made transparent and configurable”, and the approved
implementation plan. The assistant used those constraints to bound the build, then used tests
and independent numerical expectations to check its output.
