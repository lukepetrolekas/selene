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
    fn_in = sys.argv[1]
    fn_out = sys.argv[2]

    command_builders = []
    actor_resolver = {}

    with open(fn_in, 'r', encoding='utf-8') as file:
        data = file.read()

        d = DigiplayBuilder(data)

        with open(fn_out + "characters.rpy", 'w') as outscr:
            outscr.write(d.characters())

        with open(fn_out + "digiplay.rpy", 'w') as outscr:
            outscr.write(str(d))
