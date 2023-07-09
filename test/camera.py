'''
Camera Example
==============

This example demonstrates a simple use of the camera. It shows a window with
a buttoned labelled 'play' to turn the camera on and off. Note that
not finding a camera, perhaps because gstreamer is not installed, will
throw an exception during the kv language processing.

'''

# Uncomment these lines to see all the messages
# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import time
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    # Camera:
    #     id: camera
    #     resolution: (640, 480)
    #     play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')


class CameraClick(BoxLayout):
    pass
    # def capture(self):
    #     '''
    #     Function to capture the images and give them the names
    #     according to their captured time and date.
    #     '''
    #     camera = self.ids['camera']
    #     timestr = time.strftime("%Y%m%d_%H%M%S")
    #     camera.export_to_png("IMG_{}.png".format(timestr))
    #     print("Captured")


class TestCamera(App):

    def build(self):
        return CameraClick()
    
    def on_start(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self.ROOTWTF, 0)
    def ROOTWTF(self, *args, **kwargs):
        print("WHY CANT I DO APP GET CURRENT APP WTF1", App)
        print("WHY CANT I DO APP GET CURRENT APP WTF2", App.get_running_app())
        # https://stackoverflow.com/questions/54616982/arising-errors-in-kivy-when-root-widget-comes-from-an-instance-from-kv-file
        '''
        Or you can return the root widget from the kv file, if you captured the returned root widget from loading the kv file (or string). For example, theRoot = Builder.load_file('somefile.kv') and return theRoot.
        '''
        print("WHY CANT I DO APP GET CURRENT APP WTF3", App.get_running_app().root)

if __name__ == '__main__':
    TestCamera().run()