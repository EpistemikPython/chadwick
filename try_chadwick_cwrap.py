import sys
import os
from pychadwick.libutils import ChadwickLibrary as cwlib

print(sys.path)

f = "chadwick.term"
pyf = open(f, 'r')
print(F"type(pyf) = {type(pyf)}")

pyfd = os.fdopen(pyf.fileno(), 'r')
print(F"type(pyfd) = {type(pyfd)}")

try:
    with cwlib.cwrap.open(f, "r") as fp:
    # with open(f, "r") as fp:
        print(F"type(fp) = {type(fp)}")
        cwfp = cwlib.cwrap.CFILE(fp)
        print(F"type(cwfp) = {type(cwfp)}")
        g = cwlib.read_game(fp)
        if g:
            print("found a game.")
        else:
            print("NO game.")
        g1 = cwlib.cw_file_find_first_game(fp)
        if g1:
            print("found the first game.")
        else:
            print("NO first game.")
except Exception as e:
    print(F"Exception: {repr(e)}")
