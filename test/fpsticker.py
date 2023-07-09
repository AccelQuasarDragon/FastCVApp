#need an indep process that can tell the fps frame for kivy:
import time
i = 0
# ogtime = time.time()
# while True:
#     i += 1
#     #figure out how much fps while True has:
#     if i == 100000:
#         break
# finaltime = time.time()
# print("fps of while loop?", (finaltime - ogtime)/i, i) #iirc while true has ~1000 fps, well, it's super fast... fps of while loop? 1.0999679565429687e-07 100000
'''
#now I need to +1 every 1/30 second for 30 fps:
ogtime = time.time()
tickertime = time.time()
while True:
    if time.time() - tickertime > 1/30:
        i += 1
        tickertime = time.time()
    #make it finish in 10 seconds, let's see how close my ticker is to the  "true" time
    if i == 300:
        break
finaltime = time.time()
# print("fps of while loop?", (finaltime - ogtime)/i, i) #iirc while true has ~1000 fps, well, it's super fast... fps of while loop? 1.0999679565429687e-07 100000
print("has it been 10 seconds?", finaltime - ogtime, "i: ", i)
#RIP, there is a delay:  10.196099996566772 
'''
#https://stackoverflow.com/questions/1938048/high-precision-clock-in-python

# instead of making my own ticker which has a delay, use time.time instead and divide to figure out fps:

ogtime = time.time()
fps = 1/30
while True:
    frame = int((time.time() - ogtime)/ fps)
    print("framecount:", frame)
    if frame >=300:
        break
finaltime = time.time()
# print("fps of while loop?", (finaltime - ogtime)/i, i) #iirc while true has ~1000 fps, well, it's super fast... fps of while loop? 1.0999679565429687e-07 100000
print("has it been 10 seconds?", finaltime - ogtime, "i: ", i)
#RIP, there is a delay:  10.196099996566772 
'''
WAY BETTER SOLUTION:
framecount: 299
framecount: 299
framecount: 299
framecount: 300
has it been 10 seconds? 10.000000238418579 i:  0
if I had used time.time earlier I probably wouldn't have spent 3 months on fixing this problem...
'''