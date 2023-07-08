# https://stackoverflow.com/questions/66956444/live-video-feed-from-camera-to-tkinter-window-with-opencv
import tkinter
from tkinter import *
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk
import cv2

ikkuna=tkinter.Tk()
ikkuna.title("Example about handy CV2 and tkinter combination...")

frame=np.random.randint(0,255,[100,100,3],dtype='uint8')
img = ImageTk.PhotoImage(Image.fromarray(frame))

paneeli_image=tkinter.Label(ikkuna) #,image=img)
paneeli_image.grid(row=0,column=0,columnspan=3,pady=1,padx=10)

message="You can see some \nclassification results \nhere after you add some intelligent  \nadditional code to your combined and handy \n tkinter & CV2 solution!"
paneeli_text=tkinter.Label(ikkuna,text=message)
paneeli_text.grid(row=1,column=1,pady=1,padx=10)

global cam

def otakuva():
    global frame
    global cam
    cam = cv2.VideoCapture("creativecommonsmedia\Elephants Dream charstart2FULL.webm")
    #cv2.namedWindow("Experience_in_AI camera")
    while True:
        ret, frame = cam.read()

        import time
        #Update the image to tkinter...
        time1 = time.time()
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img_update = ImageTk.PhotoImage(Image.fromarray(frame))
        paneeli_image.configure(image=img_update)
        paneeli_image.image=img_update
        paneeli_image.update()
        print("update time", time.time()-time1)

        if not ret:
            print("failed to grab frame")
            break

        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")

            cam.release()
            cv2.destroyAllWindows()
            break

def lopeta():
    global cam
    cam.release()
    cv2.destroyAllWindows()
    print("Stopped!")

painike_korkeus=10
painike_1=tkinter.Button(ikkuna,text="Start",command=otakuva,height=5,width=20)
painike_1.grid(row=1,column=0,pady=10,padx=10)
painike_1.config(height=1*painike_korkeus,width=20)

painike_korkeus=10
painike_1=tkinter.Button(ikkuna,text="Stop",command=lopeta,height=5,width=20)
painike_1.grid(row=1,column=2,pady=10,padx=10)
painike_1.config(height=1*painike_korkeus,width=20)

ikkuna.mainloop()