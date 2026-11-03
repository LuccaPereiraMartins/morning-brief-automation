# Data pack

All data is synthetic. Rates instruments use real names; the EM countries (Corvana, Valdoria) and their currencies
(CVD, VDL) are fictional. It is now the morning of **2026-10-29**; the latest close in the data is **2026-10-28**.

| Folder / file | Contents |
|---|---|
| `requests/` | The two PM requests. Pick one (see the brief). |
| `research/` | Overnight broker and internal research. `source` in the front matter is the research provider. |
| `market_data/` | End-of-day closes for 2026-09-30 to 2026-10-28, and FX rates. |
| `positions/` | Positions for each pod's book, and the Rates pod's DV01 limits. |
| `entitlements.yaml` | Users, the books they can see, and the research they are licensed to read. |
| `platform/` | The firm's engineering standards for AI applications, and the audit event schema. |

## Units and conventions

- Yields and swap rates are in percent. Columns ending `_BP` are spreads over US Treasuries, in basis points.
  FX pairs are quoted as units of the second currency per one unit of the first.
- `dv01` is the profit or loss for a 1bp **fall** in yields, so long bonds and receive-fixed swaps are positive.
  It is in `dv01_ccy`, scaled by `dv01_unit`.
- `cs01_usd` is the profit or loss in USD for a 1bp **tightening** in credit spreads.
- `fx_delta_usd` is the USD value of the local-currency exposure; positive means long the local currency.
- DV01 limits apply to the absolute net DV01 per curve bucket, in USD.
