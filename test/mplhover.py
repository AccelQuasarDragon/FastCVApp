# https://stackoverflow.com/questions/60987714/matplotlib-hover-text

import matplotlib.pyplot as plt
import matplotlib as mpl
import squarify
import mplcursors

sizes = [5, 20, 30, 25, 10, 12]
sumsizes = sum(sizes)
labels = ['A', 'B', 'C', 'D', 'E', 'F']

cmap = plt.cm.get_cmap('Greens')
norm = plt.Normalize(vmin=min(sizes), vmax=max(sizes))
colors = [cmap(norm(s)) for s in sizes]
squarify.plot(sizes=sizes, label=labels, color=colors)
plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm))

cursor = mplcursors.cursor(hover=True)
cursor.connect("add", lambda sel: sel.annotation.set_text(
    # f"ID:{sel.target.index} '{labels[sel.target.index]}'\nSize:{sizes[sel.target.index]} ({sizes[sel.target.index] * 100.0 / sumsizes:.1f} %)"))
    f"{sel.target}"))

    #sel: selection/artists/etc
    #sel.target: the point on the plot

plt.show()