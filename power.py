"""
Allows submarines to manage their power usage.
"""

from random import choice

class PowerManager():
    def __init__(self, sub):
        self.sub = sub
        self.active = False
        # power is a dictionary mapping systems to their current power.
        self.power = {"engines": 0, "scanners": 1, "comms": 1, "crane": 0, "weapons": 1}
        # power_max is the maximum power for each system.
        self.power_max = {"engines": 1, "scanners": 1, "comms": 2, "crane": 1, "weapons": 1}
        # total_power acts as health - if your total_power would go _below_ zero, you explode.
        self.total_power = 3
        # total_power_max allows for healing up until that cap.
        self.total_power_max = 3
        # innate power is power that you're not allowed to change.
        # Control can use this to provide a mandatory upgrade.
        self.innate_power = {"engines": 1}
        # Power only updates at game tick, so we need to keep track of the changes made.
        self.scheduled_power = self.power.copy()
        # Damage only happens at game tick, so we need to keep track of any taken.
        self.scheduled_damage = []

    def activate(self, value):
        self.active = value
        return True

    def activated(self):
        return self.active

    def get_power(self, system):
        """
        Returns the power given to a system, both innately and otherwise.
        """
        used = 0
        if system in self.power:
            used += self.power[system]
        if system in self.innate_power:
            used += self.innate_power[system]
        return used
    
    def add_system(self, systemname):
        """
        Adds a new system with max power 1.
        """
        if systemname in self.power:
            return False
        self.power[systemname] = 0
        self.power_max[systemname] = 1
        return True

    def power_use(self, power):
        use = 0
        for system in power:
            use += power[system]
        return use
    
    def apply_power_schedule(self):
        # Check for changes and add these to the string.
        message = ""
        for system in self.power:
            difference = self.scheduled_power[system] - self.power[system]
            connective = "increased"
            if difference < 0:
                connective = "decreased"
            if difference != 0:
                message += f"Power to **{system}** {connective} by {abs(difference)}.\n"
        self.power = self.scheduled_power
        if message == "":
            return None
        return message
    
    def modify_system(self, systemname, amount):
        """
        Upgrades or downgrades a system systemname by amount.
        Specify a negative amount to downgrade.
        """
        if not systemname in self.power_max:
            return False
        if self.power_max[systemname] + amount < 0:
            return False
        self.power_max[systemname] += amount
        self.power[systemname] = min(self.power[systemname], self.power_max[systemname])
        return True
    
    def modify_innate_system(self, systemname, amount):
        """
        Upgrades or downgrades an innate system systemname by amount.
        """
        if not systemname in self.power_max:
            return False
        current_innate = 0
        if systemname in self.innate_power:
            current_innate = self.innate_power[systemname]
        if current_innate + amount < 0:
            return False
        self.innate_power[systemname] = current_innate + amount
        return True
    
    def modify_reactor(self, amount):
        """
        Upgrades or downgrades reactor by amount.
        """
        if self.power_max - amount < 0:
            return False
        if amount > 0:
            self.heal(amount)
        else:
            self.damage(-amount)
        return True
    
    def power_systems(self, systems):
        """
        Attempts to give power to the list of things to power `systems`.
        Will not change anything if it would mean you go over the power cap.
        If you name a system that doesn't exist, it will not apply the changes.
        """
        if len(systems) > self.total_power - self.power_use(self.scheduled_power):
            return False
        power_copy = self.scheduled_power.copy()
        for system in systems:
            if system in power_copy:
                use = power_copy[system]
                maxi = self.power_max[system]
                use += 1
                if use > maxi:
                    return False
                power_copy[system] = use
            else:
                return False
        self.scheduled_power = power_copy
        return True
    
    def unpower_systems(self, systems):
        """
        Attempts to remove power from all of the named systems in `systems`.
        If you specify a system that doesn't exist, it will fail.
        """
        power_copy = self.scheduled_power.copy()
        for system in systems:
            if system in power_copy:
                use = power_copy[system]
                use -= 1
                if use < 0:
                    return False
                power_copy[system] = use
            else:
                return False
        self.scheduled_power = power_copy
        return True

    def run_damage(self, amount):
        if amount <= 0:
            return ""
        self.total_power -= 1
        # If the submarine is now below zero power, it explodes.
        if self.total_power < 0:
            self.activate(False)
            return "**SUBMARINE DESTROYED. PLEASE SPEAK TO CONTROL.**"
        # Otherwise, if there is unused power, damage that first.
        system = ""
        if self.power_use(self.power) < self.total_power:
            system = "reserves"
        else:
            # Pick a system at random to lose power.
            available_systems = filter(lambda system: self.power[system] > 0, self.power)
            system = choice(list(available_systems))
            self.unpower_systems([system])
        # If the submarine hits zero, soak up all remaining damage.
        if self.total_power == 0:
            return (
                f"Damage taken to {system}!\n"
                "**EMERGENCY SUBMARINE POWER INITIATED!!! ONLY BASIC ENGINE FUNCTIONALITY AVAILABLE!!!**"
            )
        # Else continue taking damage.
        message = self.run_damage(amount - 1)
        return f"Damage taken to {system}!\n" + message
    
    def damage(self, amount):
        self.scheduled_damage.append(amount)
    
    def damage_tick(self):
        damage_message = ""
        for hit in self.scheduled_damage:
            damage_message += self.run_damage(hit)
        self.scheduled_damage = []
        return damage_message

    def heal(self, amount):
        self.total_power = min(self.total_power + amount, self.total_power_max)
        return f"Healed back up to {self.total_power} power!"
    
    def status(self):
        message = f"**Power status** ({self.power_use(self.power)}/{self.total_power}/{self.total_power_max} used/available/max):\n"

        for system in self.power:
            use = self.power[system]
            maxi = self.power_max[system]
            innate = 0
            scheduled = self.scheduled_power[system]
            difference = scheduled - use

            if system in self.innate_power:
                innate = self.innate_power[system]

            # Don't print out information on systems that cannot be powered.
            if maxi + innate <= 0:
                continue

            power_status = f"({use}/{maxi}"
            if innate > 0 or difference != 0:
                power_status += " with"
            if innate > 0:
                power_status += f" {innate} innate"
                if difference != 0:
                    power_status += ","
            if difference != 0:
                plusminus = "+"
                if difference < 0:
                    plusminus = "-"
                power_status += f" {plusminus}{abs(difference)} scheduled"
            power_status += ")"

            system_status = "offline"
            if use + innate > 0:
                system_status = "online"
            message += f"* **{system.capitalize()}** is {system_status} {power_status}\n"

        return message + "\n"