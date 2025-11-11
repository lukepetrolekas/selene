import re

class DigiplayBuilder():
    _shorthand = re.compile(r'\\(\w+)/')

    def __init__(self, s):
        self.s = s
        self.actor_builders = ActorBuilder.extract(s)
        self.command_builders = LineBuilder.extract(s)
        self.command_builders.extend(NarrationBuilder.extract(s))
        self.command_builders.extend(BeatBuilder.extract(s))
        self.command_builders.extend(SoundBuilder.extract(s))
        self.command_builders.extend(BgBuilder.extract(s))
        self.command_builders.extend(CodeBuilder.extract(s))

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
        # need to sort by cindex
        return '\n'.join([self.format(str(x)) for x in sorted(self.command_builders, key= lambda b: b.cindex)])

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

        for m in re.finditer(ActorBuilder._actor,s):
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
    _regex = re.compile(r'\\begin\{dialogue\}\{\\(?P<actor>\w+)\/\}\n(\t+)(?P<line>.*)\n\\end\{dialogue\}')
    _italics = re.compile(r'\\emph\{([^\}]+)\}')
    _parens = re.compile(r'\\paren\{([^\}]+)\}')

    @staticmethod
    def extract(s, offset=0):
        lines = []

        for m in re.finditer(LineBuilder._regex, s):
            lines.append(LineBuilder(offset + m.start(), m.group("actor"), m.group("line")))

        return lines

    @staticmethod
    def format(s):
        s = re.sub("--", u"\u2014", s) # em dash
        s = re.sub("'", u"\u2019", s) # apostrophe to single quote (asthetic)
        s = re.sub(r"\.\.\.", u"\u2026", s) # ellipsis
        s = re.sub(f"\"", "\\\"", s) # quotes within line
        s = LineBuilder._italics.sub(r'{i}\g<1>{/i}', s) #italics
        s = LineBuilder._parens.sub(r'{size=18}{i}\g<1>{/i}{/size} ', s) #put these comments into italics and shrink
        s = s.strip()
        return s

    def __init__(self, cindex, actor, line):
        super().__init__(cindex)
        self.actor = actor
        self.line = line

    def __str__(self):
        output = ""
        for index, l in enumerate(self.line.splitlines()):
            l = LineBuilder.format(l)

            if index == 0:
                output = F"    {self.actor} \"{l}\""
            else:
                output = output + F"\n    extend \" {l}\""

        return output
    
class NarrationBuilder(CommandBuilder):
    _narration = re.compile(r'\\narr\{(?P<narration>[^\}]+)\}')

    @staticmethod
    def extract(s, offset=0):
        narrations = []

        for m in re.finditer(NarrationBuilder._narration,s):
            narrations.append(NarrationBuilder(offset + m.start(), m.group("narration"), "FFF"))

        return narrations

    def __init__(self, cindex, narration, colorHex):
        super().__init__(cindex)
        self.narration = narration
        self.colorHex = colorHex

    def __str__(self):
        return F"    \"{self.narration}\""
    
    
class BeatBuilder(CommandBuilder):
    # only consider beats on newlines, and not in the middle of someone speaking...
    _narration = re.compile(r'\n\\beat')

    @staticmethod
    def extract(s, offset=0):
        narrations = []

        for m in re.finditer(BeatBuilder._narration,s):
            narrations.append(BeatBuilder(offset + m.start()))

        return narrations

    def __init__(self, cindex):
        super().__init__(cindex)

    def __str__(self):
        return F"    pause 2"

    
class SoundBuilder(CommandBuilder):
    #I only care about the file, in 2nd argument
    _narration = re.compile(r'\\sound\{[^\}]+\}\{(?P<sfx>[^\}]+)\}')

    @staticmethod
    def extract(s, offset=0):
        narrations = []

        for m in re.finditer(SoundBuilder._narration,s):
            narrations.append(SoundBuilder(offset + m.start(), m.group("sfx")))

        return narrations

    def __init__(self, cindex, sfx):
        super().__init__(cindex)
        self.sfx = sfx

    def __str__(self):
        return F"    play sound {self.sfx}"

class BgBuilder(CommandBuilder):
    _bg = re.compile(r'\\(ex|in)tslug\[\\(?P<time>\w+)\/\]\{\\(?P<bg>\w+)\/\}(\s*%\s*(?P<trans>\w+))?')

    @staticmethod
    def extract(s, offset=0):
        extractions = []

        for m in re.finditer(BgBuilder._bg,s):
            extractions.append(BgBuilder(offset + m.start(), m.group("time"), m.group("bg"), m.group("trans")))

        return extractions

    def __init__(self, cindex, time, bg, trans):
        super().__init__(cindex)
        self.time = time
        self.bg = bg
        self.trans = "dissolve" if trans is None else trans

    def __str__(self):
        return F"    scene bg_{self.bg}_{self.time}\n    with {self.trans}"


    
class CodeBuilder(CommandBuilder):
    _narration = re.compile(r'%C\s*(?P<code>[^\n]+)')

    @staticmethod
    def extract(s, offset=0):
        extractions = []

        for m in re.finditer(CodeBuilder._narration,s):
            extractions.append(CodeBuilder(offset + m.start(), m.group("code")))

        return extractions

    def __init__(self, cindex, code):
        super().__init__(cindex)
        self.code = code

    def __str__(self):
        return F"    {self.code}"