# https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
import multiprocessing
from kivy.app import App
from kivy.uix.label import Label

class MainApp(App):
    def build(self):
        return Label(text='Main App Window')
    def run(self):
        '''Launches the app in standalone mode.
        '''
        self._run_prepare()
        from kivy.base import runTouchApp
        runTouchApp()
        # self.stop()

class OtherApp(App):
    def build(self):
        return Label(text='Other App Window')

def open_parent():
    MainApp().run()

def open_child():
    OtherApp().run()

if __name__ == '__main__':
    a = multiprocessing.Process(target=open_parent)
    b = multiprocessing.Process(target=open_child)
    a.start()
    b.start()
    #problem was I get here and then it kills kivy
    import time
    # time.sleep(1000)
    time.sleep(30)