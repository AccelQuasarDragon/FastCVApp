# https://stackoverflow.com/questions/34197984/kivy-filechooser-list-directories-only

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from os.path import join, isdir

Builder.load_string("""
<MyWidget>:
    FileChooserListView:
        filters: [root.is_dir]
""")

class MyWidget(BoxLayout):
    def is_dir(self, directory, filename):
        return isdir(join(directory, filename))

class MyApp(App):
    def build(self):
        return MyWidget()

if __name__ == '__main__':
    MyApp().run()