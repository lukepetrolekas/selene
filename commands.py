class CommandBuilder():
    def __init__(self, cindex):
        self.cindex = cindex

class ActorBuilder(CommandBuilder):
    def __init__(self, cindex, alias, actor):
        super().__init__(cindex)
        self.alias = alias
        self.actor = actor

    def __str__(self):
        return F"define {self.alias} = Character(\"{self.actor.upper()}\")\n"

class LineBuilder(CommandBuilder):
    def __init__(self, cindex, actor, blocking, line):
        super().__init__(cindex)
        self.actor = actor
        self.blocking = blocking
        self.line = line

    def __str__(self):
        return F"    {self.actor} \"{self.line}\""