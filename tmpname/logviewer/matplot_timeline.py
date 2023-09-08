import matplotlib.pyplot as plt
import numpy as np
# import matplotlib.dates as mdates
from datetime import datetime
import os

#plan read in text file or smth then split > display on matplotlib
print("?????", *__file__.split(os.path.sep)[:-1], )
filelocation = os.path.join(os.sep, __file__.split(os.path.sep)[0] + os.sep, *__file__.split(os.path.sep)[:-1], "logs.txt")
print("filelocation", filelocation)
with open(filelocation, "r", encoding="utf8") as file:
    log_data = file.readlines()

#fix logdata:
xvarlist = []
commentlist = []

pidlist = []
log_data_sorted = []

for lineVAR in log_data:
    lineVAR_parsed = lineVAR.split(" ")
    if len(lineVAR_parsed) > 1:
        #create the list per plot/PID, each item looks like this: PID, x value (in datetime) (y is determined later), the annotation  
        parsed_time = datetime.fromtimestamp(float(lineVAR_parsed[1])).strftime("%I:%M:%S:%f")
        if lineVAR_parsed[0] not in pidlist:
            pidlist.append(lineVAR_parsed[0])
            log_data_sorted.append([[lineVAR_parsed[0]] + [parsed_time] + lineVAR_parsed[2:]])
        else:
            log_data_sorted[pidlist.index(lineVAR_parsed[0])].append([lineVAR_parsed[0]] + [parsed_time] + lineVAR_parsed[2:])

        xvarlist.append(parsed_time)
        commentlist.append(lineVAR_parsed[2:])

#for each PID assign a color and height:
#these heights are interleaved:
arange = np.array(np.arange(-4,3.5,0.5))
brange = np.array(np.arange(4,-3.5,-.5))
# https://stackoverflow.com/questions/5347065/interweaving-two-numpy-arrays-efficiently
def JoshAdel(a, b):
    # https://stackoverflow.com/questions/67625331/how-to-fix-must-be-passed-as-a-sequence-warning-for-pil-in-python
    # return np.hstack([var for var in zip(a,b)])
    # https://stackoverflow.com/a/5347082
    return np.vstack((a,b)).reshape((-1,),order='F')
    # return c
thearange = JoshAdel(arange, brange)


fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
#plot on x axis for the baseline
theproblem = np.zeros_like(xvarlist)
# theproblem = np.zeros(len(xvarlist))
# theproblem = np.zeros((0,len(xvarlist)))
print("wrwerw", xvarlist, theproblem, theproblem.shape)
ax.plot(np.array(xvarlist), theproblem, "-o", color="k", markerfacecolor="w")  # Baseline and markers on it.

import matplotlib.colors as mcolors
if len(pidlist) < 6:
# if len(pidlist) < len(mcolors.CSS4_COLORS.keys()):
    # basecolorlist = ['b', 'g', 'r', 'c', 'm', 'y']
    # vlinecolorlist = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
    basecolorlist = list(mcolors.CSS4_COLORS.keys())
    vlinecolorlist = list(mcolors.CSS4_COLORS.keys())
elif len(pidlist) < len(mcolors.CSS4_COLORS.keys()):
    #choose random color
    basecolorlist = list(mcolors.CSS4_COLORS.keys())

def filter_colors(*args):
    testlist = args[0]
    current_color = args[1]
    # print("hwainstance0", testlist, isinstance(testlist[0],np.ndarray), current_color)
    if isinstance(testlist[0],np.ndarray): 
        #assume they're all the same type.....
        return [colorVAR for colorVAR in testlist if (colorVAR != current_color).all()]
    else:
        return [colorVAR for colorVAR in testlist if colorVAR != current_color]

#make a unique plot with a label per PID:
for PIDVar in pidlist:
    #pick a random base color as per: https://matplotlib.org/stable/gallery/color/named_colors.html
    import random
    current_color = random.choice(basecolorlist)
    #filter out current color from basecolorlist
    basecolorlist = filter_colors(basecolorlist, current_color)
    vline_color = random.choice(vlinecolorlist)
    vlinecolorlist = filter_colors(vlinecolorlist, vline_color)

    xvarlistfixed = [guyVAR[1] for guyVAR in log_data_sorted[pidlist.index(PIDVar)]]
    print("inhomogeneous", xvarlistfixed)
    must_have_same_first_dimension = np.array(xvarlistfixed)
    #plot with the color and height (pick height sequentially, use: thearange[pidlist.index(PIDVar)])
    random_height = np.full(must_have_same_first_dimension.shape, thearange[pidlist.index(PIDVar)])
    
    # np.zeros_like(xvarlist)
    print("THECOLROS", current_color)

    ax.plot(xvarlistfixed, random_height, 's',"-o", color=current_color, markerfacecolor="w", label=str(PIDVar))  # Baseline and markers on it.
    ax.vlines(xvarlistfixed, 0, random_height, color=vline_color, label=str(PIDVar))

