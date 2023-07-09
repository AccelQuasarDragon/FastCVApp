#reference: https://stackoverflow.com/questions/58075187/name-process-when-creating-it-with-pythons-subprocess-popen

import subprocess
import time

class NamedPopen(subprocess.Popen):
     """
     Like subprocess.Popen, but returns an object with a .name member
     """
     def __init__(self, *args, name=None, **kwargs):
         self.name = name
         super().__init__(*args, **kwargs)

fred = NamedPopen('print( "yabba dabba doo")', shell=True, name="fred")
barney = NamedPopen('print("hee hee, okay fred")', name="barney", shell=True)
print('... stay tuned ...')
fred.wait()
barney.wait()