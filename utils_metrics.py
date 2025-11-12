from pathlib import Path
import pandas as pd
import datetime

DATA_PATH = "sp500_2025_h1.csv"   # adjust if different
SECTOR_CACHE = "sector_mapping.csv"

def _closing_cols(df):
    return [c for c in df.columns if c.endswith("_closing")]

def reorder_date(date_str):
    """Takes 'MM-DD-YYYY' and returns 'DD-MM-YYYY'."""
    parts = date_str.replace('_closing', '').split('-')
    if len(parts) == 3:
        month, day, year = parts
        return f"{day}-{month}-{year}"
    return date_str

def load_and_compute():
    """Loads data, maps sector (from cache), computes metrics, returns all artifacts."""
    df = pd.read_csv(DATA_PATH)

    closing_cols = _closing_cols(df)
    # figure out first/last closing columns text-only (no datetime headaches)
    def _parse_date_from_col(c):
        s = c.replace("_closing", "")
        try:
            return datetime.datetime.strptime(s, "%m-%d-%Y")
        except Exception:
            return None

    closing_cols = [c for c in df.columns if c.endswith('_closing')]
    closing_dates = pd.to_datetime([c.replace('_closing','') for c in closing_cols], dayfirst=True)

    sorted_pairs = sorted(zip(closing_dates, closing_cols), key=lambda x: x[0])
    first_close_col = sorted_pairs[0][1]
    last_close_col  = sorted_pairs[-1][1]

    range_label = f"{reorder_date(first_close_col)} → {reorder_date(last_close_col)}"

    # metrics (idempotent)
    if "avg_closing_price" not in df.columns:
        df["avg_closing_price"] = df[closing_cols].mean(axis=1)
    if "percent_change" not in df.columns:
        df["percent_change"] = ((df[last_close_col] - df[first_close_col]) / df[first_close_col]) * 100
    if "volatility" not in df.columns:
        df["volatility"] = df[closing_cols].std(axis=1, ddof=1)

    # sector mapping (from cached csv if present)
    if "sector" not in df.columns:
        if Path(SECTOR_CACHE).exists():
            smap = pd.read_csv(SECTOR_CACHE)
            mapdict = dict(zip(smap["ticker"], smap["sector"]))
            df["sector"] = df["ticker"].map(mapdict).fillna("Unknown")
        else:
            df["sector"] = "Unknown"

    # sector aggregates
    sector_perf = (
        df.groupby("sector", dropna=False)["percent_change"]
          .mean().reset_index().rename(columns={"percent_change":"avg_percent_growth"})
    )
    sector_vol = df.groupby("sector", dropna=False)["volatility"].mean().reset_index().rename(columns={"volatility":"avg_volatility"})
    sector_stats = sector_perf.merge(sector_vol, on="sector", how="outer")

    # top lists
    top_growth = df.nlargest(10, "percent_change")[["company_name","ticker","percent_change"]].copy()
    top_avg    = df.nlargest(10, "avg_closing_price")[["company_name","ticker","avg_closing_price"]].copy()
    top_vol    = df.nlargest(10, "volatility")[["company_name","ticker","volatility"]].copy()
    for tdf in (top_growth, top_avg, top_vol):
        tdf["label"] = tdf["company_name"] + " (" + tdf["ticker"] + ")"

    return {
        "df": df,
        "closing_cols": closing_cols,
        "first_close_col": first_close_col,
        "last_close_col": last_close_col,
        "range_label": range_label,
        "sector_stats": sector_stats,
        "top_growth": top_growth,
        "top_avg": top_avg,
        "top_vol": top_vol,
    }
