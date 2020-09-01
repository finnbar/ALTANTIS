from ALTANTIS.utils.consts import TICK, CROSS

class DiscordAction():
    def __init__(self):
        pass

    async def do_status(self):
        pass

class React(DiscordAction):
    def __init__(self, react):
        self.react = react

    async def do_status(self, ctx):
        await ctx.message.add_reaction(self.react)

class Message(DiscordAction):
    def __init__(self, contents):
        self.contents = contents

    async def do_status(self, ctx):
        await ctx.send(self.contents)

OKAY_REACT = React(TICK)
FAIL_REACT = React(CROSS)

def to_react(status : bool):
    return OKAY_REACT if status else FAIL_REACT
