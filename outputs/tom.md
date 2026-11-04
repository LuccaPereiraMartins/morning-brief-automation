# Rates morning brief — tom

Book: **RATES_RV** · Snapshot: **2026-10-28** · Request: `eb13480a-3052-4f89-bc89-33b7a13abd21`

Research mode: **offline stub**. No model call was made; the research text below is quoted source material.

Synthetic data; end-of-day snapshot, not an intraday risk monitor.

## Risk and limits

| Bucket | Net USD DV01 | Limit | Utilization | Headroom | Status |
|---|---:|---:|---:|---:|---|
| 5Y | 69,500.00 | 100,000.00 | 69.5% | 30,500.00 | within limit |
| 10Y | 48,557.04 | 120,000.00 | 40.5% | 71,442.96 | within limit |
| 30Y | 21,150.08 | 50,000.00 | 42.3% | 28,849.92 | within limit |
| TOTAL | 139,207.12 | 150,000.00 | 92.8% | 10,792.88 | approaching limit |

Warning at 90.0% utilization (configurable demonstration assumption; confirm with the PM). This flag reflects the supplied snapshot; it does not send a notification.

DV01 is USD profit/loss for a one-basis-point fall in yields. Limits apply to absolute net DV01. Total nets all signed position exposures.

Limits: `positions/rates_limits.csv:2` (as of undated limit configuration); `positions/rates_limits.csv:3` (as of undated limit configuration); `positions/rates_limits.csv:4` (as of undated limit configuration); `positions/rates_limits.csv:5` (as of undated limit configuration)

### Currency contributions

| Source currency | Net DV01 converted to USD |
|---|---:|
| EUR | 30,993.36 |
| GBP | -50,186.24 |
| USD | 158,400.00 |

Cross-currency offsets follow the supplied limit definition; they do not establish protection against independent curve moves.

## Market closes

Changes are close-to-close against the previous available observation.

| Series | Latest (%) | Previous (%) | Change (bp) |
|---|---:|---:|---:|
| BUND_10Y | 2.698 | 2.642 | +5.60 |
| GILT_10Y | 4.492 | 4.562 | -7.00 |
| GILT_30Y | 5.298 | 5.281 | +1.70 |
| SOFR_SWAP_10Y | 3.746 | 3.801 | -5.50 |
| SONIA_SWAP_10Y | 3.926 | 3.999 | -7.30 |
| UST_10Y | 4.121 | 4.180 | -5.90 |
| UST_2Y | 3.536 | 3.494 | +4.20 |
| UST_30Y | 4.835 | 4.827 | +0.80 |
| UST_5Y | 3.777 | 3.712 | +6.50 |

Sources: `market_data/rates_eod.csv:22` (as of 2026-10-28); `market_data/rates_eod.csv:21` (as of 2026-10-27)

### Derived spreads

| Spread | Latest (bp) | Change (bp) |
|---|---:|---:|
| US 2s10s (UST_10Y − UST_2Y) | 58.50 | -10.10 |
| US 5s30s (UST_30Y − UST_5Y) | 105.80 | -5.70 |
| US 10Y swap spread (SOFR_SWAP_10Y − UST_10Y) | -37.50 | +0.40 |
| UK 10Y swap spread (SONIA_SWAP_10Y − GILT_10Y) | -56.60 | -0.30 |

Spreads use the same dated observations cited above.

## Research for your positions

Your licensed providers: Bank A, Bank B, Bank C, Internal. Only same-date, relevant, licensed documents are included. Research quotes are source assertions and may differ from the market closes above.

### [1] US Rates Weekly - Back into 5s30s steepeners

**Bank A** · 2026-10-28 · `research/2026-10-28_bank-a_ust-weekly.md:8` (as of 2026-10-28)

> With the 10y at 4.35% and the market pricing barely one more cut this cycle, we think the long end has further to cheapen. 5s30s has steepened to 112bp from 90bp at the start of the month. We re-enter 5s30s steepeners (DV01-neutral) with a target of 130bp and a stop at 100bp.  We stay neutral on 10y swap spreads at around -38bp.

Positions: R-001, R-002, R-003, R-004. Region matches the listed positions; review the source view.

### [2] Gilts - BoE November preview

**Bank B** · 2026-10-28 · `research/2026-10-28_bank-b_gilts-boe-preview.md:8` (as of 2026-10-28)

