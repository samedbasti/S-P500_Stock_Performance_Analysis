import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime

df = pd.read_csv("sp500_2025_h1.csv")
df.info()
df.describe()
df.head()

#Getting the closing date of companies
def _closing_date_from_col(col):
    try:
        date_str = col.replace('_closing','')
        return pd.to_datetime(date_str, dayfirst=True)
    except Exception:
        return pd.NaT


closing_cols = [c for c in df.columns if c.endswith('_closing')]
closing_dates = pd.to_datetime([c.replace('_closing','') for c in closing_cols], dayfirst=True)

sorted_pairs = sorted(zip(closing_dates, closing_cols), key=lambda x: x[0])
first_close_col = sorted_pairs[0][1]
last_close_col  = sorted_pairs[-1][1]

df['percent_change'] = ((df[last_close_col] - df[first_close_col]) / df[first_close_col]) * 100
df['volatility'] = df[closing_cols].std(axis=1, ddof=1)

cache_path = "sector_mapping.csv"

sector_map = {}
try:
    smap = pd.read_csv(cache_path)
    sector_map = dict(zip(smap['ticker'], smap['sector']))
    print(f"Loaded cached sector mapping with {len(sector_map)} tickers.")
except Exception:
    print("No cached sector mapping found. Fetching from yfinance ...")
    unique_tickers = df['ticker'].dropna().unique().tolist()

    def norm(t):
        return t.replace('.', '-')

    for i, t in enumerate(unique_tickers, 1):
        yt = norm(t)
        try:
            info = yf.Ticker(yt).get_info()
            sector_map[t] = info.get('sector', 'Unknown') or 'Unknown'
        except Exception:
            sector_map[t] = 'Unknown'
        if i % 20 == 0:
            time.sleep(2)

    pd.DataFrame({'ticker': list(sector_map.keys()),
                  'sector': list(sector_map.values())}).to_csv(cache_path, index=False)
    print(f"Saved sector mapping to {cache_path}")

df['sector'] = df['ticker'].map(sector_map).fillna('Unknown')

sector_perf = (
    df.groupby('sector', dropna=False)['percent_change']
      .mean()
      .reset_index()
      .sort_values('percent_change', ascending=False)
)

sector_vol = (
    df.groupby('sector', dropna=False)['volatility']
      .mean()
      .reset_index()
)

sector_stats = sector_perf.merge(sector_vol, on='sector', how='outer')
sector_stats.rename(columns={'percent_change':'avg_percent_growth',
                             'volatility':'avg_volatility'}, inplace=True)

print("\nSector stats (avg % growth and avg volatility):")
print(sector_stats)

def reorder_date(date_str):
    """Takes 'MM-DD-YYYY' and returns 'DD-MM-YYYY'."""
    parts = date_str.replace('_closing', '').split('-')
    if len(parts) == 3:
        month, day, year = parts
        return f"{day}-{month}-{year}"
    return date_str

plt.figure(figsize=(10,6))
sns.barplot(x='avg_percent_growth', y='sector', data=sector_stats.sort_values('avg_percent_growth', ascending=False))
plt.title(f'Average Sector Performance ({reorder_date(first_close_col)} → {reorder_date(last_close_col)})')
plt.xlabel('Average % Growth')
plt.ylabel('Sector')
plt.tight_layout()
plt.show()

plt.figure(figsize=(8,6))
sns.scatterplot(data=sector_stats, x='avg_volatility', y='avg_percent_growth', hue='sector', s=120)
for _, r in sector_stats.iterrows():
    plt.text(r['avg_volatility']*1.005, r['avg_percent_growth']*1.005, r['sector'], fontsize=8)
plt.title('Sector Risk vs Return (Jan–Jun 2025)')
plt.xlabel('Average Volatility (Std. Dev. of Closing Price)')
plt.ylabel('Average % Growth')
plt.tight_layout()
plt.show()
