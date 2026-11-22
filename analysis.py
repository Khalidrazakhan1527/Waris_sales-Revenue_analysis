"""Clean retail data, run planned hypothesis tests, and build the offline report."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent
TEXT = ["Order ID", "Region", "State", "Category", "Sub-Category", "Segment",
        "Product ID", "Product Name"]
NUMERIC = ["Sales", "Quantity", "Discount", "Profit"]
FIELDS = ["Order Date", *TEXT, *NUMERIC]
ITEMS = ["speed_1", "speed_2", "quality_1", "quality_2", "usefulness_1",
         "usefulness_2", "ease_1", "ease_2"]


def clean(path):
    raw = pd.read_csv(path, encoding="cp1252")
    data = raw[FIELDS].copy()
    for field in TEXT:
        data[field] = data[field].astype("string").str.strip().replace("", pd.NA)
    for field in NUMERIC:
        data[field] = pd.to_numeric(data[field], errors="coerce").replace(
            [np.inf, -np.inf], np.nan)
    dates = data["Order Date"].astype("string").str.strip()
    data["Order Date"] = pd.to_datetime(dates, format="%Y-%m-%d", errors="coerce")
    data["Order Date"] = data["Order Date"].fillna(
        pd.to_datetime(dates, format="%m/%d/%Y", errors="coerce"))
    data = data.dropna()
    data = data[data.Sales.gt(0) & data.Quantity.gt(0) &
                data.Quantity.mod(1).eq(0) & data.Discount.between(0, 1)]
    valid_count = len(data)
    # Order lines can legitimately repeat once identifying fields are removed.
    dedup_fields = FIELDS
    if "Row ID" in raw:
        data = data.assign(row_id=raw.loc[data.index, "Row ID"])
        dedup_fields = [*FIELDS, "row_id"]
    data = data.drop_duplicates(subset=dedup_fields)
    if "row_id" in data and data.row_id.dropna().duplicated().any():
        raise ValueError("Conflicting records share a Row ID. Resolve before analysis.")
    if data.empty:
        raise ValueError("No valid sales rows.")
    if data.groupby("Order ID")["Region"].nunique().gt(1).any():
        raise ValueError("An order appears in multiple regions.")
    return data[FIELDS].sort_values("Order Date"), {
        "input_rows": len(raw), "invalid_rows": len(raw) - valid_count,
        "duplicates_removed": valid_count - len(data), "retained_rows": len(data)}


def result(statistic, p):
    return {"statistic": float(statistic), "p_value": float(p)} if (
        np.isfinite(statistic) and np.isfinite(p)) else {"status": "Undefined"}


def sales_tests(data):
    orders = data.groupby(["Region", "Order ID"], as_index=False).Sales.sum()
    groups = [group.Sales.to_numpy() for _, group in orders.groupby("Region")]
    anova = {"status": "Requires at least two regions with multiple orders"}
    levene = anova
    if len(groups) >= 2 and all(len(group) > 1 for group in groups):
        f, p = stats.f_oneway(*groups)
        anova = result(f, p)
        anova.update(df_between=len(groups)-1, df_within=len(orders)-len(groups))
        levene = result(*stats.levene(*groups, center="median"))
    margin = data.Profit / data.Sales
    correlation = regression = {"status": "Requires varying discount and margin"}
    if len(data) >= 3 and data.Discount.nunique() > 1 and margin.nunique() > 1:
        correlation = result(*stats.pearsonr(data.Discount, margin, alternative="less"))
        fit = stats.linregress(data.Discount, margin, alternative="less")
        regression = dict(slope=float(fit.slope), intercept=float(fit.intercept),
                          r_squared=float(fit.rvalue**2), p_value=float(fit.pvalue))
    return {"H01_ANOVA_order_revenue": anova, "Levene_median": levene,
            "regional_order_counts": orders.groupby("Region").size().to_dict(),
            "H02_Pearson_one_sided": correlation, "H02_regression_one_sided": regression,
            "discount_quantity_Pearson_two_sided": (
                result(*stats.pearsonr(data.Discount, data.Quantity))
                if len(data) >= 3 and data.Discount.nunique() > 1
                and data.Quantity.nunique() > 1 else {"status": "Insufficient variation"})}


def survey(path):
    if path is None:
        return {"status": "Awaiting collected responses", "n": 0}
    raw = pd.read_csv(path)
    scores = raw[ITEMS].apply(pd.to_numeric, errors="coerce")
    scores = scores[scores.isin([1, 2, 3, 4, 5]).all(axis=1)]
    if len(scores) < 2:
        return {"status": "Fewer than two complete responses", "n": len(scores),
                "excluded": len(raw)-len(scores)}
    decision = scores[ITEMS[:4]]
    composite = decision.mean(axis=1)

    def alpha(items):
        variance = items.sum(axis=1).var(ddof=1)
        k = items.shape[1]
        return float(k/(k-1)*(1-items.var(ddof=1).sum()/variance)) if variance else None

    def describe(series):
        return {"mean": float(series.mean()), "sd": float(series.std(ddof=1))}

    test = result(*stats.ttest_1samp(composite, 3, alternative="greater")) if (
        composite.std(ddof=1) > 0) else {"status": "Zero variance in composite"}
    return {"n": len(scores), "excluded": len(raw)-len(scores),
            "decision_composite": describe(composite), "cronbach_alpha_decision": alpha(decision),
            "H03_one_sided_t_vs_3": test,
            "items": {item: describe(scores[item]) for item in ITEMS},
            "usefulness": describe(scores[ITEMS[4:6]].mean(axis=1)),
            "ease": describe(scores[ITEMS[6:]].mean(axis=1))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sales", type=Path)
    parser.add_argument("--survey", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "output")
    parser.add_argument("--source", default="User-supplied retail data")
    args = parser.parse_args()
    data, audit = clean(args.sales)
    data["Order Date"] = data["Order Date"].dt.strftime("%Y-%m-%d")
    args.output.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output / "sales_clean.csv", index=False)
    findings = {"source": args.source, "cleaning": audit, "sales_tests": sales_tests(data),
                "survey": survey(args.survey)}
    (args.output / "statistical_results.json").write_text(json.dumps(findings, indent=2,
                                                                     allow_nan=False))
    payload = json.dumps({"data": data.to_numpy().tolist(), "findings": findings},
                         ensure_ascii=True, allow_nan=False).replace("<", "\\u003c")
    template = (ROOT / "dashboard.template.html").read_text()
    (args.output / "Sales_Revenue_Dashboard.html").write_text(
        template.replace("/* PROJECT_DATA */", payload), encoding="utf-8")
    print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
