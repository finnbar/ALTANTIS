"""
A file for useful control functionality.
"""

control_controller = None

async def notify_control(event):
    await control_controller.send(event)

def init_control(client):
    global control_controller
    control_controller = client