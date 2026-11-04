# Rates — 2026-10-28 — jim

RATES_RV · EOD · live

**TOTAL: approaching limit — 92.8% used; USD 10,792.88/bp headroom.**

## Research

- **Bank A / US:** Bank A expects further long-end Treasury cheapening and curve steepening, while remaining neutral on swap spreads. The Treasury curve and swap-spread discussion covers the listed UST and SOFR positions. (R-001, R-002, R-003, R-004; [1])
- **Internal / Global:** Internal strategy reports a Treasury bull flattening and gilt outperformance, and flags book DV01 near its limit. The market commentary concerns the Treasury and gilt holdings; the DV01 warning is book-wide across the listed positions. (R-001, R-002, R-003, R-004, R-005, R-006, R-007, R-008; [2])

## DV01 — USD/bp

| Bucket | Net | Limit | Used |
|---|---:|---:|---:|
| 5Y | 69,500.00 | 100,000.00 | 69.5% |
| 10Y | 48,557.04 | 120,000.00 | 40.5% |
| 30Y | 21,150.08 | 50,000.00 | 42.3% |
| TOTAL | 139,207.12 | 150,000.00 | 92.8% |

Warning ≥90.0% (demo policy); breach >100%.

<details>
<summary>Market closes and sources</summary>

Levels in %, changes in bp versus the previous close.

| Series | Close | Δ bp |
|---|---:|---:|
| BUND_10Y | 2.698 | +5.60 |
| GILT_10Y | 4.492 | -7.00 |
| GILT_30Y | 5.298 | +1.70 |
| SOFR_SWAP_10Y | 3.746 | -5.50 |
| SONIA_SWAP_10Y | 3.926 | -7.30 |
| UST_10Y | 4.121 | -5.90 |
| UST_2Y | 3.536 | +4.20 |
| UST_30Y | 4.835 | +0.80 |
| UST_5Y | 3.777 | +6.50 |

US 2s10s: 58.50bp.
US 5s30s: 105.80bp.

Market: `market_data/rates_eod.csv:22` (2026-10-28); previous: `market_data/rates_eod.csv:21` (2026-10-27)

Research references (quotes are broker views, not official closes):
- [1] US Rates Weekly - Back into 5s30s steepeners — `research/2026-10-28_bank-a_ust-weekly.md:8` (2026-10-28)
- [2] Rates pod - morning note — `research/2026-10-28_internal_rates-strategy.md:9` (2026-10-28)

</details>

<details>
<summary>DV01 conversions and audit</summary>

USD DV01 = raw DV01 × unit scale × USD per currency; signs are preserved.

| Position | Raw / currency / unit | Scale | FX quote | USD DV01 | Sources |
|---|---|---:|---|---:|---|
| R-001 | 69500 / USD / units | 1 | USD/USD=1 | 69,500.00 | `positions/rates_rv_2026-10-28.csv:2` (2026-10-28); USD identity |
| R-002 | 73.2 / USD / thousands | 1000 | USD/USD=1 | 73,200.00 | `positions/rates_rv_2026-10-28.csv:3` (2026-10-28); USD identity |
| R-003 | 168000 / USD / units | 1 | USD/USD=1 | 168,000.00 | `positions/rates_rv_2026-10-28.csv:4` (2026-10-28); USD identity |
| R-004 | -152300 / USD / units | 1 | USD/USD=1 | -152,300.00 | `positions/rates_rv_2026-10-28.csv:5` (2026-10-28); USD identity |
| R-005 | 51800 / GBP / units | 1 | GBPUSD=1.3312 | 68,956.16 | `positions/rates_rv_2026-10-28.csv:6` (2026-10-28); `market_data/fx_rates.csv:2` (2026-10-28) |
| R-006 | -39100 / GBP / units | 1 | GBPUSD=1.3312 | -52,049.92 | `positions/rates_rv_2026-10-28.csv:7` (2026-10-28); `market_data/fx_rates.csv:2` (2026-10-28) |
| R-007 | -50400 / GBP / units | 1 | GBPUSD=1.3312 | -67,092.48 | `positions/rates_rv_2026-10-28.csv:8` (2026-10-28); `market_data/fx_rates.csv:2` (2026-10-28) |
| R-008 | 26700 / EUR / units | 1 | EURUSD=1.1608 | 30,993.36 | `positions/rates_rv_2026-10-28.csv:9` (2026-10-28); `market_data/fx_rates.csv:3` (2026-10-28) |

Currency contributions (USD/bp): EUR: 30,993.36; GBP: -50,186.24; USD: 158,400.00

Limits (absolute signed net; total nets across currencies/curves): `positions/rates_limits.csv:2` (undated); `positions/rates_limits.csv:3` (undated); `positions/rates_limits.csv:4` (undated); `positions/rates_limits.csv:5` (undated)

Audit request: `a4c2ecb1-e2cc-4c42-8bf5-6b2d1b831b18`. Local synthetic snapshot; no intraday notifications.

</details>
