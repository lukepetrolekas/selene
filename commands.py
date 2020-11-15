class CommandBuilder():
    def __init__(self, cindex):
        self.cindex = cindex

class LineBuilder(CommandBuilder):
    def __init__(self, cindex, actor, blocking, line):
        super().__init__(cindex)
        self.actor = actor
        self.blocking = blocking
        self.line = line

    def __str__(self):
        return self.line