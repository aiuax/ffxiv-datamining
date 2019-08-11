#!/bin/env python
import os
import sys
from shutil import copyfile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: {0} in_file".format(sys.argv[0]))

    leaf = os.path.split(sys.argv[1])[1]
    in_file_path = sys.argv[1]
    out_file_path = "./{0}.temp".format(leaf)
    with open(out_file_path, 'w', encoding="utf-8-sig") as out_file:
        with open(in_file_path, 'r', encoding="utf-8-sig") as in_file:
            line = in_file.readline()
            while line:
                while line.count('"') % 2:
                    line = line.rstrip('\n')
                    line += in_file.readline()
                out_file.write(line)
                line = in_file.readline()
    copyfile(out_file_path, in_file_path)
    os.remove(out_file_path)
