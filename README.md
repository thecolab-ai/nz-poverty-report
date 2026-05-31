# The Baseline We Built — Poverty in Aotearoa New Zealand

**An independent, data-driven report on poverty as New Zealand's foundational challenge — the drivers, what works, and the highest-leverage path to solving it.**

Produced by [thecolab.ai](https://thecolab.ai) · point-in-time as at 31 May 2026.

📄 **[Read the report (PDF)](report/thecolab-poverty-baseline-challenge-nz.pdf)** — 48 pages.

---

## The headline

In the year ended June 2025, **169,300 children (14.3%) were in material hardship** — one in seven, the highest in roughly a decade — and **210,600 (17.8%) fell below the after-housing-costs income line**. Hardship is sharply concentrated: **Pacific children 31.0% and Māori children 25.1%**, against 11.5% for European children. The numbers are rising and the legislated targets are slipping.

The evidence points to two highest-leverage moves — **adequate, wage-indexed income support** and **public/affordable housing at register scale** — with housing the master driver that turns low income into lived hardship.

## What's in this repo

| Path | What it is |
|------|-----------|
| `report/thecolab-poverty-baseline-challenge-nz.pdf` | The full 48-page report |
| `data/cpra-measures-2025.csv` | The nine Child Poverty Reduction Act measures (rate + child count) — spreadsheet |
| `data/hardship-by-ethnicity-2025.csv` | Child poverty and material hardship by ethnicity — spreadsheet |
| `data/child-poverty-baseline-2025.json` | The baseline figures used for the report's charts |
| `data/research-output.json` | The full structured research output (drivers, solution levers, synthesis) |
| `scripts/render_report.py` | The report generator (matplotlib charts + WeasyPrint). Needs the brand fonts, which are not included here |

## Data sources

All figures come from **public, official New Zealand open data**, attributed in the report:

- **Stats NZ** — Child Poverty Reduction Act statistics (the nine measures, material/severe hardship, breakdowns by ethnicity, region and disability); household material hardship and income.
- **NZ Index of Multiple Deprivation** (small-area deprivation).
- **Ministry of Housing and Urban Development (HUD)** — public-housing register, accommodation supplement (via data.govt.nz).
- **Ministry of Social Development (MSD)** — benefit statistics.
- **Reserve Bank of New Zealand** and **Treasury** — macro and fiscal context.

These are queried through thecolab's open [nz-skills](https://thecolab.ai) data tooling.

## Method & integrity

The report was compiled by a multi-agent research process: each driver chapter was independently **fact-checked and run through internal-consistency logic checks** (e.g. severe hardship cannot exceed total material hardship; after-housing-cost poverty cannot fall below before-housing-cost). Where a chapter's figures were thinner or needed care, the report says so — see the confidence overview near the end.

The official Child Poverty Reduction Act measures use the codes `MEASA`–`MEASJ`; the verbatim Stats NZ legend is documented in the report and reflected in the CSVs.

## Notes

- This is **independent analysis**, not financial, policy, or legal advice, and is not affiliated with or endorsed by any political party or government agency.
- Estimates carry sampling error; the report surfaces confidence intervals alongside point estimates.
- Figures are a point-in-time snapshot (year ended June 2025 for child-poverty measures; 31 May 2026 for macro context).

Built by thecolab.ai — *AI expertise, built together.*
