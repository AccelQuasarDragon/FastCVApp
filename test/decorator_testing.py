def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Something is happening before the function is called.")
        func(*args, **kwargs)
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_whee():
    print("Whee!")

@my_decorator
def greet(name):
    print(f"Hello {name}")

say_whee()
greet("Za Warudo!")




# def decorator_factory(argument):
#     def decorator(function):
#         def wrapper(*args, **kwargs):
#             funny_stuff()
#             something_with_argument(argument)
#             result = function(*args, **kwargs)
#             more_funny_stuff()
#             return result
#         return wrapper
#     return decorator
print("==============================")
# https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments
def decoratorFunctionWithArguments(arg1, arg2, arg3):
    def wrap(f):
        print ("Inside wrap()")
        def wrapped_f(*args):
            print ("Inside wrapped_f()")
            print ("Decorator arguments:", arg1, arg2, arg3)
            f(*args)
            print ("After f(*args)")
        return wrapped_f
    return wrap

@decoratorFunctionWithArguments("hello", "world", 42)
def sayHello(a1, a2, a3, a4):
    print ('sayHello arguments:', a1, a2, a3, a4)

sayHello("A","B","V","X")