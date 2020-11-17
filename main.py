import re
import os
import sys
import operator
import commands
from commands import *

SLUG = re.compile(r'\\(ex|in)tslug\[(?P<time>.*)\]\{(?P<location>.*)\}(\s+\% WITH (?P<transition>.*))?')

ACTOR = re.compile(r"\\@ifdefinable\{\\(?P<alias>[\w\d]+)\}{\\def\\.+\/\{(?P<actor>.+)\}\}")
DIALOGUE = re.compile(r'\\begin\{dialogue\}\{\\(?P<actor>\w+)\/(\s\((?P<blocking>.*)\))?\}\n\t?(?P<line>.*)\n\\end\{dialogue\}')

FADE_IN = re.compile(r'\\fadein')
FADE_OUT = re.compile(r'\\fadeout')

STRIP_PAREN = re.compile(r'\\paren\{[^\}]+\}') # temp

def format_line(s):
    s = re.sub("--", u"\u2014", s) # em dash
    s = re.sub(f"\"", "\\\"", s) # quotes
    s = re.sub(STRIP_PAREN, '', s) # temp
    return s

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
            
        for m in re.finditer(FADE_IN, data):
            command_builders.append(CodeBuilder(m.start(), "label start:"))

        for m in re.finditer(SLUG, data):
            command_builders.append(SlugBuilder(m.start(), m.group("time"), m.group("location"), m.group("transition")))

        for m in re.finditer(DIALOGUE, data):
            command_builders.append(LineBuilder(m.start(), m.group("actor"), m.group("blocking"), format_line(m.group("line"))))

        for m in re.finditer(FADE_OUT, data):
            command_builders.append(CodeBuilder(m.start(), "    return\n"))

    # update all scenes
    for b in command_builders:
        if isinstance(b, commands.SlugBuilder):
            b.location = re.sub("[^A-Za-z]", '', b.location) # temp
                
    # update all character shorthands
    for b in command_builders:
        if isinstance(b, commands.LineBuilder):
            for k,v in actor_resolver.items():
                b.line = re.sub(F"\\\\{k}\/", v, b.line)

    command_builders.sort(key=lambda x: x.cindex)
    r = '\n'.join([x.__str__() for x in command_builders])

    with open(fn_out, 'w') as outscr:
        outscr.write(r)