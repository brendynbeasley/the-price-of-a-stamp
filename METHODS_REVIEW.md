# Methods review: Ramsey (1927)

**Paper.** F. P. Ramsey, "A Contribution to the Theory of Taxation," *The Economic Journal* 37(145), March 1927,
pp. 47–61. Read alongside its usual companion, M. Boiteux, "Sur la gestion des monopoles publics astreints
à l'équilibre budgétaire," *Econometrica* 24(1), 1956, pp. 22–40.

**Statistical focus.** The proportional-reduction theorem (section 6 and section 8) and the inverse-elasticity rule
of equation (12), which together are what later literature calls the Ramsey rule; secondarily, the quadratic-utility
results of Part II (rule valid for any revenue; maximum revenue at half output).

**Review standard.** Internal consistency of the formal results, explicitness of assumptions, and the testability of
the predictions, judged as a modern referee would judge a theory paper.

**What was read.** The full text of Ramsey (1927) from the public-domain scan of the JSTOR copy held at the Internet
Archive (item `ramseycontribtheorytax1927`), in its OCR text version, which garbles many equations; equation
content below is taken from the legible statements of results that accompany them. Boiteux (1956) was not read; it
is described only from its bibliographic record and secondary accounts, and nothing below relies on its contents.

## Methods summary

**Research design.** Pure theory. Ramsey sets up a competitive economy with n commodities and a net-utility function
u = F(x_1, …, x_n), introduces specific taxes λ_r that drive a wedge between demand and supply prices, and maximizes
u subject to a revenue constraint R = Σ λ_r x_r. Distribution, differences in the marginal utility of money, foreign
trade and externalities are set aside explicitly (p. 47). The marginal utility of money is held constant and
revenue is assumed to be returned without affecting demand schedules.

**Sampling strategy, sample size, inclusion and exclusion criteria.** Do not apply. The paper has no data. Its
scope conditions play the role of inclusion criteria: commodities are final consumption or saving (to avoid double
counting, p. 48); the analysis holds for "sufficiently small" revenue in Part I and for any feasible revenue under
quadratic utility in Part II.

**Independent and dependent variables.** The choice variables are the tax rates (specific taxes λ_r, later ad
valorem rates); the outcome is the loss of utility. The comparative statics are expressed through demand and supply
elasticities, which the paper treats as known.

**Statistical methods.** Calculus of variations with Lagrange multipliers (section 5), second-order conditions via
negative-definite quadratic forms, and a geometric argument with similar hyper-ellipsoids in Part II (sections 10 to
14). An appendix extends the problem to a revenue that also buys fixed quantities of goods.

**Reported effect sizes, confidence intervals, p-values.** None. The formal results stand in for statistics and are
listed in the table below. There are no numerical examples beyond the remark that a 500% whisky tax might still
count as "small" for the approximation (p. 60).

**Missing data treatment.** Does not apply.

**Stated limitations.** Ramsey states that applications cannot be made exactly without data he does not have
(p. 58); that the infinitesimal results are only approximations whose range depends on the unknown curvature of
supply and demand curves (p. 60); that the treatment of saving assumes taxes imposed for a very short time with no
expectation of future taxation (p. 59); and that the general equations are too complicated to be worth stating
without practical data (p. 60).

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Proportional-reduction rule, infinitesimal revenue | dx_1/x_1 = dx_2/x_2 = … = dx_n/x_n (unitless) | Section 6, p. 51 | Optimal pattern of output reductions for a small revenue with a general utility function | That actual tax systems follow it, or its accuracy for large revenues |
| Same rule when only some goods are taxed | dx_r/x_r equal across taxed goods | Section 8, p. 52 | Extension to a restricted tax base | Behavior of untaxed goods' outputs, which may move in either direction |
| Inverse-elasticity rule, independent goods | ad valorem tax on good r proportional to 1/ρ_r + 1/ε_r (demand and supply elasticities) | Equation (12), p. 56 | Optimal relative tax rates when demands and supplies are independent | Optimal rates with cross-price effects; any equity considerations |
| Absolutely inelastic good | entire revenue raised from it | Section 16(3), pp. 56–57 | Limiting case of equation (12) | That such a tax is fair or politically feasible |
| Rule with labor as the only resource | tax rates set by each good's demand elasticity ρ_r and the supply elasticity of labor ε; uniform ad valorem taxes if labor supply is fixed (ε → 0) | Equations (13)–(14), p. 57 | Case of complete substitutes in supply | Results when labor supply is elastic and heterogeneous |
| Part II, quadratic utility | same-proportion rule valid for any feasible revenue; taxes in fixed proportions independent of revenue | Sections 11–12, pp. 53–54 | Global version under linear schedules | Validity when schedules are curved |
| Maximum revenue | output of every good cut to one half; R = 4k(1−k) × maximum | Sections 11–12, p. 54 | Revenue-maximizing point under linear schedules | Welfare at that point, which is far from optimal |
| Savings application | income tax should be partly but not wholly remitted on saving | Section 22, p. 59 | Application of equation (13) to saving vs spending | A dynamic optimal-tax result; Ramsey flags the short-horizon assumption |

## Interpretation notes

- The inverse-elasticity form most often quoted, a markup or tax proportional to 1/ε of demand, is equation (12)
  with infinitely elastic supply. Ramsey's own statement includes the supply elasticity, so the commonly cited rule
  is a special case of his.
- The proportional-reduction statement is the more general result. It holds with cross-price effects (section 8),
  whereas the inverse-elasticity form needs independent demands and supplies.
- Ramsey's model is a government taxing competitive markets. The regulated-monopoly reading, in which the
  "revenue" is a firm's fixed cost and the "tax" is its markup, comes from Boiteux (1956) and later work; the
  algebra carries over, but the application to a firm is not in Ramsey's paper.
- Ramsey assumes away distribution entirely. The rule minimizes the loss of total surplus, not the burden on any
  group, which is why later readers see it as a benchmark for efficiency rather than a complete prescription.

## Unanswered questions

- How large is "small"? Ramsey says the range of validity depends on the curvature of supply and demand schedules,
  which he could not measure, and gives no way to bound the error.
- How should elasticities be obtained in practice, and how should their sampling error enter the choice of rates?
  The paper treats them as known constants.
- What happens when the government cannot observe or tax some goods (leisure in particular) and cross-elasticities
  are large? Section 8 handles a restricted tax base in principle but gives no usable formula.
- How should equity weights enter? The paper excludes them by assumption.

## Items requiring expert verification

- The OCR text of the scan garbles equations (3), (3'), (11), (13) and (14). The extraction above relies on the
  verbal statements next to them; an expert should confirm the exact symbolic forms against a clean copy.
- The exact way the labor-supply elasticity enters equation (13) is illegible in the OCR and should be checked
  against the printed page.
- The relationship between Ramsey (1927) and Boiteux (1956), including whether Boiteux cites Ramsey and how his
  break-even multiplier is defined, could not be checked because Boiteux's paper was not read.
- No published correction or comment documenting an analytical error in Ramsey (1927) was found in the sources
  examined; this is a statement about what was checked, not a claim that none exists.

**Relation to this repository's rerun.** The rerun does not reproduce anything in the paper, which has no data. It
takes the inverse-elasticity form of equation (12), in Boiteux's regulated-monopoly reading, and asks whether the
Postal Service's fiscal 2025 markups line up with its own elasticity estimates; it also uses the Part II linear-demand
solution to compute Ramsey prices. Both steps assume independent demands, which is the case in which equation (12)
holds.