#set hover as per: # https://stackoverflow.com/questions/60987714/matplotlib-hover-text
import mplcursors
cursor = mplcursors.cursor(hover=True)

#as per: https://stackoverflow.com/questions/75059446/accessinglocal-data-with-mplcursors
def infoParser(selVAR):

    if selVAR.artist.get_label() in pidlist:
        if isinstance(selVAR.index,tuple):
            target = selVAR.index[0]
        else:
            target = selVAR.index
        # print("notes1", pidlist.index(selVAR.artist.get_label()), pidlist,selVAR.artist.get_label())
        # print("notes2",  selVAR)
        # print("notes3",   selVAR.index[0]) #sometimes is index=9, sometimes is index=(9, 1.0)
        dataentry = log_data_sorted[pidlist.index(selVAR.artist.get_label())][target]
        datastring = " ".join(dataentry[2:])
        selVAR.annotation.set_text( 
            f"PID: {selVAR.artist.get_label()} \n time: {dataentry[1]}, \n data: {datastring}, ")


# cursor.connect("add", lambda sel: sel.annotation.set_text(
#     # f"ID:{sel.target.index} '{labels[sel.target.index]}'\nSize:{sizes[sel.target.index]} ({sizes[sel.target.index] * 100.0 / sumsizes:.1f} %)"))
#     f"{dir(sel)[40:]}")) #sel.annotation
# cursor.connect("add", lambda sel: print( dir(sel)))
# cursor.connect("add", lambda sel: print( f"{sel.artist.get_label()} \n "))
# https://stackoverflow.com/questions/75059446/accessinglocal-data-with-mplcursors
# cursor.connect("add", lambda sel: sel.annotation.set_text( 
#     f"PID: {sel.artist.get_label()} \n time: {sel.target}, {log_data_sorted[pidlist.index(sel.artist.get_label())][sel.index[0]]}, ") #{sel.target.get_label()}
#     if sel.artist.get_label() in pidlist else "")

cursor.connect("add", infoParser)

#sel.index[0] is usable data to get the info from the list
     #note: {}
    # if (sel.artist.get_label() in pidlist))
# https://stackoverflow.com/questions/60380004/mplcursors-shows-only-y-coordinate

# log_data_sorted[pidlist.index(sel.artist.get_label())][sel.index[0]]
#info I want: PID, time, note

#you can do it right: plan is to set the color<>height correspondence, then when you check selection u can get the right text

#new idea: each pid gets its own curve: https://stackoverflow.com/questions/60209132/display-annotation-text-of-plot-simultaneously-in-matplotlib

plt.show()

# =-=-=-==-=-=-==-=-=-==-=-=-==-=-=-==-=-=-==-=-=-=

# import matplotlib.pyplot as plt
# import numpy as np
# # import matplotlib.dates as mdates
# from datetime import datetime
# import os

# #plan read in text file or smth then split > display on matplotlib
# print("?????", *__file__.split(os.path.sep)[:-1], )
# filelocation = os.path.join(os.sep, __file__.split(os.path.sep)[0] + os.sep, *__file__.split(os.path.sep)[:-1], "logs.txt")
# print("filelocation", filelocation)
# with open(filelocation, "r", encoding="utf8") as file:
#     log_data = file.readlines()

# #fix logdata:
# log_data_parsed = []
# xvarlist = []
# yvarlist = []
# commentlist = []
# for lineVAR in log_data:
#     lineVAR_parsed = lineVAR.split(" ")
#     if len(lineVAR_parsed) > 1:
#         #info is: PID/time in sec/text
#         print("index out of range", lineVAR_parsed)
#         parsed_time = datetime.fromtimestamp(float(lineVAR_parsed[1])).strftime("%I:%M:%S:%f")
#         # print("type wtf", type([lineVAR_parsed[0]]), type([parsed_time]), type(lineVAR_parsed[2:]))
#         log_data_parsed.append([lineVAR_parsed[0]] + [parsed_time] + lineVAR_parsed[2:])
#         xvarlist.append(parsed_time)
#         # yvarlist.append()
#         commentlist.append(lineVAR_parsed[2:])

# # dates = ['1688087730.719562', '1688087230.719562', '1688087770.719562', '1688087930.719562',]
# # dates = [datetime.fromtimestamp(float(VAR)).strftime("%I:%M:%S") for VAR in dates]
# # names = ['v2.2.4', 'v3.0.3', 'v3.0.2', 'v3.0.1',]

# fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
# #plot on x axis
# thisruns = np.zeros_like(xvarlist)
# print("err why", xvarlist, thisruns, thisruns.shape, type(xvarlist))
# ax.plot(xvarlist, np.zeros_like(xvarlist), "-o", color="k", markerfacecolor="w")  # Baseline and markers on it.
# # levels = np.tile([-5, 5, -3, 3, -1, 1], int(np.ceil(len(xvarlist)/6)))[:len(xvarlist)]
# # levels = np.arrange([-5,5,0.5])
# # thearange = np.arange(-5,5,0.5)
# # arange = np.array(np.arange(-5,5,1))
# # brange = np.array(np.arange(-6,4,1))
# # brange = np.array(np.arange(4.5,-4.5,.5))
# arange = np.array(np.arange(-5,4.5,0.5))
# brange = np.array(np.arange(5,-4.5,-.5))
# print(arange, arange.shape)
# print(brange, brange.shape)

# # https://stackoverflow.com/questions/5347065/interweaving-two-numpy-arrays-efficiently
# def andersonvom(a, b):
#     # https://stackoverflow.com/questions/67625331/how-to-fix-must-be-passed-as-a-sequence-warning-for-pil-in-python
#     # return np.hstack([var for var in zip(a,b)])
#     # https://stackoverflow.com/a/5347082
#     return np.vstack((a,b)).reshape((-1,),order='F')
#     # return c
# thearange = andersonvom(arange, brange)

# levels = np.tile(thearange, int(np.ceil(len(xvarlist)/len(thearange))))[:len(xvarlist)]
# #plot offset so that matplotlib will resize right
# ax.plot(xvarlist, levels, 's',"-o", color="k", markerfacecolor="w", label="testlabel")  # Baseline and markers on it.
# #vertical lines
# ax.vlines(xvarlist, 0, levels, color="tab:red")
# norm = plt.Normalize(vmin=min([lineVAR[1] for lineVAR in log_data]), vmax=max(levels))

# #reference: https://github.com/Phlya/adjustText/wiki
# from adjustText import adjust_text
# annotate_list = []
# #annotate writes text and takes (x,y) coords which is why u gotta zip
# for nameVAR, dateVAR, levelsVAR in zip(commentlist, xvarlist, levels):
#     # annotate_list = ax.annotate(nameVAR, (dateVAR, levelsVAR), textcoords="offset points", horizontalalignment="right",) 
#         #verticalalignment="bottom" if l > 0 else "top"
#     annotationguy = ax.annotate(nameVAR, (dateVAR, levelsVAR), textcoords="offset points", horizontalalignment="right",) 
#     #need this because annotate list complains about non homogeneous size so need to make the list into a single element: " ".join(nameVAR))
#     # textelement = ax.text(dateVAR, levelsVAR," ".join(nameVAR))
#     # annotationguy.set_visible(False)
#     annotate_list.append(annotationguy) 
    
# # adjust_text(annotate_list)

# # remove y-axis and spines
# # ax.yaxis.set_visible(False)
# # ax.spines[["left", "top", "right"]].set_visible(False)

# # ax.annotate("wtf",(-1, 1), textcoords="offset points", horizontalalignment="right",) 
# # from adjustText import adjust_text
# # np.random.seed(0)
# # x, y = np.random.random((2,30))
# # fig, ax = plt.subplots()
# # plt.plot(x, y, 'bo')
# # texts = [plt.text(x[i], y[i], 'Text%s' %i, ha='center', va='center') for i in range(len(x))]
# # adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))

# #set hover as per: # https://stackoverflow.com/questions/60987714/matplotlib-hover-text
# import mplcursors
# cursor = mplcursors.cursor(hover=True)
# # cursor.connect("add", lambda sel: sel.annotation.set_text(
# #     # f"ID:{sel.target.index} '{labels[sel.target.index]}'\nSize:{sizes[sel.target.index]} ({sizes[sel.target.index] * 100.0 / sumsizes:.1f} %)"))
# #     f"{dir(sel)[40:]}")) #sel.annotation
# # cursor.connect("add", lambda sel: print( dir(sel)))
# cursor.connect("add", lambda sel: print( sel.artist.get_label()))

# #you can do it right: plan is to set the color<>height correspondence, then when you check selection u can get the right text

# #new idea: each pid gets its own curve: https://stackoverflow.com/questions/60209132/display-annotation-text-of-plot-simultaneously-in-matplotlib

# plt.show()