## plot_weather.py to plot raw 3-hourly temperature, daily mean, and daily standard deviation
## for Hoquiam vs Spokane (2006-2025), and print summary numbers for the report.

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# This saves me time from having to set the font sizes for every single element in the plot.
plt.rcParams.update({
    "font.size": 16,         # base size for all text
    "axes.titlesize": 18,    # panel titles (a), (b)
    "axes.labelsize": 18,    # axis labels
    "xtick.labelsize": 15,   # tick numbers
    "ytick.labelsize": 15,
    "legend.fontsize": 15,
    "figure.titlesize": 22,  # main title
})

CSV = "hoquiam_spokane_temp.csv"
COLORS = {"Hoquiam": "#3b528b", "Spokane": "#5ec962"}  # viridis at 0.25 and 0.75
ZOOM_YEAR = "2021"  # year with the June heat dome

data = pd.read_csv(CSV, parse_dates=["time"])

raw, daily = {}, {}
for city, df in data.groupby("city"):
    s = df.set_index("time")["temp_f"].sort_index()
    # Raw data points every 3 hours (00:00, 03:00, 06:00, ...)
    raw[city] = s[s.index.hour % 3 == 0]
    # Daily mean and daily sample standard deviation (ddof=1)
    daily[city] = s.resample("D").agg(["mean", "std"])


def draw(ax, start=None, end=None, point_alpha=0.03, point_size=1):
    for city in ["Spokane", "Hoquiam"]:
        c = COLORS[city]
        r = raw[city][start:end]
        d = daily[city][start:end]
        ax.scatter(r.index, r.values, s=point_size, alpha=point_alpha,
                   color=c, rasterized=True)
        ax.fill_between(d.index, d["mean"] - d["std"], d["mean"] + d["std"],
                        color=c, alpha=0.25, linewidth=0)
        ax.plot(d.index, d["mean"], color=c, linewidth=0.8)
    ax.set_ylabel("Temperature (°F)")
    ax.grid(alpha=0.3)


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# Full 20 years
draw(ax1)
ax1.set_title("(a) Full period, 2006–2025", loc="left")
ax1.set_xlabel("Year")
ax1.xaxis.set_major_locator(mdates.YearLocator(2))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax1.set_xlim(pd.Timestamp("2006-01-01"), pd.Timestamp("2026-01-01"))

# Zoom on one year
draw(ax2, f"{ZOOM_YEAR}-01-01", f"{ZOOM_YEAR}-12-31",
     point_alpha=0.35, point_size=3)
ax2.set_title(f"(b) Detail, {ZOOM_YEAR}", loc="left")
ax2.set_xlabel(f"Date ({ZOOM_YEAR})")
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

# One shared legend that explains the three layers
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
handles = []
for city in ["Spokane", "Hoquiam"]:
    c = COLORS[city]
    handles += [
        Line2D([], [], marker="o", ls="", color=c, alpha=0.5,
               label=f"{city}: raw (every 3 h)"),
        Line2D([], [], color=c, lw=2, label=f"{city}: daily mean"),
        Patch(color=c, alpha=0.25, label=f"{city}: daily mean ± 1σ"),
    ]

# i might use you if i want the legend on the first panel instead of the bottom
# ax1.legend(handles=handles, loc="upper left", ncol=2, fontsize=8)
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False)

fig.suptitle("Coast vs. Inland: Hourly Temperature in Hoquiam and Spokane, WA "
             "(2006–2025)")
#fig.tight_layout()

fig.tight_layout(rect=[0, 0.08, 1, 1])
fig.savefig("fig_temperature.png", dpi=200)
fig.savefig("fig_temperature.pdf")
fig.savefig("fig_temperature.png", dpi=200, bbox_inches="tight", pad_inches=0)
print("Saved fig_temperature.png and fig_temperature.pdf\n")

# Important values for my report 
for city in ["Hoquiam", "Spokane"]:
    d = daily[city]
    hot = d["mean"].idxmax()
    cold = d["mean"].idxmin()
    print(f"{city}")
    print(f"  overall mean temp        : {d['mean'].mean():.1f} °F")
    print(f"  average daily std (σ)    : {d['std'].mean():.1f} °F")
    print(f"  avg daily σ, July        : {d['std'][d.index.month == 7].mean():.1f} °F")
    print(f"  avg daily σ, January     : {d['std'][d.index.month == 1].mean():.1f} °F")
    print(f"  hottest day (daily mean) : {hot.date()}  {d['mean'].max():.1f} °F")
    print(f"  coldest day (daily mean) : {cold.date()}  {d['mean'].min():.1f} °F")
    print(f"  highest raw reading      : {raw[city].max():.1f} °F "
          f"on {raw[city].idxmax()}")
    print()
