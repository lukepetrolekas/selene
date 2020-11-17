import re
import os
import sys
import operator
import commands
from commands import *

ACTOR = re.compile(r"\\@ifdefinable\{\\(?P<alias>[\w\d]+)\}{\\def\\.+\/\{(?P<actor>.+)\}\}")
DIALOGUE = re.compile(r'\\begin\{dialogue\}\{\\(?P<actor>\w+)\/(\s\((?P<blocking>.*)\))?\}\n\t?(?P<line>.*)\n\\end\{dialogue\}')

def format_line(s):
    return re.sub("--", u"\u2014", s) # em dash

if __name__ == '__main__':
    fn_in = sys.argv[1]
    fn_out = sys.argv[2]

    command_builders = []
    actor_resolver = {}

    with open(fn_in, 'r') as file:
        data = file.read()

        for m in re.finditer(ACTOR, data):
            command_builders.append(ActorBuilder(m.start(), m.group("alias"), m.group("actor")))
            actor_resolver[m.group("alias")] = m.group("actor")

        for m in re.finditer(DIALOGUE, data):
            command_builders.append(LineBuilder(m.start(), m.group("actor"), m.group("blocking"), format_line(m.group("line"))))

    # update all character shorthands
    for b in command_builders:
        if isinstance(b, commands.LineBuilder):
            for k,v in actor_resolver.items():
                b.line = re.sub(F"\\\\{k}\/", v, b.line)

    sorted(command_builders, key=lambda x: x.cindex)
    [print(x) for x in command_builders]