> We expect the MPC to hold Bank Rate on 5 November with a 6-3 vote, but with dovish guidance. With 10y gilts around 4.5%, we prefer receiving 10y SONIA versus paying 2y, and we see 10y SONIA swap spreads (now around -57bp) as too negative given the reduction in long-end gilt supply in the remit revision.  Risks: a hawkish surprise on services inflation would hit the front end hardest.

Positions: R-005, R-006, R-007. Region matches the listed positions; review the source view.

### [3] EUR rates - Bund swap spreads look stretched

**Bank C** · 2026-10-28 · `research/2026-10-28_bank-c_eur-swap-spreads.md:8` (as of 2026-10-28)

> 10y Bunds at 2.64% look cheap against swaps after the October supply. We recommend long 10y Bunds versus paying 10y EUR swaps, targeting 10bp of tightening in the spread. We also see value in 10y Bund-gilt spread tighteners.

Positions: R-008. Region matches the listed positions; review the source view.

### [4] Rates pod - morning note

**Internal** · 2026-10-28 · `research/2026-10-28_internal_rates-strategy.md:9` (as of 2026-10-28)

> UST 2s10s at 58bp and 5s30s at 106bp after yesterday&#x27;s bull flattening into the close. Gilts outperformed Treasuries. Total book DV01 is running close to the limit; worth reviewing the 10y bucket before adding risk. Watch the 30y gilt syndication next week.

Positions: R-001, R-002, R-003, R-004, R-005, R-006, R-007, R-008. Region matches the listed positions; review the source view.

## DV01 conversion appendix

USD DV01 = supplied DV01 × unit scale × USD per source currency. Inverse quotes use 1 / quoted FX rate. USD uses an identity conversion.

| Position | Instrument | Raw DV01 | Currency / unit | Scale | FX quote | USD per currency | USD DV01 | Sources |
|---|---|---:|---|---:|---|---:|---:|---|
| R-001 | UST 4.25 08/15/31 | 69500 | USD / units | 1 | USD/USD=1 | 1 | 69,500.00 | `positions/rates_rv_2026-10-28.csv:2` (as of 2026-10-28); USD identity |
| R-002 | UST 4.625 08/15/56 | 73.2 | USD / thousands | 1000 | USD/USD=1 | 1 | 73,200.00 | `positions/rates_rv_2026-10-28.csv:3` (as of 2026-10-28); USD identity |
| R-003 | SOFR IRS 10Y RECEIVE | 168000 | USD / units | 1 | USD/USD=1 | 1 | 168,000.00 | `positions/rates_rv_2026-10-28.csv:4` (as of 2026-10-28); USD identity |
| R-004 | UST 4.125 08/15/36 | -152300 | USD / units | 1 | USD/USD=1 | 1 | -152,300.00 | `positions/rates_rv_2026-10-28.csv:5` (as of 2026-10-28); USD identity |
| R-005 | UKT 4.5 03/07/36 | 51800 | GBP / units | 1 | GBPUSD=1.3312 | 1.3312 | 68,956.16 | `positions/rates_rv_2026-10-28.csv:6` (as of 2026-10-28); `market_data/fx_rates.csv:2` (as of 2026-10-28) |
| R-006 | UKT 4.375 07/31/56 | -39100 | GBP / units | 1 | GBPUSD=1.3312 | 1.3312 | -52,049.92 | `positions/rates_rv_2026-10-28.csv:7` (as of 2026-10-28); `market_data/fx_rates.csv:2` (as of 2026-10-28) |
| R-007 | SONIA IRS 10Y PAY | -50400 | GBP / units | 1 | GBPUSD=1.3312 | 1.3312 | -67,092.48 | `positions/rates_rv_2026-10-28.csv:8` (as of 2026-10-28); `market_data/fx_rates.csv:2` (as of 2026-10-28) |
| R-008 | DBR 2.6 02/15/36 | 26700 | EUR / units | 1 | EURUSD=1.1608 | 1.1608 | 30,993.36 | `positions/rates_rv_2026-10-28.csv:9` (as of 2026-10-28); `market_data/fx_rates.csv:3` (as of 2026-10-28) |

## Coverage and limitations

- Position relevance uses configured instrument regions; it is not a hedge model.
- Older research is excluded from this morning's view.
- Limit files have no effective date; the supplied configuration is assumed applicable.
- Source content hashes, calculations, and this exact response are retained in the audit.
