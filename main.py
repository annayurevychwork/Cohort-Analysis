import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

file_name = "Cohort analysis.xlsx"
installs_df = pd.read_excel(file_name, sheet_name="Task1. Installs", engine="openpyxl")
revenue_df = pd.read_excel(file_name, sheet_name="Task 1. Revenue Cohort", engine="openpyxl")

revenue_df = revenue_df.iloc[1:].copy()

first_col_revenue = revenue_df.columns[0]
revenue_df = revenue_df.rename(columns={first_col_revenue: 'Week of installs'})
revenue_df['Week of installs'] = revenue_df['Week of installs'].astype(int)

if 'Weeks Since Install' in revenue_df.columns:
    revenue_df = revenue_df.drop(columns=['Weeks Since Install'])

install_week_col = installs_df.columns[0]
install_count_col = installs_df.columns[1]

df = pd.merge(revenue_df, installs_df, left_on='Week of installs', right_on=install_week_col)

total_revenue_per_week = {}
total_installs_per_week = {}

for w in range(45):
    col = w if w in df.columns else str(w)

    if col in df.columns:
        valid_cohorts = df[df[col].notna()]
        if len(valid_cohorts) > 0:
            total_revenue_per_week[w] = valid_cohorts[col].sum()
            total_installs_per_week[w] = valid_cohorts[install_count_col].sum()

arpu_weekly = {w: total_revenue_per_week[w] / total_installs_per_week[w] for w in total_revenue_per_week}

arpu_cumulative = pd.Series(arpu_weekly).cumsum()

arpu_3_months = arpu_cumulative[12]
print(f"1. Дохід з одного користувача за 3 місяці: ${arpu_3_months:.4f}")

def log_func(x, a, b):
    return a * np.log(x + 1) + b

max_weeks_data = len(arpu_cumulative)
x_data = np.arange(max_weeks_data)
y_data = arpu_cumulative.values

popt_log, _ = curve_fit(log_func, x_data, y_data)

x_pred = np.arange(53)
y_pred_log = log_func(x_pred, *popt_log)

arpu_1_year = y_pred_log[52]
print(f"2. Прогнозований дохід з одного користувача за 1 рік: ${arpu_1_year:.4f}")

plt.figure(figsize=(10, 6))
plt.plot(x_data, y_data, marker='o', label='Фактичний Cumulative ARPU', markersize=4)
plt.plot(x_pred, y_pred_log, linestyle='--', color='red', label='Логарифмічний прогноз')
plt.axvline(x=12, color='green', linestyle=':', label=f'3 місяці: ${arpu_3_months:.2f}')
plt.axvline(x=52, color='orange', linestyle=':', label=f'1 рік: ${arpu_1_year:.2f}')
plt.plot(12, arpu_3_months, 'go')
plt.plot(52, arpu_1_year, 'yo')
plt.title('Фактичні дані та Прогноз на 1 рік')
plt.xlabel('Тижні після встановлення')
plt.ylabel('Cumulative ARPU')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()