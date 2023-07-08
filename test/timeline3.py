#https://stackoverflow.com/a/68386722

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime

df = pd.DataFrame(
    {
        'event': ['birthday', 'first steps'] * 5,
        'date': pd.date_range(start='1/1/2018', periods=10)        
    }
)

df['date'] = pd.to_datetime(df['date'])

levels = np.tile(
    [-5, 5, -3, 3, -1, 1],
    int(np.ceil(len(df)/6))
)[:len(df)]

fig, ax = plt.subplots(figsize=(12.8, 4), constrained_layout=True)
ax.set(title="A series of events")

ax.vlines(df['date'], 0, levels, color="tab:red")  # The vertical stems.
ax.plot(   # Baseline and markers on it.
    df['date'],
    np.zeros_like(df['date']),
    "-o",
    color="k",
    markerfacecolor="w"
)

# annotate lines
for d, l, r in zip(df['date'], levels, df['event']):
    ax.annotate(
        r,
        xy=(d, l),
        xytext=(-3, np.sign(l)*3),
        textcoords="offset points",
        horizontalalignment="right",
        verticalalignment="bottom" if l > 0 else "top"
    )

# format xaxis with 4 month intervals
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# remove y axis and spines
ax.yaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)    
ax.margins(y=0.1)
plt.show()