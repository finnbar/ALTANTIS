"""
Allows submarines to communicate with one another.
"""

from utils import diagonal_distance
from state import get_subs, get_sub
from npc import get_npcs, get_npc

from random import random
from time import time as now

GARBLE = 10
COMMS_COOLDOWN = 30

class CommsSystem():
    def __init__(self, sub):
        self.sub = sub
        # last_comms is the time when the Comms were last used.
        self.last_comms = 0
    
    def garble(self, content, distance):
        """
        We define the message error as the proportion of incorrect characters
        in a message. This error increases with distance between two subs.
        We define this error as GARBLE/comms per point of distance.
        The error never goes above 100%. Messages with 100% are not received.
        (Note: the clarity keyword effectively reduces distance by 2x comms.)
        """
        comms_power = self.sub.power.get_power("comms")
        if comms_power == 0:
            return None
        if "clarity" in self.sub.keywords:
            distance -= 2*comms_power
            distance = max(0, distance)
        message_error = min(distance * GARBLE / comms_power, 100)
        if message_error == 100:
            return None
        new_content = list(content)
        for i in range(len(new_content)):
            if new_content[i] not in [" ", "\n", "\r"] and random() < message_error / 100:
                new_content[i] = "_"
        return "".join(new_content)

    async def broadcast(self, content):
        if self.last_comms + COMMS_COOLDOWN > now():
            return False
        
        my_pos = self.sub.movement.get_position()
        for subname in get_subs():
            if subname == self.sub.name:
                continue

            sub = get_sub(subname)

            dist = diagonal_distance(my_pos, sub.movement.get_position())
            garbled = self.garble(content, dist)
            if garbled is not None:
                await sub.send_message(f"**Message received from {self.sub.name.title()}**:\n`{garbled}`\n**END MESSAGE**", "captain")

        for npcname in get_npcs():
            npc = get_npc(npcname)

            dist = diagonal_distance(my_pos, npc.get_position())
            garbled = self.garble(content, dist)
            if garbled is not None:
                await npc.send_message(f"**Message received from {self.sub.name.title()}**:\n`{garbled}`\n**END MESSAGE**", "")
        self.last_comms = now()
        return True
    