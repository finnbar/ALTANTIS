import discord

async def create_or_return_role(guild : discord.Guild, role : str, **kwargs) -> discord.Role:
    all_roles = await guild.fetch_roles()
    for r in all_roles:
        if r.name == role:
            return r
    return await guild.create_role(name=role, **kwargs)