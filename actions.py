"""
The backend for all Discord actions, which allow players to control their sub.
"""

from utils import React, Message, OKAY_REACT, FAIL_REACT, to_pair_list
from state import get_subs, get_sub, add_team, remove_team
from world import draw_map, bury_treasure_at, get_square, investigate_square
from consts import direction_emoji
from npc import add_npc

# MOVEMENT

def move(direction, subname):
    """
    Records the team's direction.
    We then react to the message accordingly.
    """
    print("Setting direction of", subname, "to", direction)
    if subname in get_subs():
        # Store the move and return the correct emoji.
        if get_sub(subname).movement.set_direction(direction):
            return React(direction_emoji[direction])
    return FAIL_REACT

def teleport(subname, x, y):
    """
    Teleports team to (x,y), checking if the space is in the world.
    """
    print("Teleporting", subname, "to", (x,y))
    if subname in get_subs():
        sub = get_sub(subname)
        if sub.movement.set_position(x, y):
            return OKAY_REACT
    return FAIL_REACT

async def set_activation(team, value):
    """
    Sets the submarine's power to `value`.
    """
    sub = get_sub(team)
    if sub:
        print("Setting power of", team, "to", value)
        if sub.power.activated() == value:
            return Message(f"{team.title()} activation unchanged.")
        sub.power.activate(value)
        if sub.power.activated():
            await sub.send_to_all(f"{team.title()} is **ON** and running! Current direction: **{sub.movement.get_direction().upper()}**.")
            return OKAY_REACT
        await sub.send_to_all(f"{team.title()} is **OFF** and halted!")
        return OKAY_REACT
    return FAIL_REACT

# STATUS

def print_map(team, options=["w", "d", "s"]):
    """
    Prints the map from the perspective of one submarine, or all if team is None.
    """
    subs = []
    code_to_key = {"w": "Wall", "d": "Docking station", "s": "Storm", "t": "Treasure", "n": "NPC"}
    if options is True:
        options = code_to_key.keys()
    options = list(filter(lambda v: v in code_to_key, options))
    if team is None:
        subs = [get_sub(sub) for sub in get_subs()]
    else:
        sub = get_sub(team)
        if sub is None:
            return FAIL_REACT
        subs = [sub]
    print("Printing map for", subs)
    formatted = f"```\n"
    map_string = draw_map(subs, options)
    formatted += map_string + "\n```\n"
    subs_string = "**KEY**\n"
    for i in range(len(subs)):
        subs_string += f"{i}: {subs[i].name.title()}, "
    formatted += subs_string[:-2] + "\n"
    for o in options:
        formatted += f"{o.upper()}: {code_to_key[o]}\n"
    return Message(formatted[:-1])

def zoom_in(x, y, loop):
    return Message(investigate_square(x, y, loop))

def get_status(team, loop):
    sub = get_sub(team)
    if sub:
        status_message = sub.status_message(loop)
        return Message(status_message)
    return FAIL_REACT

def get_scan(team):
    sub = get_sub(team)
    if sub:
        return Message(sub.scan.previous_scan())
    return FAIL_REACT

# POWER

def power_systems(team, systems):
    """
    Powers `systems` of the submarine `team` if able.
    """
    sub = get_sub(team)
    if sub:
        result = sub.power.power_systems(systems)
        return Message(result)
    return FAIL_REACT

def unpower_systems(team, systems):
    """
    Unpowers `systems` of the submarine `team` if able.
    """
    sub = get_sub(team)
    if sub:
        result = sub.power.unpower_systems(systems)
        return Message(result)
    return FAIL_REACT

async def deal_damage(team, amount, reason):
    sub = get_sub(team)
    if sub:
        sub.damage(amount)
        if reason: await sub.send_to_all(reason)
        return OKAY_REACT
    return FAIL_REACT

async def heal_up(team, amount, reason):
    sub = get_sub(team)
    if sub:
        sub.power.heal(amount)
        if reason: await sub.send_to_all(reason)
        return OKAY_REACT
    return FAIL_REACT

async def upgrade_sub(team, amount):
    sub = get_sub(team)
    if sub:
        sub.power.modify_reactor(amount)
        await sub.send_message(f"Submarine **{team.title()}** was upgraded! Power cap increased by {amount}.", "engineer")
        return OKAY_REACT
    return FAIL_REACT

async def upgrade_sub_system(team, system, amount):
    sub = get_sub(team)
    if sub:
        if sub.power.modify_system(system, amount):
            await sub.send_message(f"Submarine **{team.title()}** was upgraded! **{system.title()}** max power increased by {amount}.", "engineer")
            return OKAY_REACT
    return FAIL_REACT

async def upgrade_sub_innate(team, system, amount):
    sub = get_sub(team)
    if sub:
        if sub.power.modify_innate(system, amount):
            await sub.send_message(f"Submarine **{team.title()}** was upgraded! **{system.title()}** innate power increased by {amount}.", "engineer")
            return OKAY_REACT
    return FAIL_REACT

