from pathlib import Path
import plotly.express as px
import plotly.io as pio
from utils_metrics import load_and_compute

arts = load_and_compute()
range_label  = arts["range_label"]
sector_stats = arts["sector_stats"]
top_growth   = arts["top_growth"]
top_avg      = arts["top_avg"]
top_vol      = arts["top_vol"]

# --- Figures
fig_sector = px.bar(
    sector_stats.sort_values("avg_percent_growth", ascending=True),
    x="avg_percent_growth", y="sector", orientation="h",
    title=f"Average Sector Performance ({range_label})",
    labels={"avg_percent_growth":"Average % Growth","sector":"Sector"}
)

fig_risk = px.scatter(
    sector_stats, x="avg_volatility", y="avg_percent_growth", color="sector",
    title="Sector Risk vs Return", labels={"avg_volatility":"Average Volatility","avg_percent_growth":"Average % Growth"}
)

fig_growth = px.bar(
    top_growth.sort_values("percent_change", ascending=True),
    x="percent_change", y="label", orientation="h",
    title=f"Top 10 by % Growth ({range_label})",
    labels={"percent_change":"% Growth","label":"Company"}
)

fig_avg = px.bar(
    top_avg.sort_values("avg_closing_price", ascending=True),
    x="avg_closing_price", y="label", orientation="h",
    title=f"Top 10 by Average Closing Price ({range_label})",
    labels={"avg_closing_price":"Average Price (USD)","label":"Company"}
)

fig_vol = px.bar(
    top_vol.sort_values("volatility", ascending=True),
    x="volatility", y="label", orientation="h",
    title=f"Top 10 by Volatility ({range_label})",
    labels={"volatility":"Std Dev of Price","label":"Company"}
)

# --- Bundle into one HTML with tabs
titles = ["Sector Performance","Risk vs Return","Top 10 % Growth","Top 10 Avg Price","Top 10 Volatility"]
figs = [fig_sector, fig_risk, fig_growth, fig_avg, fig_vol]

divs = []
for i, f in enumerate(figs):
    html = pio.to_html(f, full_html=False, include_plotlyjs=False, div_id=f"fig{i}")
    style = "" if i == 0 else "display:none;"
    divs.append(f'<div id="panel{i}" style="{style}">{html}</div>')

buttons = "".join([f'<button class="tabbtn" onclick="showPanel({i})">{t}</button>' for i, t in enumerate(titles)])

template = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>S&P 500 Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.29.1.min.js"></script>
<style>
 body {{ font-family: Arial, sans-serif; margin: 16px; }}
 .tabbtn {{ margin:4px; padding:8px 12px; border:1px solid #ccc; background:#f7f7f7; cursor:pointer; }}
 .tabbtn:hover {{ background:#eee; }}
 .wrap {{ max-width: 1200px; }}
</style>
</head>
<body>
<div class="wrap">
  <h2>S&amp;P 500 Interactive Dashboard (Jan–Jun 2025)</h2>
  <p>Date range: <b>{arts['range_label']}</b></p>
  <div>{buttons}</div>
  {"".join(divs)}
</div>
<script>
function showPanel(i){{
  const n = {len(figs)};
  for(let k=0;k<n;k++) {{
    const el = document.getElementById('panel'+k);
    if (el) el.style.display = (k===i)?'':'none';
  }}
}}
</script>
</body>
</html>
"""

Path("dashboard.html").write_text(template, encoding="utf-8")
print("✅ Wrote dashboard.html")
