"""Annual environmental trend analysis. Use complete calendar years only.

Mann-Kendall via scipy kendalltau(year, annual value); for no ties the two-sided
p-value approximates MK; ties are supported by scipy. Sen slope via theilslopes.
Not corrected for serial correlation or measurement/coverage uncertainty.
"""
from collections import defaultdict
from math import isfinite
from scipy.stats import linregress, kendalltau, theilslopes

class TrendValidationError(ValueError):
    pass

def analyze_dataset(dataset, min_complete_years=8):
    metadata = dataset["metadata"]
    variable = metadata.get("variable")
    unit = metadata.get("normalized_unit")
    aggregation = {"temperature": ("mean", "degC"), "rainfall": ("sum", "mm/month"), "soil_moisture": ("mean", None)}.get(variable)
    if aggregation is None:
        raise TrendValidationError("Unsupported variable")
    if variable == "rainfall" and unit != "mm/month":
        raise TrendValidationError("Rainfall requires normalized monthly depth in mm/month")
    if variable == "temperature" and unit != "degC":
        raise TrendValidationError("Temperature requires normalized Celsius")
    groups = defaultdict(dict)
    for point in dataset["observations"]:
        year, month = map(int, point["date"][:7].split("-"))
        value = float(point["value"])
        if not isfinite(value):
            raise TrendValidationError("Non-finite observation")
        if month in groups[year]:
            raise TrendValidationError("Duplicate month")
        groups[year][month] = value
    full_years = sorted(y for y, months in groups.items() if len(months) == 12 and set(months) == set(range(1, 13)))
    excluded = [{"year":y,"observed_months":len(months),"reason":"incomplete calendar year"} for y, months in sorted(groups.items()) if y not in full_years]
    if len(full_years) < min_complete_years:
        raise TrendValidationError(f"At least {min_complete_years} complete calendar years required; found {len(full_years)}")
    method, expected_unit = aggregation
    if expected_unit and unit != expected_unit:
        raise TrendValidationError("Normalized unit inconsistent with aggregation")
    annual = []
    for year in full_years:
        values = list(groups[year].values())
        annual.append({"year":year,"value":round((sum(values)/12 if method=="mean" else sum(values)),9)})
    x = [p["year"] for p in annual]
    y = [p["value"] for p in annual]
    if len(set(y)) < 2:
        raise TrendValidationError("Annual values are constant; trend significance and R-squared are undefined")
    regression = linregress(x, y)
    tau, mk_p = kendalltau(x, y)
    sen = theilslopes(y, x, alpha=0.95)
    slope=float(regression.slope)
    for p in annual:
        p["fitted"] = round(float(regression.intercept + slope * p["year"]),9)
    slope_unit = {"temperature":"degC/year", "rainfall":"mm/year²", "soil_moisture":f"{unit}/year"}[variable]
    significant = bool(mk_p < 0.05)
    direction = "increasing" if sen.slope > 0 else "decreasing" if sen.slope < 0 else "flat"
    label = "statistically significant" if significant else "not statistically significant"
    return {
        "dataset_id": metadata["id"], "variable":variable, "region":metadata["region"],
        "unit": ("mm/year" if variable == "rainfall" else unit), "annual_aggregation":method,"slope_unit":slope_unit,
        "included_years":len(full_years), "first_year":x[0], "last_year":x[-1],
        "excluded_years":excluded, "annual_series":annual,
        "linear_regression":{"slope_per_year":slope,"intercept":float(regression.intercept),"r_squared":float(regression.rvalue**2),"p_value":float(regression.pvalue),"standard_error":float(regression.stderr)},
        "mann_kendall":{"kendall_tau":float(tau),"p_value":float(mk_p),"significant_at_0_05":significant,"method":"Kendall rank test on annual values (MK-style, uncorrected)"},
        "sen_slope":{"slope_per_year":float(sen.slope),"confidence_interval_95":{"lower":float(sen.low_slope),"upper":float(sen.high_slope)}},
        "interpretation":f"For {metadata['region']}, the complete-year {variable} series ({x[0]}–{x[-1]}) shows a {direction} Sen slope of {sen.slope:.4f} {slope_unit}; the annual rank trend is {label} (two-sided p={mk_p:.4g}). This is not a causal attribution or a national estimate.",
        "limitations":["Annual aggregation excludes every incomplete year (including 2025 if only January is available).","The rank-test p-value does not adjust for serial autocorrelation; significant results require cautious interpretation.","Statistical trend does not imply causation or prove a climate driver.","Data coverage and spatial grid limit representativeness; see source metadata."],
        "provenance":{"source_url":metadata["source_url"],"source_file_sha256":metadata.get("source_file_sha256"),"verification_status":metadata.get("verification_status"),"coverage_warning":metadata.get("coverage_warning")}
    }
