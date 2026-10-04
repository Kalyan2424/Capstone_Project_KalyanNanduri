# Task 11 — Two visualizations using Matplotlib - return_rate_by_payment.png & monthly_revenue_trend.png

import pandas as pd
import matplotlib.pyplot as plt

# --- Global style for gridlines ---
plt.style.use("seaborn-v0_8-whitegrid")

# --- Load cleaned dataset ---
merged = pd.read_csv("cleaned_orders.csv")

# --- Return rates by payment method ---
return_stats = merged.groupby('payment_method')['returned'].agg(['count','mean'])
return_stats['return_rate_pct'] = (return_stats['mean'] * 100).round(2)

plt.figure(figsize=(6,4))
bars = plt.bar(return_stats.index, return_stats['return_rate_pct'],
               color=['#E74C3C','#27AE60','#2980B9'])

plt.ylabel("Return Rate (%)")
plt.yticks(range(0, 55, 5))   

cod_rate = return_stats.loc['COD','return_rate_pct']
card_rate = return_stats.loc['CARD','return_rate_pct']
ratio = round(cod_rate/card_rate, 1)

plt.title(f"COD Returns ≈ {ratio}x Card")

# Annotate values with two decimals
for bar, val in zip(bars, return_stats['return_rate_pct']):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f"{val:.2f}%", ha='center', va='bottom')

plt.savefig("return_rate_by_payment.png")
plt.close()

# --- Monthly revenue trend (outlier-corrected) ---
monthly_excl = merged.loc[~merged['is_outlier']].groupby('year_month')['order_value'].sum().round(2)

plt.figure(figsize=(8,5))
plt.plot(monthly_excl.index, monthly_excl.values, marker='o', color='#27AE60')

plt.ylabel("Revenue (INR)")   
plt.xlabel("Month")
plt.yticks(range(0, int(monthly_excl.max())+5000, 2000))   

# Highlight peak month
peak_month = monthly_excl.idxmax()
peak_value = monthly_excl.max()
plt.title(f"Outlier-Corrected Monthly Revenue Trend — Peak in {peak_month}", pad=30)
plt.annotate(f"{peak_value:.2f}", xy=(peak_month, peak_value),
             xytext=(peak_month, peak_value+1500), color='red', ha='center')

plt.savefig("monthly_revenue_trend.png")
plt.close()

# --- Console outputs with two decimals ---
return_rates = merged.groupby('payment_method')['returned'].mean() * 100
print(return_rates.map("{:.2f}".format))   

monthly_revenue = merged.loc[~merged['is_outlier']].groupby('year_month')['order_value'].sum()
print(monthly_revenue.map("{:.2f}".format))   
