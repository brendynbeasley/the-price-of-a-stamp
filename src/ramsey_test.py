"""Ramsey's inverse-elasticity rule tested on the US Postal Service's FY2025 market-dominant prices.

Ramsey (1927) and Boiteux (1956) show that a seller who must cover a fixed budget with the least loss
of consumer welfare sets each product's Lerner index L = (p - c) / p in proportion to the inverse of its
own-price elasticity, L_i = lambda / |e_i|, with one lambda for every product. The Postal Service is the
textbook case: a public monopoly that must recover large institutional (overhead) costs from markups.

Inputs (all in data/raw/, public filings in Postal Regulatory Commission dockets ACR2025):
    Public_FY25CRA_Expanded.xlsx           revenue, attributable and volume-variable cost by product
    DemandEquationTables_md_Jan2026.docx   Postal Service long-run own-price elasticities and t-statistics
    vf_md_Jan2026.xlsx                     FY2025 volumes for each demand category (used as weights)

Outputs (results/): products.csv, demand_categories.csv, ramsey_tests.csv, markup_vs_elasticity.png

Usage:
    python src/ramsey_test.py
"""

import re
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

# Each PCRA product (section, row label) and the demand categories whose elasticities describe it.
# Keys of the demand side are the two header rows of vf_md_Jan2026.xlsx, joined with " | ".
# Political mail categories cut across the Marketing Mail products and are left out; the
# Postal Service's own mail and free mail for the blind have no price and no elasticity.
PRODUCTS = {
    ("First-Class Mail", "Single-Piece Letters"): ["First-Class SP | Stamped Letters", "First-Class SP | Metered Letters"],
    ("First-Class Mail", "Single-Piece Postcards"): ["First-Class | SP Cards"],
    ("First-Class Mail", "Presort Letters"): ["First-Class | WS Letters"],
    ("First-Class Mail", "Presort Cards"): ["First-Class | WS Cards"],
    ("First-Class Mail", "Flats"): ["First-Class | SP Flats", "First-Class | WS Flats"],
    ("First-Class Mail", "Outbound Single-Piece First-Class Mail International"): ["Outbound | International"],
    ("USPS Marketing Mail", "High Density and Saturation Letters"): ["Comm Mktg | HD/Sat Letters", "NP Mktg | HD/Sat Letters"],
    ("USPS Marketing Mail", "High Density and Saturation Flats and Parcels"): ["Comm Mktg | HD/Sat Flats", "NP Mktg | HD/Sat Flats"],
    ("USPS Marketing Mail", "Carrier Route"): ["Comm Mktg | Flats & Basic CR", "NP Mktg | Flats & Basic CR"],
    ("USPS Marketing Mail", "Letters"): ["Comm Mktg | Letters", "NP Mktg | Letters"],
    ("USPS Marketing Mail", "Flats"): ["Comm Mktg | Flats & Basic CR", "NP Mktg | Flats & Basic CR"],
    ("USPS Marketing Mail", "Parcels"): ["Marketing | Parcels"],
    ("USPS Marketing Mail", "Every Door Direct Mail Retail"): ["Comm Mktg | EDDM"],
    ("Periodicals", "In County"): ["Periodical | In-County"],
    ("Periodicals", "Outside County"): ["Periodical | Regular", "Periodical | NP & Classroom"],
    ("Package Services", "Alaska Bypass"): ["Alaska | Bypass"],
    ("Package Services", "Bound Printed Matter Flats"): ["BPM | Flats"],
    ("Package Services", "Bound Printed Matter Parcels"): ["BPM | Parcels"],
    ("Package Services", "Media and Library Mail"): ["Media & Library | Rate Mail"],
    ("Ancillary Services", "Certified Mail"): ["Certified | Mail"],
    ("Ancillary Services", "COD"): ["COD | Mail"],
    ("Ancillary Services", "Insurance"): ["Insured | Mail"],
    ("Ancillary Services", "Registered Mail"): ["Registered | Mail"],
    ("Ancillary Services", "Stamped Envelopes"): ["Stamped | Envelopes"],
    ("Ancillary Services", "Stamped Cards"): ["Stamped | Cards"],
    ("Special Services", "Money Orders"): ["Money | Orders"],
    ("Special Services", "Post Office Box Service"): ["Post Office | Boxes"],
}

# Products whose prices are held down by statute (39 U.S.C. 3626 preferred rates, the Alaska Bypass
# rule tying rates to parcel post), so Ramsey's rule cannot apply to them. Used in a robustness check.
STATUTORY = {("Periodicals", "In County"), ("Periodicals", "Outside County"),
             ("Package Services", "Media and Library Mail"), ("Package Services", "Alaska Bypass")}