async def add_system(team, system):
    sub = get_sub(team)
    if sub:
        if sub.power.add_system(system):
            await sub.send_message(f"Submarine **{team.title()}** was upgraded! New system **{system}** was installed.", "engineer")
            return OKAY_REACT
    return FAIL_REACT

# COMMS

async def shout_at_team(team, message):
    sub = get_sub(team)
    if sub:
        await sub.send_to_all(message)
        return OKAY_REACT
    return FAIL_REACT

async def broadcast(team, message):
    sub = get_sub(team)
    if sub and sub.power.activated():
        print(f"Going to broadcast {message}!")
        result = await sub.comms.broadcast(message)
        if result:
            return OKAY_REACT
        else:
            return Message("The radio is still in use! (It has a thirty second cooldown.)")
    return FAIL_REACT

# INVENTORY

async def arrange_trade(team, partner, items):
    pair_list = []
    try:
        pair_list = to_pair_list(items)
    except ValueError as _:
        return Message("Input list is badly formatted.")
    sub = get_sub(team)
    partner_sub = get_sub(partner)
    if sub and partner_sub:
        return Message(await sub.inventory.begin_trade(partner_sub, pair_list))
    return Message("Didn't recognise the submarine asked for.")

async def make_offer(team, items):
    pair_list = to_pair_list(items)
    if pair_list is None:
        return Message("Input list is badly formatted.")
    sub = get_sub(team)
    if sub:
        return Message(await sub.inventory.make_offer(pair_list))
    return FAIL_REACT

async def accept_offer(team):
    sub = get_sub(team)
    if sub:
        return Message(await sub.inventory.accept_trade())
    return FAIL_REACT

async def reject_offer(team):
    sub = get_sub(team)
    if sub:
        return Message(await sub.inventory.reject_trade())
    return FAIL_REACT

async def give_item_to_team(team, item, quantity):
    sub = get_sub(team)
    if sub:
        if sub.inventory.add(item, quantity):
            await sub.send_message(f"Obtained {quantity}x {item.title()}!", "captain")
            return OKAY_REACT
    return FAIL_REACT

async def take_item_from_team(team, item, quantity):
    sub = get_sub(team)
    if sub:
        if sub.inventory.remove(item, quantity):
            await sub.send_message(f"Lost {quantity}x {item.title()}!", "captain")
            return OKAY_REACT
    return FAIL_REACT

def drop_item(team, item):
    sub = get_sub(team)
    if sub:
        return Message(sub.inventory.drop(item))
    return FAIL_REACT

# ENGINEERING

async def give_team_puzzle(team, reason):
    sub = get_sub(team)
    if sub:
        await sub.puzzles.send_puzzle(reason)
        return OKAY_REACT
    return FAIL_REACT

async def answer_team_puzzle(team, answer):
    sub = get_sub(team)
    if sub:
        await sub.puzzles.resolve_puzzle(answer)
        return OKAY_REACT
    return FAIL_REACT

# CRANE

def drop_crane(team):
    sub = get_sub(team)
    if sub and sub.inventory.drop_crane():
        return OKAY_REACT
    return FAIL_REACT

# DANGER ZONE

async def kill_sub(team, verify):
    sub = get_sub(team)
    if sub and sub.name == verify:
        sub.damage(sub.power.total_power)
        await sub.send_to_all("Submarine took catastrophic damage and will die on next game loop.")
        return OKAY_REACT
    return FAIL_REACT

def delete_team(team):
    # DELETES THE TEAM IN QUESTION. DO NOT DO THIS UNLESS YOU ARE ABSOLUTELY CERTAIN.
    if remove_team(team):
        return OKAY_REACT
    return FAIL_REACT

# GAME MANAGEMENT

async def register(category, x, y):
    """
    Registers a team, setting them up with everything they could need.
    Requires a category with the required subchannels.
    ONLY RUNNABLE BY CONTROL.
    """
    print("Registering", category.name.lower())
    if add_team(category.name.lower(), category, x, y):
        sub = get_sub(category.name.lower())
        if sub:
            await sub.send_to_all(f"Channel registered for sub **{category.name.title()}**.")
            return OKAY_REACT
    return FAIL_REACT

# MAP MODIFICATION

def bury_treasure(name, x, y):
    if bury_treasure_at(name, (x, y)):
        return OKAY_REACT
    return FAIL_REACT

def add_attribute_to(x, y, attribute, value):
    square = get_square(x, y)
    if square and square.add_attribute(attribute, value):
        return OKAY_REACT
    return FAIL_REACT

def remove_attribute_from(x, y, attribute):
    square = get_square(x, y)
    if square and square.remove_attribute(attribute):
        return OKAY_REACT
    return FAIL_REACT

def add_npc_to_map(name, ntype, x, y):
    return Message(add_npc(name, ntype, x, y))

# WEAPONRY

def schedule_shot(x, y, team, damaging):
    sub = get_sub(team)
    if sub:
        return Message(sub.weapons.prepare_shot(damaging, x, y))
    return FAIL_REACT