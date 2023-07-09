# https://stackoverflow.com/questions/50552486/initialize-kivy-widget-values-from-python-on-program-start
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label

initial_text = "init text"


class MainApp(App):
    def build(self):
        return Label()

    def on_start(self):
        Clock.schedule_once(self.initialize_widgets, 5)

    def initialize_widgets(self, dt):
        print("self.root???", self.root)
        self.root.text = initial_text


if __name__ == '__main__':
    MainApp().run()