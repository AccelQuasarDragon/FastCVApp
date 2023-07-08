#example as per: https://stackoverflow.com/questions/71957402/the-on-drop-file-function-in-kivy-for-python-passes-5-arguments-but-only-3-argu
import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.button import Label
from kivy.core.window import Window


class Gui(App):

    def build(self):
        Window.bind(on_drop_file=self._on_file_drop)
        return Label(text = "Drag and Drop File here")

    def _on_file_drop(self, window, file_path, x, y):
        print(file_path)
        return


if __name__ == '__main__':
    drop = Gui()

    drop.run()