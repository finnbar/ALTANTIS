"""
A file for useful control functionality.
"""

control_alerts = None

async def notify_control(event):
    if control_alerts:
        await control_alerts.send(event)

def init_control_notifs(channel):
    global control_alerts
    control_alerts = channel