# Technical notes

This is the technical companion to the [README](README.md). It covers the original study, the data, the rules, the
full set of test statistics and how to reproduce everything. Every table the scripts write is in
[results/FINDINGS.md](results/FINDINGS.md).

## The original study

F. P. Ramsey, "A Contribution to the Theory of Taxation," *Economic Journal* 37(145), March 1927, pp. 47–61. Ramsey
asks how proportionate commodity taxes should be set to raise a given revenue with the least loss of utility. For an
infinitesimal revenue the taxes should reduce the production of every taxed good in the same proportion (section 6,
p. 51; section 8, p. 52). With independent goods, the ad valorem tax on each good should be proportional to the sum
of the reciprocals of its demand and supply elasticities (equation 12, p. 56), so with constant costs the tax is
inversely proportional to the demand elasticity. With a quadratic utility function (linear schedules) the
same-proportion rule holds for any feasible revenue, and revenue is maximized by halving every output (section 11,
p. 54). The paper contains no data; its "headline numbers" are these formal results. Boiteux (1956) derives the same
rule for a multiproduct public monopoly under a break-even constraint.

## Headline results

| Test | Estimate | Ramsey's prediction |
|---|---|---|
| Slope of markup on 1/elasticity, 27 products, unweighted | −0.101 (SE 0.037), 95% CI [−0.173, −0.030] | positive |
| Intercept, same regression | 0.616 (SE 0.092) | zero |
| Slope, revenue-weighted | −0.015 (SE 0.068) | positive |
| Slope, excluding 4 statutory products | −0.011 (SE 0.036) | positive |
| Spearman rank correlation | −0.375 (p = 0.054) | positive |
| Log form, positive markups (N = 23), slope | −0.023 (SE 0.207); slope = 1 rejected, p < 0.001 | one |
| Ramsey number L·ε across products | −0.194 to 1.414, SD 0.333 | constant |
| Deadweight loss, same contribution, linear demand | actual $3,228M, Ramsey $2,523M, saving $704M (21.8%) | Ramsey lower |
| Break-even ($32,584M contribution), consumer-surplus loss | uniform +31.5%: $13,184M; Ramsey: $11,994M | Ramsey lower |

## Data

All files are public filings in Postal Regulatory Commission docket ACR2025, downloaded from prc.arkcase.com on
November 1, 2026, and committed to `data/raw/`.

| File | Source filing | Used for |
|---|---|---|
| `Public_FY25CRA_Expanded.xlsx` | USPS-FY25-1, Public Cost and Revenue Analysis (filed Dec 29, 2025) | Revenue, attributable cost, volume-variable cost by product; institutional costs; totals |
| `Public_FY25CRAReport.xlsx` | same | Revenue per piece (sheet Cost1) |
| `DemandEquationTables_md_Jan2026.docx` | Documentation of Demand Elasticities and Volume Forecasts (filed Jan 20, 2026) | Long-run own-price elasticities and t-statistics |
| `vf_md_Jan2026.xlsx` | same | FY2025 volumes by demand category (sheet HistVols), elasticities (sheet Elasts) |

## Method

Rules fixed before seeing results:

- **Markup.** $`L_i = (R_i - VVC_i)/R_i`$ with revenue $`R_i`$ and volume-variable cost $`VVC_i`$ from the PCRA.
  Attributable cost replaces volume-variable cost as a check.
- **Elasticity.** The Postal Service's long-run own-price elasticity (sum of current and up to four quarterly lags).
  A product spanning several demand categories gets the FY2025 volume-weighted mean; its standard error assumes
  independent category estimates. Marketing Mail Flats and Carrier Route both map to the "Flats & Basic CR"
  demand categories, so they share one elasticity.
- **Sample.** 27 market-dominant products matched to demand categories, $45,019M of $45,765M market-dominant
  revenue. Excluded: political mail (cuts across products), inbound international (UPU-set prices), return receipts
  (not separated in the PCRA), penalty and free mail (no price).
- **Statutory products.** In-county and outside-county Periodicals, Media and Library Mail, Alaska Bypass, dropped
  in one robustness sample.
- **Estimating equation.** One cross-section, HC1 standard errors, OLS and revenue-weighted WLS:

```math
L_i = \alpha + \beta \,\frac{1}{\varepsilon_i} + u_i, \qquad H_0:\ \alpha = 0,\ \beta = \lambda > 0
```

- **Ramsey number.** $`\lambda_i = L_i\,\varepsilon_i`$, which Boiteux's first-order condition makes equal across products:

```math
\frac{p_i - c_i}{p_i} = \frac{\mu}{1+\mu}\cdot\frac{1}{\varepsilon_i}
```

- **Counterfactual, linear demand (main).** Prices indexed to 1 at FY2025; quantity in FY2025 revenue dollars, so
  $`q_i(p) = R_i\,[1 - \varepsilon_i (p-1)]`$, slope $`b_i = \varepsilon_i R_i`$, marginal cost
  $`c_i = VVC_i/R_i`$. With $`\bar{x}_i = q_i(c_i)`$:

