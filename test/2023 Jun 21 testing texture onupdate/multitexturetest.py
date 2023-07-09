#reference: https://discord.com/channels/423249981340778496/423250272316293120/897398151466594314

from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics import Rectangle, BindTexture, Fbo
from kivy.properties import (ObjectProperty,)
from PIL import Image as image 
from kivy.graphics.texture import Texture
import numpy as np

ALPHA_GAUSSIAN_SHADER = """
$HEADER$

uniform sampler2D texture1;
uniform vec2 position;
uniform float horizontal_std;
uniform float vertical_std;

void main(void) {{
    float alpha;
    if ((position.x != 0.0 || position.y != 0.0) && (horizontal_std != 0.0 && vertical_std != 0.0)) {{
        alpha = 1.0 - (exp(-pow((tex_coord0.x - position.x) / horizontal_std, 2.0)) * exp(-pow((tex_coord0.y - 1.0 + position.y) / vertical_std, 2.0)));
    }} else {{
        alpha = 1.0;
    }}
    gl_FragColor = alpha * texture2D(texture0, tex_coord0) + (1.0 - alpha) * texture2D(texture1, tex_coord0);
}}
"""

class MultitextureWidget(Image):
    unblurred_texture = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  

        shader = ALPHA_GAUSSIAN_SHADER

        self.blurred_picture = image.open('blur_picture.jpg')
        self.unblurred_picture = image.open('picture.jpg')

        self.unblurred_texture = Texture.create(size=(self.blurred_picture.size), colorfmt='rgb')
        self.unblurred_texture.uvpos  = (0,  1)
        self.unblurred_texture.uvsize = (1, -1)
        self.unblurred_texture.blit_buffer(np.array(self.unblurred_picture).tostring(), colorfmt='rgb')


        self.texture = Texture.create(size=(self.blurred_picture.size), colorfmt='rgb')
        self.texture.uvpos  = (0,  1)
        self.texture.uvsize = (1, -1)
        self.texture.blit_buffer(np.array(self.blurred_picture).tostring(), colorfmt='rgb') 
        self.texture_size = list(self.texture.size)


        with self.canvas:
            self.fbo = Fbo(size=self.size)
        with self.fbo:
            BindTexture(texture=self.texture, index=0)
            BindTexture(texture=self.unblurred_texture, index=1)
            self.fbo_rectangle = Rectangle(pos=self.pos, size=self.size, texture=self.texture)
        self.fbo["texture1"] = 1

        self.fbo.shader.fs = shader.format(r_l_asym=0)


    def on_size(self, instance, value):
        self.fbo_rectangle.size = self.texture_size
        self.fbo.size = self.texture_size
        self.texture = self.fbo.texture
        self.fbo.draw()


    def on_texture(self, instance, value):
        pass

    def on_touch_down(self,touch):
        spos = [0.5, 0.5] #Example of coordinates 
        self.update_shader(spos)


    def update_shader(self, position):
        
        #Here is my code to update my texture ? 
        pass

class MultitextureApp(App):

    def build(self):
        return MultitextureWidget()


if __name__ == '__main__':
    MultitextureApp().run()