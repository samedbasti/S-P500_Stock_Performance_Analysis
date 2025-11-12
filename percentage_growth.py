import pandas as pd

df = pd.read_csv("sp500_2025_h1.csv")
df.info()
df.describe()
df.head()

first_close_col = [col for col in df.columns if col.endswith('_closing')][0]
last_close_col = [col for col in df.columns if col.endswith('30-06-2025_closing')][0]

df['percent_change'] = ((df[last_close_col] - df[first_close_col]) / df[first_close_col]) * 100

top10_growth = df.sort_values('percent_change', ascending=False).head(10)
bottom10_growth = df.sort_values('percent_change', ascending=True).head(10)

print("Top 10 Stocks by % Growth (Jan–Jun 2025):")
print(top10_growth[['company_name', 'ticker', 'percent_change']])

# Plot top 10 growth
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
sns.barplot(x='percent_change', y='company_name', data=top10_growth, palette='coolwarm')
plt.title('Top 10 S&P 500 Stocks by % Growth (Jan–Jun 2025)')
plt.xlabel('Growth (%)')
plt.ylabel('Company')
plt.tight_layout()
plt.show()
