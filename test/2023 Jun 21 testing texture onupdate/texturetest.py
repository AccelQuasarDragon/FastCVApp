'''
references:
https://stackoverflow.com/questions/46125196/kivy-error-raise-factoryexceptionunknown-class-s-name

https://www.geeksforgeeks.org/python-how-to-use-multiple-kv-files-in-kivy/
https://stackoverflow.com/questions/29332868/is-it-possible-to-read-from-more-than-one-kv-file-in-kivy-app
'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import numpy as np
import random

class Threebythreeone(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self.createTexture, 1)
        Clock.schedule_interval(self.updateTextureTimer, 2)
    
    def createTexture(self, *args):
        randguy = random.randint(0,255)
        emptyframe = np.full((500,700, 3), [randguy, randguy, randguy], dtype=np.uint8)
        buf = emptyframe.tobytes()

        #create the texture 
        self.texture1 = Texture.create(
            size=(500,700), colorfmt='rgb')
        self.texture1.blit_buffer(
            buf, colorfmt='rgb', bufferfmt="ubyte"
        )
        print("textureid in createtexture??", self, self.ids)
        self.ids["textureID"].texture = self.texture1
        #set the ask update 

    def updateTextureTimer(self, *args):
        self.ids["textureID"].texture.ask_update(self.updateTexture)

    def updateTexture(self, *args):
        randguy = random.randint(0,255)
        emptyframe = np.full((500,700, 3), [randguy, randguy, randguy], dtype=np.uint8)
        buf = emptyframe.tobytes()
        # self.ids["textureID"].texture.blit_data(buf) #as per discord, just use blit data https://discord.com/channels/423249981340778496/670954391641128960/821299580829564978
        self.ids["textureID"].texture.blit_buffer(
            buf, colorfmt='rgb', bufferfmt="ubyte"
        )
        print("updated texture")

class Noughtsandcrosses(BoxLayout):
    pass


class nandxApp(App):
    def build(self):
        from kivy.lang import Builder
        import os
        filesplit = __file__.split(os.sep)
        realpath = os.path.join( filesplit[0] + os.sep, *filesplit[1:-1], "texturetest.kv" )
        print(realpath )
        with open(realpath, "r") as f:
            kvstring = f.read()

        build_app_from_kv = Builder.load_string(kvstring)
        # return Noughtsandcrosses()
        return build_app_from_kv


if __name__ == "__main__":
    nandxApp().run()