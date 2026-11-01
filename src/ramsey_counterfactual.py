"""What Ramsey prices would look like at the Postal Service, and what they would save.

Extension to src/ramsey_test.py. Each market-dominant product's demand is calibrated at its FY2025
point (revenue, volume-variable cost, long-run elasticity) and prices are re-solved two ways:

  Scenario A, same contribution: Ramsey prices that raise exactly the FY2025 contribution
              (revenue minus volume-variable cost) of the 27 products, compared with actual prices.
  Scenario B, break even:      Ramsey prices that also close the FY2025 gap between total costs and
              total revenue (Boiteux's budget constraint), compared with an across-the-board increase.

Main demand form is linear, Ramsey's own Part II case, where the optimum lowers every product's
quantity by the same proportion k from its marginal-cost level. Constant-elasticity demand is the
robustness check. Prices are indexed to 1.00 at FY2025 levels, so a product's quantity is measured in
dollars of FY2025 revenue and its marginal cost c is volume-variable cost divided by revenue.

Run src/ramsey_test.py first; this reads results/products.csv and results/usps_totals.csv.

Outputs (results/): counterfactual_products.csv, counterfactual_summary.csv, ramsey_prices.png

Usage:
    python src/ramsey_counterfactual.py
"""

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"


# ---------- linear demand: q = R (1 - e (p - 1)), so dq/dp = -e R and q(1) = R ----------

def lin_q(p, d):
    return d.R * (1 - d.e * (p - 1))


def lin_dcs(p, d):
    """Change in consumer surplus moving from p = 1 to p (exact for linear demand)."""
    return -(p - 1) * (d.R + lin_q(p, d)) / 2


def lin_dwl(p, d):
    """Deadweight loss relative to pricing at marginal cost: the Harberger triangle 0.5 * b * (p - c)^2."""
    return 0.5 * d.e * d.R * (p - d.c) ** 2


def lin_ramsey(d, target):
    """Ramsey Part II: quantities fall by a common proportion k from their marginal-cost level x_bar."""
    b = d.e * d.R
    xbar = lin_q(d.c, d)
    S = (xbar ** 2 / b).sum()
    if target > S / 4:
        raise ValueError("target exceeds the maximum contribution (k = 1/2)")
    k = (1 - np.sqrt(1 - 4 * target / S)) / 2
    return d.c + k * xbar / b, k, S / 4


def lin_uniform(d, target):
    contrib = lambda th: ((th - d.c) * lin_q(th, d)).sum() - target
    th = brentq(contrib, 0.5, 1 / d.e.max() + 1 - 1e-6)
    return pd.Series(th, index=d.index)


# ---------- constant elasticity: q = R p^(-e) ----------

def ce_q(p, d):
    return d.R * p ** (-d.e)


def ce_dcs(p, d):
    out = np.where(np.isclose(d.e, 1), -d.R * np.log(p), d.R / (1 - d.e) * (1 - p ** (1 - d.e)))
    return pd.Series(out, index=d.index)


def ce_ramsey(d, target):
    """(p - c)/p = lambda / e for every product, lambda chosen to hit the target."""
    price = lambda lam: d.c / (1 - lam / d.e)
    contrib = lambda lam: ((price(lam) - d.c) * ce_q(price(lam), d)).sum() - target
    lam = brentq(contrib, 1e-9, d.e.min() * (1 - 1e-9))
    return price(lam), lam


def ce_uniform(d, target):
    contrib = lambda th: ((th - d.c) * ce_q(th, d)).sum() - target
    return pd.Series(brentq(contrib, 0.5, 20), index=d.index)


def revenue_per_piece():
    """FY2025 revenue per piece for mail products, from the PCRA report (Cost1 sheet, column D)."""
    raw = pd.read_excel(RAW / "Public_FY25CRAReport.xlsx", sheet_name="Cost1", header=None)
    rows, section = [], None
    for _, r in raw.iterrows():
        if not isinstance(r[1], str):
            continue
        name = re.sub(r"\s*\(note \d\)", "", r[1].strip()).rstrip(":").strip()
        if name in ("First-Class Mail", "USPS Marketing Mail", "Periodicals", "Package Services"):
            section = name
            continue
        rows.append({"section": section, "product": name, "rev_per_piece": pd.to_numeric(r[9], errors="coerce")})
    return pd.DataFrame(rows).dropna()


