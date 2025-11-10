import re
import os
import sys
import operator
import commands
from commands import *

SLUG = re.compile(r'\\(ex|in)tslug\[(?P<time>.*)\]\{(?P<location>.*)\}(\s+\% WITH (?P<transition>.*))?')

FADE_IN = re.compile(r'\\fadein')
FADE_OUT = re.compile(r'\\fadeout')

STRIP_PAREN = re.compile(r'\\paren\{[^\}]+\}') # temp

if __name__ == '__main__':
    fn_in = '/home/aurix/projects/soulwater/soulwater_screenplay/' #sys.argv[1]
    fn_out = '/home/aurix/projects/soulwater/renpy-8.4.1-sdk/soulwater/game/' #sys.argv[2]

    command_builders = []
    actor_resolver = {}

    data = []

    with open(fn_in + "cast.tex", 'r', encoding='utf-8') as file:
        data.append(file.read())

    with open(fn_in + "locations.tex", 'r', encoding='utf-8') as file:
        data.append(file.read())


    with open(fn_in + "act1.tex", 'r', encoding='utf-8') as file:
        data.append(file.read())
    with open(fn_in + "act2.tex", 'r', encoding='utf-8') as file:
        data.append(file.read())
    with open(fn_in + "act3.tex", 'r', encoding='utf-8') as file:
        data.append(file.read())
    with open(fn_in + "act4.tex", 'r', encoding='utf-8') as file:
        data.append(file.read())
    with open(fn_in + "act5.tex", 'r', encoding='utf-8') as file:
        data.append(file.read())

    # merge file into one big string...
    
    data = " ".join(data)

    # loaded all files, now generate

    d = DigiplayBuilder(data)

    with open(fn_out + "characters.rpy", 'w') as outscr:
        outscr.write(d.characters())

    with open(fn_out + "digiplay.rpy", 'w') as outscr:
        outscr.write("label digiplay:\n" +  str(d))