# Section headers in the PCRA sheet, used to tell apart rows such as "Flats" and "Letters".
SECTIONS = ["First-Class Mail", "USPS Marketing Mail", "Periodicals", "Package Services",
            "Ancillary Services", "Special Services", "COMPETITIVE MAIL AND SERVICES"]


def load_pcra():
    """Revenue, attributable cost and volume-variable cost ($ millions) for every PCRA row, by section."""
    raw = pd.read_excel(RAW / "Public_FY25CRA_Expanded.xlsx", sheet_name="Summary", header=None)
    rows, section = [], None
    for _, r in raw.iterrows():
        label = r[1]
        if not isinstance(label, str):
            continue
        name = re.sub(r"\s*\(note \d\)", "", label.strip()).rstrip(":").strip()
        if name in SECTIONS:
            section = name
            continue
        rows.append({"section": section, "product": name, "revenue": r[3], "attrib_cost": r[5], "vv_cost": r[7]})
    pcra = pd.DataFrame(rows)
    for c in ["revenue", "attrib_cost", "vv_cost"]:
        pcra[c] = pd.to_numeric(pcra[c], errors="coerce")
    print(f"PCRA FY2025: {len(pcra)} labelled rows read from Public_FY25CRA_Expanded.xlsx")
    return pcra


