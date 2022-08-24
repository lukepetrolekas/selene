import re

class DigiplayBuilder():
    _shorthand = re.compile(r'\\(\w+)/')

    def __init__(self, s):
        self.s = s
        self.actor_builders = ActorBuilder.extract(s)
        self.command_builders = ["label digiplay:"] + LineBuilder.extract(s)

    def format(self, s):
        # very obvious optimization. If there is no \, there is nothing
        # needed to check for substitutes.
        if '\\' not in s:
            return s

        for ab in self.actor_builders:
            s = s.replace(F"\\{ab.alias}/", ab.actor)

        return s

    def characters(self):
        return "label characters:\n" + '\n'.join([str(x) for x in self.actor_builders])

    def __str__(self):
        return '\n'.join([self.format(str(x)) for x in self.command_builders])

class CommandBuilder():
    def __init__(self, cindex):
        self.cindex = cindex

class CodeBuilder(CommandBuilder):
    def __init__(self, cindex, cmd):
        super().__init__(cindex)
        self.cmd = cmd

    def __str__(self):
        return self.cmd

class SlugBuilder(CommandBuilder):
    def __init__(self, cindex, time, location, transition):
        super().__init__(cindex)
        self.time = time
        self.location = location
        self.transition = transition
        
    def __str__(self):
        return F"    scene bg {self.location}" + (F"\n    with {self.transition}" if self.transition else "")

class ActorBuilder(CommandBuilder):
    _actor = re.compile(r"\\@ifdefinable\{\\(?P<alias>[\w\d]+)\}{\\def\\.+\/\{(?P<actor>.+)\}\}")

    @staticmethod
    def extract(s, offset=0):
        actors = []

        for m in re.finditer(ActorBuilder._actor, s):
            actors.append(ActorBuilder(offset + m.start(), m.group("alias"), m.group("actor"), "FFF"))

        return actors

    def __init__(self, cindex, alias, actor, colorHex):
        super().__init__(cindex)
        self.alias = alias
        self.actor = actor
        self.colorHex = colorHex

    def __str__(self):
        return F"    define {self.alias} = Character(\"{self.actor.upper()}\", color=\"#{self.colorHex}\")"

class LineBuilder(CommandBuilder):
    _regex = re.compile(r'\\begin{dialogue}{\\(?P<actor>\w+)/}\s*(\#(?P<expr>\w+))?\s*(\@(?P<block>\w+))?\n(?P<line>(.*|\n)+)\n\\end{dialogue}')
    _italics = re.compile(r'\\emph\{([^\}]+)\}')

    @staticmethod
    def extract(s, offset=0):
        lines = []

        for m in re.finditer(LineBuilder._regex, s):
            lines.append(LineBuilder(offset + m.start(), m.group("actor"), m.group("expr"), m.group("block"), m.group("line")))

        return lines

    @staticmethod
    def format(s):
        s = re.sub("--", u"\u2014", s) # em dash
        s = re.sub("'", u"\u2019", s) # apostrophe to single quote (asthetic)
        s = re.sub("\.\.\.", u"\u2026", s) # ellipsis
        s = re.sub(f"\"", "\\\"", s) # quotes within line
        s = LineBuilder._italics.sub(r'{i}\g<1>{/i}', s) #italics
        s = s.strip()
        return s

    def __init__(self, cindex, actor, expr, block, line):
        super().__init__(cindex)
        self.actor = actor
        self.expr = expr
        self.block = block
        self.line = line

    def __str__(self):
        output = ""
        for index, l in enumerate(self.line.splitlines()):
            l = LineBuilder.format(l)

            match l:
                case '\\beat':
                    continue
                case '\\pause':
                    continue

            if index == 0:
                output = F"    {self.actor} \"{l}\""
            else:
                output = output + F"\n    extend \" {l}\""

        return output