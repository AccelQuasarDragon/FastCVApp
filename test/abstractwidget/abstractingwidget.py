'''
references:
https://stackoverflow.com/questions/46125196/kivy-error-raise-factoryexceptionunknown-class-s-name

https://www.geeksforgeeks.org/python-how-to-use-multiple-kv-files-in-kivy/
https://stackoverflow.com/questions/29332868/is-it-possible-to-read-from-more-than-one-kv-file-in-kivy-app
'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class Threebythreeone(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("how many times is this instanced? I call it twice in kv... IT GETS CALLED TWICE IF U CALL IT TWICE IN KV....")


class Noughtsandcrosses(BoxLayout):
    pass


class nandxApp(App):
    def build(self):
        from kivy.lang import Builder
        import os
        filesplit = __file__.split(os.sep)
        realpath = os.path.join( filesplit[0] + os.sep, *filesplit[1:-1], "Abstractingwidget.kv" )
        print(realpath )
        with open(realpath, "r") as f:
            kvstring = f.read()

        build_app_from_kv = Builder.load_string(kvstring)
        # return Noughtsandcrosses()
        return build_app_from_kv


if __name__ == "__main__":
    nandxApp().run()