def docx_paragraphs(path):
    """Plain text of every paragraph (including table cells) in a .docx file, in order."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    paras = re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S)
    return [re.sub(r"\s+", " ", "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))).strip() for p in paras]


def load_elasticity_tables():
    """Long-run own-price elasticity and its t-statistic for each demand equation in the Jan 2026 filing."""
    paras = [p for p in docx_paragraphs(RAW / "DemandEquationTables_md_Jan2026.docx") if p]
    out, title = [], None
    for i, p in enumerate(paras):
        if p.startswith("ECONOMETRIC DEMAND EQUATION FOR"):
            title = p.replace("ECONOMETRIC DEMAND EQUATION FOR", "").strip()
        elif p == "Long-Run" and title:
            out.append({"equation": title, "lr_elasticity": float(paras[i + 1]), "lr_t": float(paras[i + 2])})
            title = None
    tab = pd.DataFrame(out)
    print(f"Demand tables: {len(tab)} equations with a long-run own-price elasticity")
    return tab


def load_demand_categories():
    """FY2025 volume and long-run elasticity for each demand category in the volume-forecast workbook."""
    vols = pd.read_excel(RAW / "vf_md_Jan2026.xlsx", sheet_name="HistVols", header=None)
    el = pd.read_excel(RAW / "vf_md_Jan2026.xlsx", sheet_name="Elasts", header=None)
    sum_row = el.index[el[0].astype(str).str.startswith("SUM")][0]
    base_row = vols.index[vols[0].astype(str).str.startswith("Base Volumes")][0]
    cats = []
    for j in range(1, vols.shape[1]):
        if pd.isna(vols.iloc[2, j]):
            continue
        key = f"{str(vols.iloc[2, j]).strip()} | {str(vols.iloc[3, j]).strip()}"
        cats.append({"category": key, "fy25_volume_m": float(vols.iloc[base_row, j]),
                     "lr_elasticity_vf": float(el.iloc[sum_row, j])})
    cats = pd.DataFrame(cats)
    print(f"Volume forecasts: {len(cats)} demand categories with FY2025 base volumes")
    return cats


def attach_t_stats(cats, tables):
    """Match each workbook category to its equation table by elasticity value (they are the same estimate)."""
    t = []
    for _, r in cats.iterrows():
        d = (tables.lr_elasticity - r.lr_elasticity_vf).abs()
        ok = d.idxmin() if len(d) and d.min() < 0.0006 else None
        t.append(tables.loc[ok, ["equation", "lr_t"]].tolist() if ok is not None else [None, np.nan])
    cats[["equation", "lr_t"]] = pd.DataFrame(t, index=cats.index)
    cats["lr_se"] = (cats.lr_elasticity_vf / cats.lr_t).abs()
    return cats


def build_products(pcra, cats):
    """One row per product with its markup and a volume-weighted long-run elasticity."""
    c = cats.set_index("category")
    rows = []
    for (section, product), keys in PRODUCTS.items():
        hit = pcra[(pcra.section == section) & (pcra["product"] == product)]
        if len(hit) != 1:
            raise ValueError(f"PCRA row not found once: {section} / {product}")
        h = hit.iloc[0]
        w = c.loc[keys, "fy25_volume_m"] / c.loc[keys, "fy25_volume_m"].sum()
        eps = float((w * c.loc[keys, "lr_elasticity_vf"]).sum())
        se = float(np.sqrt((w ** 2 * c.loc[keys, "lr_se"] ** 2).sum()))
        rows.append({"section": section, "product": product, "revenue_m": h.revenue, "attrib_cost_m": h.attrib_cost,
                     "vv_cost_m": h.vv_cost, "elasticity": eps, "elasticity_se": se,
                     "demand_categories": "; ".join(keys), "statutory": (section, product) in STATUTORY})
    p = pd.DataFrame(rows)
    p["cost_coverage_pct"] = 100 * p.revenue_m / p.attrib_cost_m
    p["lerner"] = (p.revenue_m - p.vv_cost_m) / p.revenue_m             # markup over marginal (volume-variable) cost
    p["lerner_attrib"] = (p.revenue_m - p.attrib_cost_m) / p.revenue_m  # markup over attributable cost
    p["inv_elasticity"] = 1 / p.elasticity.abs()
    p["ramsey_number"] = p.lerner * p.elasticity.abs()                  # lambda_i, equal for all i under Ramsey
    p["elasticity_t"] = p.elasticity / p.elasticity_se
    return p


def ramsey_regressions(p):
    """L_i = a + b (1/|e_i|) + u. Ramsey: a = 0, b = lambda > 0, and L_i |e_i| the same for every product."""
    samples = {
        "All matched products": p,
        "Excluding statutory preferred rates": p[~p.statutory],
        "Elasticity significant (|t| >= 1.96)": p[p.elasticity_t.abs() >= 1.96],
    }
    rows = []
    for name, d in samples.items():
        for ycol, ylab in [("lerner", "volume-variable cost"), ("lerner_attrib", "attributable cost")]:
            for wname, w in [("unweighted", None), ("revenue-weighted", d.revenue_m)]:
                X = sm.add_constant(d.inv_elasticity)
                m = (sm.WLS(d[ycol], X, weights=w) if w is not None else sm.OLS(d[ycol], X)).fit(cov_type="HC1")
                rho, rho_p = stats.spearmanr(d.inv_elasticity, d[ycol])
                rows.append({"sample": name, "markup_over": ylab, "weights": wname, "n": len(d),
                             "intercept": m.params["const"], "intercept_se": m.bse["const"],
                             "slope": m.params["inv_elasticity"], "slope_se": m.bse["inv_elasticity"],
                             "slope_p": m.pvalues["inv_elasticity"], "r2": m.rsquared,
                             "slope_ci_low": m.conf_int().loc["inv_elasticity", 0],
                             "slope_ci_high": m.conf_int().loc["inv_elasticity", 1],
                             "spearman_rho": rho, "spearman_p": rho_p})
    # log form, positive markups only: log L = a + b log(1/|e|); Ramsey predicts b = 1
    d = p[p.lerner > 0]
    m = sm.OLS(np.log(d.lerner), sm.add_constant(np.log(d.inv_elasticity))).fit(cov_type="HC1")
    rows.append({"sample": "Positive markups, log form", "markup_over": "volume-variable cost", "weights": "unweighted",
                 "n": len(d), "intercept": m.params["const"], "intercept_se": m.bse["const"],
                 "slope": m.params["inv_elasticity"], "slope_se": m.bse["inv_elasticity"],
                 "slope_p": 2 * stats.norm.sf(abs((m.params["inv_elasticity"] - 1) / m.bse["inv_elasticity"])),
                 "r2": m.rsquared, "slope_ci_low": m.conf_int().loc["inv_elasticity", 0],
                 "slope_ci_high": m.conf_int().loc["inv_elasticity", 1], "spearman_rho": np.nan, "spearman_p": np.nan})
    tests = pd.DataFrame(rows)
    tests.loc[tests["sample"] == "Positive markups, log form", "note"] = "slope_p tests slope = 1"
    return tests


def lambda_summary(p):
    """Spread of the Ramsey number L_i |e_i| across products, which Ramsey says should be zero."""
    out = []
    for name, d in [("All matched products", p), ("Excluding statutory preferred rates", p[~p.statutory])]:
        lam = d.ramsey_number
        wmean = np.average(lam, weights=d.revenue_m)
        out.append({"sample": name, "n": len(d), "lambda_mean": lam.mean(), "lambda_rev_weighted": wmean,
                    "lambda_min": lam.min(), "lambda_max": lam.max(), "lambda_sd": lam.std(ddof=1),
                    "share_revenue_lambda_within_25pct": d.revenue_m[(lam - wmean).abs() <= 0.25 * abs(wmean)].sum()
                    / d.revenue_m.sum()})
    return pd.DataFrame(out)


def plot(p, tests):
    fig, ax = plt.subplots(figsize=(8, 5.4))
    for stat, color, lab in [(False, "#2a6f97", "Other market-dominant products"),
                             (True, "#c44536", "Rates shaped by statute")]:
        d = p[p.statutory == stat]
        ax.scatter(d.inv_elasticity, d.lerner, s=20 + 120 * np.sqrt(d.revenue_m / p.revenue_m.max()),
                   color=color, alpha=0.75, label=lab, edgecolor="white", linewidth=0.6)
    lam = np.average(p.ramsey_number[~p.statutory], weights=p.revenue_m[~p.statutory])
    xs = np.linspace(0, min(p.inv_elasticity.max() * 1.05, 1 / lam), 100)
    ax.plot(xs, lam * xs, color="#555555", ls="--", lw=1.2,
            label=f"Ramsey line, L = {lam:.2f} / |e| (revenue-weighted, non-statutory)")
    for _, r in p.iterrows():
        if r.revenue_m > 1500 or r.lerner < 0 or r.inv_elasticity > 4 or r.inv_elasticity < 0.7:
            short = {"First-Class Mail": "FCM", "USPS Marketing Mail": "Mktg"}.get(r.section, "")
            name = (r["product"].replace("High Density and Saturation", "HD/Sat")
                    .replace("Outbound Single-Piece First-Class Mail International", "Outbound International"))
            ax.annotate(f"{short} {name}".strip(),
                        (r.inv_elasticity, r.lerner), fontsize=7, xytext=(4, 3), textcoords="offset points")
    ax.axhline(0, color="#999999", lw=0.6)
    ax.set_xlabel("Inverse of the long-run own-price elasticity, 1/|e|")
    ax.set_ylabel("Markup over volume-variable cost, (p - c)/p")
    ax.set_title("USPS market-dominant products, FY2025: markup against 1/|elasticity|")
    ax.set_ylim(-0.45, 1.02)
    ax.legend(fontsize=8, loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "markup_vs_elasticity.png", dpi=150)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    pcra = load_pcra()
    cats = attach_t_stats(load_demand_categories(), load_elasticity_tables())
    unmatched = cats[cats.equation.isna() & (cats.lr_elasticity_vf != 0)]
    print(f"Demand categories without a matching equation table: {len(unmatched)}")
    cats.to_csv(OUT / "demand_categories.csv", index=False, float_format="%.6g")

    used = {k for keys in PRODUCTS.values() for k in keys}
    dropped = cats[~cats.category.isin(used)].category.tolist()
    print(f"Demand categories used: {len(used)}; not used: {len(dropped)} ({', '.join(dropped)})")

    p = build_products(pcra, cats)
    md = pcra[pcra["product"] == "Total Market Dominant Mail and Services"].iloc[0]
    print(f"Products kept: {len(p)}, covering ${p.revenue_m.sum():,.0f}M of ${md.revenue:,.0f}M "
          f"market-dominant revenue ({100 * p.revenue_m.sum() / md.revenue:.1f}%)")
    p.to_csv(OUT / "products.csv", index=False, float_format="%.6g")

    tests = ramsey_regressions(p)
    tests.to_csv(OUT / "ramsey_tests.csv", index=False, float_format="%.6g")
    lam = lambda_summary(p)
    lam.to_csv(OUT / "lambda_summary.csv", index=False, float_format="%.6g")

    # whole-Postal-Service totals used in the write-up and in the counterfactual
    get = lambda name, col: float(pcra.loc[pcra["product"] == name, col].iloc[0])
    totals = pd.DataFrame([
        {"item": "Market-dominant revenue", "value_m": md.revenue},
        {"item": "Market-dominant attributable cost", "value_m": md.attrib_cost},
        {"item": "Market-dominant volume-variable cost", "value_m": md.vv_cost},
        {"item": "Competitive revenue", "value_m": get("Total Competitive Mail and Services", "revenue")},
        {"item": "Competitive attributable cost", "value_m": get("Total Competitive Mail and Services", "attrib_cost")},
        {"item": "All revenue including investment income", "value_m": pcra.loc[pcra["product"] == "Total", "revenue"].dropna().iloc[0]},
        {"item": "Institutional costs (All Other)", "value_m": get("All Other", "attrib_cost")},
        {"item": "Total costs", "value_m": pcra.loc[pcra["product"] == "Total", "attrib_cost"].dropna().iloc[-1]},
    ])
    shortfall = totals.value_m.iloc[7] - totals.value_m.iloc[5]
    totals.loc[len(totals)] = {"item": "Shortfall of all revenue below total costs", "value_m": shortfall}
    totals.to_csv(OUT / "usps_totals.csv", index=False, float_format="%.6g")
    plot(p, tests)

    print("\nRamsey test, all products, markup over volume-variable cost:")
    print(tests[(tests.markup_over == "volume-variable cost")].round(3).to_string(index=False))
    print("\nRamsey number L*|e|:")
    print(lam.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
