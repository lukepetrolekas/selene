import re
import os
import sys
import operator
import commands
from commands import *

ACTOR = re.compile(r"\\@ifdefinable\{\\(?P<alias>[\w\d]+)\}{\\def\\.+\/\{(?P<actor>.+)\}\}")
DIALOGUE = re.compile(r'\\begin\{dialogue\}\{\\(?P<actor>\w+)\/(\s\((?P<blocking>.*)\))?\}\n\t?(?P<line>.*)\n\\end\{dialogue\}')

if __name__ == '__main__':
    fn_in = sys.argv[1]
    fn_out = sys.argv[2]

    command_builders = []

    with open(fn_in, 'r') as file:
        data = file.read()

        for m in re.finditer(ACTOR, data):
            command_builders.append(ActorBuilder(m.start(), m.group("alias"), m.group("actor")))

        for m in re.finditer(DIALOGUE, data):
            command_builders.append(LineBuilder(m.start(), m.group("actor"), m.group("blocking"), m.group("line")))

    sorted(command_builders, key=lambda x: x.cindex)
    [print(x) for x in command_builders]
