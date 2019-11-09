import sys
import os
import chadwick
from ctypes import *

# print(sys.path)
# cdll.LoadLibrary("libc.so.6")
libc = CDLL("libc.so.6")
print(libc.fdopen)


class FILE(Structure):
    pass


f = "chadwick.term"
pyf = open(f, 'r')
print(F"type(pyf)  = {type(pyf)}")

# pyfp = pointer(pyf)
# print(F"type(pyfp) = {type(pyfp)}")

pyfd = os.fdopen(pyf.fileno(), 'rb', buffering=0)
print(F"type(pyfd) = {type(pyfd)}")

libc.fdopen.restype = POINTER(FILE) # c_void_p
fp = libc.fdopen(pyf.fileno(), 'r')
print(F"type(fp) = {type(fp)}")

convert_file = pythonapi.PyObject_AsFileDescriptor
convert_file.restype = POINTER(FILE) # c_void_p
convert_file.argtypes = [py_object]
cp = convert_file(pyfd)
print(F"type(cp) = {type(cp)}")

# cpfd = os.fdopen(cp, 'r')
# print(F"type(cpfd) = {type(cpfd)}")

# newfp = pythonapi.PyFile_FromFd(pyf)
try:
    g = chadwick.read_game(cp)
    if g:
        print("found a game.")
    else:
        print("NO game.")
    g1 = chadwick.libchadwick.cw_file_find_first_game(fp)
    if g1:
        print("found the first game.")
    else:
        print("NO first game.")
except Exception as e:
    print(F"Exception: {repr(e)}")

exit()
