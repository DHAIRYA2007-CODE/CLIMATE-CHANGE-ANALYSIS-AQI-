"""
Modern AQI visualizations for Indian cities (2016–2025).
Keep this script in the same folder as the CSV dataset.
Outputs: aqi_modern_heatmap.png, aqi_modern_trends.png, aqi_data_reordered.csv
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "cities.csv"
years = [str(y) for y in range(2016, 2026)]

df = pd.read_csv(CSV_PATH)

mpl.rcParams.update({
    "figure.facecolor": "#0B1220",
    "axes.facecolor": "#111C2E",
    "savefig.facecolor": "#0B1220",
    "text.color": "#E5EDF7",
    "axes.labelcolor": "#CBD5E1",
    "xtick.color": "#CBD5E1",
    "ytick.color": "#CBD5E1",
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
})

# 1. Heatmap: transpose layout so years are rows and states are columns
state_df = df.groupby("State")[years].mean()
state_df["10Yr_Mean"] = state_df[years].mean(axis=1)
state_df = state_df.sort_values("10Yr_Mean", ascending=False).drop(columns="10Yr_Mean")
heat_data = state_df.T

fig, ax = plt.subplots(figsize=(18, 7.8), dpi=160)
im = ax.imshow(heat_data.values, cmap="magma", aspect="auto", interpolation="nearest")
ax.set_xticks(np.arange(len(heat_data.columns)))
ax.set_xticklabels(heat_data.columns, rotation=55, ha="right", fontsize=8)
ax.set_yticks(np.arange(len(heat_data.index)))
ax.set_yticklabels(heat_data.index, fontsize=10)
ax.set_title("INDIA AIR QUALITY  |  STATE-WISE AQI", loc="left", fontsize=18, pad=20, color="#F8FAFC")
ax.text(0, 1.02, "Annual mean AQI • 2016–2025 • States ordered by decade average",
        transform=ax.transAxes, fontsize=10, color="#94A3B8", va="bottom")
ax.set_xlabel("States / Union Territories", labelpad=12)
ax.set_ylabel("Year", labelpad=10)
ax.set_xticks(np.arange(-.5, len(heat_data.columns), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(heat_data.index), 1), minor=True)
ax.grid(which="minor", color="#243247", linewidth=0.55)
ax.tick_params(which="minor", bottom=False, left=False)
for spine in ax.spines.values():
    spine.set_visible(False)
cbar = fig.colorbar(im, ax=ax, pad=0.015, shrink=0.86)
cbar.set_label("Mean AQI", color="#CBD5E1", labelpad=12)
cbar.ax.tick_params(colors="#CBD5E1")
cbar.outline.set_visible(False)
fig.subplots_adjust(left=0.07, right=0.96, top=0.82, bottom=0.28)
fig.savefig(BASE_DIR / "aqi_modern_heatmap.png", dpi=180, bbox_inches="tight")
plt.show()
plt.close(fig)

# 2. City trend chart: all cities in the background, selected cities highlighted
fig, ax = plt.subplots(figsize=(13, 7), dpi=160)
for _, row in df.iterrows():
    ax.plot(years, row[years].values, color="#64748B", linewidth=0.7, alpha=0.16, zorder=1)

highlight_cities = ["Ghaziabad", "Delhi", "Noida", "Greater Noida", "Gurugram", "Panipat"]
colors = ["#FB7185", "#60A5FA", "#FBBF24", "#34D399", "#C084FC", "#22D3EE"]
for city, color in zip(highlight_cities, colors):
    matched = df[df["City"].str.casefold() == city.casefold()]
    if matched.empty:
        continue
    row = matched.iloc[0]
    ax.plot(years, row[years].values, marker="o", markersize=4, linewidth=2.5,
            color=color, label=city, zorder=3)
    ax.annotate(f"{row[years[-1]]:.0f}", (years[-1], row[years[-1]]),
                xytext=(7, 0), textcoords="offset points", color=color,
                fontsize=8, va="center", fontweight="bold")
ax.set_title("AQI OVER TIME", loc="left", fontsize=19, pad=18, color="#F8FAFC")
ax.text(0, 1.02, "All 133 cities in the background • Selected cities highlighted",
        transform=ax.transAxes, fontsize=10, color="#94A3B8", va="bottom")
ax.set_xlabel("Year", labelpad=10)
ax.set_ylabel("Mean AQI", labelpad=10)
ax.grid(True, color="#334155", linestyle="--", linewidth=0.7, alpha=0.65)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_color("#263449")
ax.legend(
    title="Selected cities",
    facecolor="#111C2E",
    edgecolor="#334155",
    labelcolor="#E5EDF7",
    title_fontsize=7,
    fontsize=7,
    ncol=3,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.16),
    framealpha=0.92,
    borderpad=0.45,
    labelspacing=0.35,
    handlelength=1.4,
    handletextpad=0.45,
    columnspacing=0.8,
)
fig.tight_layout(pad=1.5)
fig.savefig(BASE_DIR / "aqi_modern_trends.png", dpi=180, bbox_inches="tight")
plt.show()
plt.close(fig)

# 3. Save the dataset with a clean column order and rows grouped by State, then City
preferred_cols = ["City", "State", "Region"] + years + [
    "10Yr_Mean_AQI", "10Yr_Change_%", "Overall_Category"
]
df[preferred_cols].sort_values(["State", "City"]).reset_index(drop=True).to_csv(
    BASE_DIR / "aqi_data_reordered.csv", index=False
)

# 4. Preserve the original console analysis / statistical summaries
print("=" * 60)
print("1. DATASET OVERVIEW")
print("=" * 60)
print(f"Total Cities Covered : {df['City'].nunique()}")
print(f"Total States / UTs : {df['State'].nunique()}")
print(f"Total Regions : {df['Region'].nunique()}")
print(f"Missing Values : {df.isnull().sum().sum()}")
print("\\nCategory Breakdown:")
print(df['Overall_Category'].value_counts().to_string())

print("\\n" + "=" * 60)
print("2. STATISTICAL SUMMARY (2016–2025)")
print("=" * 60)
print(df[years + ['10Yr_Mean_AQI', '10Yr_Change_%']].describe().round(2).to_string())

print("\\n" + "=" * 60)
print("3. TOP 5 MOST POLLUTED CITIES (10-Year Mean AQI)")
print("=" * 60)
print(df.nlargest(5, '10Yr_Mean_AQI')[['City', 'State', '10Yr_Mean_AQI', '10Yr_Change_%', 'Overall_Category']].to_string(index=False))

print("\\n" + "=" * 60)
print("4. TOP 5 CLEANEST CITIES (10-Year Mean AQI)")
print("=" * 60)
print(df.nsmallest(5, '10Yr_Mean_AQI')[['City', 'State', '10Yr_Mean_AQI', '10Yr_Change_%', 'Overall_Category']].to_string(index=False))

print("\\n" + "=" * 60)
print("5. BIGGEST IMPROVERS VS. WORST DECLINES (2016 vs. 2025)")
print("=" * 60)
print("Largest decreases in AQI:")
print(df.sort_values('10Yr_Change_%')[['City', 'State', '2016', '2025', '10Yr_Change_%']].head(5).to_string(index=False))
print("\\nCities with increasing AQI (% change):")
worsened = df[df['10Yr_Change_%'] > 0].sort_values('10Yr_Change_%', ascending=False)
print(worsened[['City', 'State', '2016', '2025', '10Yr_Change_%']].to_string(index=False))

print("\\n" + "=" * 60)
print("6. REGIONAL & STATE AVERAGES")
print("=" * 60)
region_summary = df.groupby('Region').agg(
    Cities=('City', 'count'),
    Mean_AQI=('10Yr_Mean_AQI', 'mean'),
    Avg_Change_Pct=('10Yr_Change_%', 'mean')
).sort_values('Mean_AQI', ascending=False).round(2)
print("Regional Summary:")
print(region_summary.to_string())

print("\\nTop 5 States by Average AQI:")
state_summary = df.groupby('State')['10Yr_Mean_AQI'].mean().sort_values(ascending=False).round(2)
print(state_summary.head(5).to_string())

print("\\nSaved modern AQI charts and reordered dataset in:", BASE_DIR)