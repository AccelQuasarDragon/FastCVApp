#  need a micro-test:
#  test will be a decorator modifying class methods
#  test will be using the decorator on a print function similar to how fastapi does it
#  final test will be to do class.method to see if the class method got changed
#  reference: https://pencilprogrammer.com/decorate-python-class/
'''
def mydecorator(student):
    #define a new display method
    def newdisplay(self):
        print('Name: ', self.name)
        print('Subject: Programming')
    
    #replace the display with newdisplay
    student.display = newdisplay
    
    #return the modified student 
    return student

@mydecorator
class Student:
    def __init__(self, name):
        self.name = name
        
    def display(self):
        print('Name:', self.name)
        

obj = Student('Pencil Programmer')
obj.display()
'''
'''
Name:  Pencil Programmer
Subject: Programming
'''

'''
GOOD EXAMPLE, but not what I want, it's the REVERSE!
I want to have a class and a decorator, and actually the class with decorate the function, NOT the decorator on the class!
try this anyways
'''

# def decoratorTest(classVar):
#     #new function for classVar:
#     def newGo(self):
#         print("SUCCESS!")
#     #replace the method on the class
#     classVar.go = newGo

#     return classVar

# #instantiate and try:
# @decoratorTest
# class testClass():
#     def __init__(self, name):
#         self.go()

#     def go(self):
#         print("FAIL")



# WANT: function that gets decorated by the class like in fastapi
# fastapi does: @app.SMTH(ARGS) <--- this is a class and the methods are decorators, actually much easier. <--- so this is probably a class that takes the function as an arg and returns the class, aka class decorator.
#               def function
# then what I do is:    fastCVApp.cv_func("whatever args I want") <--- and then this replaces the cv_func method that I call in fastCVApp
#                       def function

class classTEST():
    def cv_func(self, *args): #<--- this guy should be a decorator that replaces the class.cv_func with the supplied argument
        #for some reason self is testGuy, probably because decorators are run after the class is built, and the class is not instantiated at all
        # https://stackoverflow.com/a/36231802/16355112
        # At the time when _change_x is invoked, the class is still under construction, so there can't be any instances of the class. Because of this, your self argument is misleading. When it gets called, self is actually the function print_x.
        # now that classTEST is instantiated with app = classTEST(), self is the object instance and the 2nd thing is the function supplied by decorator
        # print("???",self, type(self), args)

        #with no class instantiated self is just a reference to the function supplied by decorator: ??? <function testGuy at 0x000001FAB360B520> ()
        # with class instantiated self is now the class and function supplied by decorator is the 1st arg in *args: ??? <__main__.classTEST object at 0x0000024ED1856350> <class '__main__.classTEST'> (<function testGuy at 0x0000024ED182B520>,)

        # print("FAIL!")
        # return self.cv_func()
        #what do I need? to get the function then set self.cv_func = that function
        self.cv_func = args[0] #this is wrong, I don't have a reference to the class
        return self

app = classTEST() #need this to instantiate class

# @classTEST.cv_func
# @classTEST().cv_func #this works lmao but need to do it better
@app.cv_func #this works lmao but need to do it better
def testGuy(*args):
    print("SUCCESS!")


app.cv_func()