def main():
    p = pd.read_csv(OUT / "products.csv")
    totals = pd.read_csv(OUT / "usps_totals.csv").set_index("item").value_m
    print(f"Loaded {len(p)} products from results/products.csv")

    d = pd.DataFrame({"R": p.revenue_m, "c": p.vv_cost_m / p.revenue_m, "e": p.elasticity.abs()})
    current_contrib = (d.R * (1 - d.c)).sum()
    gap = totals["Total costs"] - totals["All revenue including investment income"]
    targets = {"A_same_contribution": current_contrib, "B_break_even": current_contrib + gap}
    print(f"FY2025 contribution of these products: ${current_contrib:,.0f}M; "
          f"FY2025 shortfall of all revenue below all costs: ${gap:,.0f}M")

    ones = pd.Series(1.0, index=d.index)
    prod = p[["section", "product", "revenue_m", "elasticity", "lerner", "statutory"]].copy()
    summary = []

    def record(scenario, demand, policy, price, q, dcs, extra=None):
        contrib = ((price - d.c) * q).sum()
        dwl = lin_dwl(price, d).sum() if demand == "linear" else np.nan
        row = {"scenario": scenario, "demand": demand, "policy": policy, "contribution_m": contrib,
               "consumer_surplus_change_m": dcs.sum(), "deadweight_loss_m": dwl,
               "revenue_m": (price * q).sum(), "quantity_change_pct": 100 * (q.sum() / d.R.sum() - 1)}
        row.update(extra or {})
        summary.append(row)

    # Actual FY2025 prices (the benchmark in Scenario A)
    record("A_same_contribution", "linear", "actual FY2025 prices", ones, d.R, ones * 0)

    for scen, T in targets.items():
        pr, k, cmax = lin_ramsey(d, T)
        record(scen, "linear", "Ramsey", pr, lin_q(pr, d), lin_dcs(pr, d),
               {"ramsey_k": k, "ramsey_lambda": np.nan, "max_contribution_m": cmax})
        prod[f"{scen}_lin_ramsey_price"] = pr
        prod[f"{scen}_lin_ramsey_markup"] = (pr - d.c) / pr
        prc, lam = ce_ramsey(d, T)
        record(scen, "constant elasticity", "Ramsey", prc, ce_q(prc, d), ce_dcs(prc, d),
               {"ramsey_lambda": lam})
        prod[f"{scen}_ce_ramsey_price"] = prc
        # statutory preferred rates held at FY2025 prices, Ramsey over the remaining products
        free = ~p.statutory
        fixed_contrib = (d.R * (1 - d.c))[~free].sum()
        prf, kf, _ = lin_ramsey(d[free], T - fixed_contrib)
        prf = prf.reindex(d.index).fillna(1.0)
        record(scen, "linear", "Ramsey, statutory rates held fixed", prf, lin_q(prf, d), lin_dcs(prf, d),
               {"ramsey_k": kf})
        prod[f"{scen}_lin_ramsey_fixed_price"] = prf
        if scen == "B_break_even":
            th = lin_uniform(d, T)
            record(scen, "linear", "uniform increase", th, lin_q(th, d), lin_dcs(th, d),
                   {"uniform_increase_pct": 100 * (th.iloc[0] - 1)})
            thc = ce_uniform(d, T)
            record(scen, "constant elasticity", "uniform increase", thc, ce_q(thc, d), ce_dcs(thc, d),
                   {"uniform_increase_pct": 100 * (thc.iloc[0] - 1)})

    rpp = revenue_per_piece()
    prod = prod.merge(rpp, on=["section", "product"], how="left")
    prod["vv_cost_per_piece"] = prod.rev_per_piece * (1 - prod.lerner)
    prod["contribution_per_piece"] = prod.rev_per_piece * prod.lerner
    prod["A_ramsey_price_per_piece"] = prod.rev_per_piece * prod.A_same_contribution_lin_ramsey_price
    prod["B_ramsey_price_per_piece"] = prod.rev_per_piece * prod.B_break_even_lin_ramsey_price
    prod.to_csv(OUT / "counterfactual_products.csv", index=False, float_format="%.6g")

    s = pd.DataFrame(summary)
    base_dwl = s.loc[(s.policy == "actual FY2025 prices"), "deadweight_loss_m"].iloc[0]
    s["dwl_saving_vs_actual_m"] = base_dwl - s.deadweight_loss_m
    s["dwl_saving_vs_actual_pct"] = 100 * s.dwl_saving_vs_actual_m / base_dwl
    for dem in s.demand.unique():
        uni = s[(s.scenario == "B_break_even") & (s.demand == dem) & (s.policy == "uniform increase")]
        rows = (s.scenario == "B_break_even") & (s.demand == dem)
        s.loc[rows, "cs_gain_vs_uniform_m"] = s.loc[rows, "consumer_surplus_change_m"] - uni.consumer_surplus_change_m.iloc[0]
    s.to_csv(OUT / "counterfactual_summary.csv", index=False, float_format="%.6g")
    print(f"Products with a revenue-per-piece figure: {prod.rev_per_piece.notna().sum()} of {len(prod)}")
    print("\nCounterfactual summary ($ millions):")
    print(s.round(3).to_string(index=False))

    # Figure: price index under Ramsey (Scenario A, linear) by product
    f = prod.sort_values("A_same_contribution_lin_ramsey_price")
    f = f.assign(label=f["product"].str.replace("High Density and Saturation", "HD/Sat")
                 .str.replace("Outbound Single-Piece First-Class Mail International", "Outbound International FCM")
                 + " (" + f.section.str.replace("USPS Marketing Mail", "Mktg").str.replace("First-Class Mail", "FCM")
                 .str.replace("Package Services", "Pkg").str.replace("Ancillary Services", "Anc")
                 .str.replace("Special Services", "Spec").str.replace("Periodicals", "Per") + ")")
    fig, ax = plt.subplots(figsize=(8, 7.5))
    chg = 100 * (f.A_same_contribution_lin_ramsey_price - 1)
    colors = np.where(chg >= 0, "#c44536", "#2a6f97")
    ax.barh(f.label, chg, color=colors)
    ax.axvline(0, color="#333333", lw=0.8)
    ax.set_xlabel("Change in price under Ramsey pricing, same total contribution (%)")
    ax.set_title("Ramsey prices for USPS market-dominant products (FY2025, linear demand)", fontsize=10)
    ax.tick_params(axis="y", labelsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "ramsey_prices.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
