"""
A file for useful control and news functionality.
"""

import discord

control_alerts = None
news_alerts = None

async def notify_control(event : str):
    if control_alerts:
        await control_alerts.send(event)

def init_control_notifs(channel : discord.TextChannel):
    global control_alerts
    control_alerts = channel

async def notify_news(event : str):
    if news_alerts:
        await news_alerts.send(event)

def init_news_notifs(channel : discord.TextChannel):
    global news_alerts
    news_alerts = channel