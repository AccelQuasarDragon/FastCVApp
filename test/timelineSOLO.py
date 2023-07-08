import matplotlib.pyplot as plt
import numpy as np
# import matplotlib.dates as mdates
from datetime import datetime

#plan read in text file or smth then split > display on matplotlib

dates = ['1688087730.719562', '1688087230.719562', '1688087770.719562', '1688087930.719562',]
dates = [datetime.fromtimestamp(float(VAR)).strftime("%I:%M:%S") for VAR in dates]
names = ['v2.2.4', 'v3.0.3', 'v3.0.2', 'v3.0.1',]

fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
#plot on x axis
ax.plot(dates, np.zeros_like(dates), "-o", color="k", markerfacecolor="w")  # Baseline and markers on it.
levels = np.tile([-5, 5, -3, 3, -1, 1],
                 int(np.ceil(len(dates)/6)))[:len(dates)]
#plot offset so that matplotlib will resize right
ax.plot(dates, levels, 's',"-o", color="k", markerfacecolor="w")  # Baseline and markers on it.
#vertical lines
ax.vlines(dates, 0, levels, color="tab:red")


#annotate writes text and takes (x,y) coords which is why u gotta zip
for nameVAR, dateVAR, levelsVAR in zip(names, dates, levels):
    ax.annotate(nameVAR, (dateVAR, levelsVAR), textcoords="offset points", horizontalalignment="right",) 
        #verticalalignment="bottom" if l > 0 else "top"

# remove y-axis and spines
# ax.yaxis.set_visible(False)
# ax.spines[["left", "top", "right"]].set_visible(False)

ax.annotate("wtf",(-1, 1), textcoords="offset points", horizontalalignment="right",) 
plt.show()