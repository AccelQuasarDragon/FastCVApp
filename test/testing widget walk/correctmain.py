import kivy
from kivy.app import App
from kivy.uix.label import Label
  
  
# Replace this with your 
# current version
kivy.require('1.11.1')  
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class UniqueButton(Button):
    def uniquecall(self, *args):
        print("uniquely called!")

class UniqueBox(BoxLayout):
    
    def TESTING(self, *args):
        #problems: widget loop only sees top level widgets, idk about screenmanagers either...
        # print("??")
        # print(instanceguy.get_running_app().root.walk(loopback=True))
        totallist = [x for x in instanceguy.get_running_app().root.walk(loopback=True)]
        # namesguy = [widgetVAR.__name__ for widgetVAR in instanceguy.get_running_app().root.walk(loopback=True)]
        idlist = [widgetVAR.ids for widgetVAR in instanceguy.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids")]
        widgetlist = [widgetVAR.ids for widgetVAR in instanceguy.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids") and "BOX3" in  widgetVAR.ids]
        widgetactual = [widgetVAR for widgetVAR in instanceguy.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids") and "testbutton" in widgetVAR.ids]
        print("tlist", totallist)
        # print("namesguy", namesguy)
        print("idlist", idlist)
        print("widgetlist", widgetlist)
        print("widgetactual", widgetactual) #, widgetactual[0].uniquecall()
        # print("widgetactual", widgetactual, widgetactual[0], widgetactual[0].__dict__, dir(widgetactual[0])) #, widgetactual[0].uniquecall()
        # print('???', instanceguy.get_running_app().root.ids["testbutton"].uniquecall)
        print('???', widgetactual[0].ids["testbutton"].uniquecall()) #["testbutton"].uniquecall()
        


# Defining a class
class MyFirstKivyApp(App):
      
    # Function that returns 
    # the root widget
    # def build(self):
          
        # Label with text Hello World is 
        # returned as root widget
        # return Label(text ="Hello World !")      
    pass
  
  
# Here our class is initialized
# and its run() method is called. 
# This initializes and starts 
# our Kivy application.
instanceguy = MyFirstKivyApp()
instanceguy.run()
