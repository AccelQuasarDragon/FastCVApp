import os, sys
def open_kivy(*args):
    # infinite recursion bug when packaging with pyinstaller with no console: https://github.com/kivy/kivy/issues/8074#issuecomment-1364595283
    if sys.__stdout__ is None or sys.__stderr__ is None:
        os.environ["KIVY_NO_CONSOLELOG"] = "1"
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.graphics.texture import Texture
    from kivy.clock import Clock
    from kivy.modules import inspector
    from kivy.core.window import Window
    from kivy.uix.button import Button

    class MainApp(App):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # remember that the KV string IS THE ACTUAL FILE AND MUST BE INDENTED PROPERLY TO THE LEFT!
            self.KV_string = f"""
#:import kivy.app kivy.app

Button: #remember to return a root widget
    text: "test"
"""
        def build(self):
            build_app_from_kv = Builder.load_string(self.KV_string)
            button = Button(text="Test")
            inspector.create_inspector(Window, button)
            return build_app_from_kv

    MainApp().run()

open_kivy()