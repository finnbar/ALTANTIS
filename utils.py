class Status():
    def __init__(self):
        pass

    async def do_status(self):
        pass

class React(Status):
    def __init__(self, react):
        self.react = react

    async def do_status(self, ctx):
        await ctx.message.add_reaction(self.react)

class Message(Status):
    def __init__(self, contents):
        self.contents = contents

    async def do_status(self, ctx):
        await ctx.send(self.contents)
