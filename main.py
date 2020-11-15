import re
import os
import sys

DIALOGUE = re.compile(r'\\begin\{dialogue\}\{\\(?P<name>\w+)\/(\s\((?P<direction>.*)\))?\}\n\t?(?P<dialogue>.*)\n\\end\{dialogue\}')

if __name__ == '__main__':
    fn_in = sys.argv[1]
    fn_out = sys.argv[2]

    with open(fn_in, 'r') as file:
        data = file.read()

        for line in re.finditer(DIALOGUE, data):
            print(line.group("dialogue"))
