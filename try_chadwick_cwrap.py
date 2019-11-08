import sys
import os
import chadwick
import cwrap

print(sys.path)

f = "chadwick.term"
pyf = open(f, 'r')
print(F"type(pyf) = {type(pyf)}")

pyfd = os.fdopen(pyf.fileno(), 'r')
print(F"type(pyfd) = {type(pyfd)}")

try:
    with cwrap.open(f, "r") as fp:
    # with open(f, "r") as fp:
        print(F"type(fp) = {type(fp)}")
        cwfp = cwrap.CFILE(fp)
        print(F"type(cwfp) = {type(cwfp)}")
        g = chadwick.read_game(fp)
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
