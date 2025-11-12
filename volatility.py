import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("sp500_2025_h1.csv")
df.info()
df.describe()
df.head()

closing_cols = [col for col in df.columns if 'closing' in col]
df['volatility'] = df[closing_cols].std(axis=1)

top10_volatility = df.sort_values('volatility', ascending=False).head(10)
print("Most Volatile Stocks:")
print(top10_volatility[['company_name', 'ticker', 'volatility']])

plt.figure(figsize=(10,6))
sns.barplot(x='volatility', y='company_name', data=top10_volatility, palette='mako')
plt.title('Most Volatile S&P 500 Stocks (Jan–Jun 2025)')
plt.xlabel('Volatility (Standard Deviation of Closing Price)')
plt.ylabel('Company')
plt.tight_layout()
plt.show()
