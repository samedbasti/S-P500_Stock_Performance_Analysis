import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("sp500_2025_h1.csv")
df.info()
df.describe()
df.head()

closing_cols = [col for col in df.columns if 'closing' in col]

df['avg_closing_price'] = df[closing_cols].mean(axis=1)

top10 = df.sort_values('avg_closing_price', ascending=False).head(10)
bottom10 = df.sort_values('avg_closing_price', ascending=True).head(10)

print("Top 10 by average closing price:")
print(top10[['company_name', 'ticker', 'avg_closing_price']])

plt.figure(figsize=(10,6))
sns.barplot(x='avg_closing_price', y='company_name', data=top10, palette='viridis')
plt.title('Top 10 S&P 500 Companies by Average Closing Price (Jan–Jun 2025)')
plt.xlabel('Average Closing Price (USD)')
plt.ylabel('Company')
plt.tight_layout()
plt.show()