```math
q_i^{R} = (1-k)\,\bar{x}_i,\qquad p_i^{R} = c_i + \frac{k\,\bar{x}_i}{b_i},\qquad T = k(1-k)\sum_i \frac{\bar{x}_i^{2}}{b_i},\qquad \text{DWL} = \sum_i \tfrac{1}{2}\, b_i\,(p_i - c_i)^2
```

- **Counterfactual, constant elasticity (check).** $`q_i = R_i\,p^{-\varepsilon_i}`$, $`p_i^R = c_i/(1-\lambda/\varepsilon_i)`$,
  $`\lambda`$ solved numerically, consumer-surplus change $`R_i\,(1 - p^{1-\varepsilon_i})/(1-\varepsilon_i)`$.
- **Targets.** Scenario A, the FY2025 contribution of the 27 products ($23,606M). Scenario B, that plus the FY2025
  shortfall of all revenue (including investment income, $81,353M) below total costs ($90,331M), which is $8,978M.

## Full test statistics

| Sample | Cost | Weights | N | β | SE | p | Intercept | R² | Spearman ρ (p) |
|---|---|---|---|---|---|---|---|---|---|
| All | volume-variable | none | 27 | −0.101 | 0.037 | 0.005 | 0.616 | 0.21 | −0.375 (0.054) |
| All | volume-variable | revenue | 27 | −0.015 | 0.068 | 0.83 | 0.560 | 0.00 | |
| All | attributable | none | 27 | −0.102 | 0.037 | 0.005 | 0.612 | 0.21 | −0.372 (0.056) |
| Non-statutory | volume-variable | none | 23 | −0.011 | 0.036 | 0.77 | 0.485 | 0.00 | −0.213 (0.33) |
| Non-statutory | volume-variable | revenue | 23 | 0.059 | 0.079 | 0.46 | 0.403 | 0.03 | |
| Significant elasticities | volume-variable | none | 24 | −0.049 | 0.076 | 0.52 | 0.528 | 0.03 | −0.236 (0.27) |
| Significant elasticities | volume-variable | revenue | 24 | 0.013 | 0.085 | 0.88 | 0.497 | 0.00 | |

Counterfactual summary (millions of dollars a year):

| Scenario | Demand | Policy | ΔCS | DWL | k or λ |
|---|---|---|---|---|---|
| A | linear | actual prices | 0 | 3,228 | |
| A | linear | Ramsey | +704 | 2,523 | k = 0.176 |
| A | linear | Ramsey, statutory fixed | +531 | 2,697 | k = 0.183 |
| A | constant elasticity | Ramsey | +2,220 | | λ = 0.135 |
| B | linear | uniform +31.5% | −13,184 | 7,434 | |
| B | linear | Ramsey | −11,994 | 6,244 | k = 0.277 |
| B | linear | Ramsey, statutory fixed | −12,501 | 6,751 | k = 0.291 |
| B | constant elasticity | uniform +28.2% | −11,999 | | |
| B | constant elasticity | Ramsey | −8,165 | | λ = 0.136 |

The maximum contribution under linear demand ($`k = 1/2`$) is $40,670M. The constant-elasticity Ramsey solution sets
$`\lambda`$ just below the smallest elasticity (in-county Periodicals, 0.136), which multiplies that product's price
650-fold in Scenario B; it is reported as a bound, not relied on.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/ramsey_test.py
python src/ramsey_counterfactual.py
```

Both scripts read only `data/raw/` and `results/`, and run offline. Python 3.12 or later.

## Repository layout

| Path | What it is |
|---|---|
| `src/ramsey_test.py` | Parses the filings, builds the product table, runs the Ramsey regressions, draws the scatter |
| `src/ramsey_counterfactual.py` | Ramsey and uniform price counterfactuals, welfare comparison, bar chart |
| `results/products.csv` | One row per product: revenue, costs, markups, elasticity, Ramsey number |
| `results/demand_categories.csv` | The 39 demand categories with volumes, elasticities, t-statistics |
| `results/ramsey_tests.csv`, `results/lambda_summary.csv` | Test statistics |
| `results/counterfactual_products.csv`, `results/counterfactual_summary.csv` | Counterfactual prices and welfare |
| `results/usps_totals.csv` | Whole-Postal-Service totals |

## References

- Boiteux, M. (1956). Sur la gestion des monopoles publics astreints à l'équilibre budgétaire. *Econometrica*
  24(1), 22–40. English translation, *Journal of Economic Theory* 3(3), 1971, 219–240.
- Postal Accountability and Enhancement Act, Public Law 109-435 (2006), 39 U.S.C. 3622.
- Postal Regulatory Commission (2025). *Elasticity Study, Phase 1*, Docket RM2024-4.
- Postal Regulatory Commission (2026). *Annual Compliance Determination Report, Fiscal Year 2025*.
- Ramsey, F. P. (1927). A contribution to the theory of taxation. *Economic Journal* 37(145), 47–61.
