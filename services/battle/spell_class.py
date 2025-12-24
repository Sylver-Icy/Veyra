class Spell:
    def __init__(self, name, mana_cost):
        self.name = name
        self.mana_cost = mana_cost

    def can_cast(self, caster):
        return caster.mana >= self.mana_cost

    def cast(self, caster, target):
        """Base class to override in subclasses"""

        if not self.can_cast(caster):
            return False, f"Not enough mana to cast {self.name}"

        caster.mana -= self.mana_cost
        return True, f"{caster.name} casts {self.name}!"


class Fireball(Spell):
    def __init__(self):
        super().__init__("Fireball", 15)

    def cast(self, caster, target):
        ok, msg =  super().cast(caster, target)

        if not ok:
            return ok, msg
        dmg = 16
        target.hp -= dmg
        return True, f"{caster.name} hurls a Fireball at {target.name} dealing 19 dmg"

class Nightfall(Spell):
    def __init__(self):
        super().__init__("Nightfall", 9)

    def cast(self, caster, target):
        ok, msg = super().cast(caster, target)
        if not ok:
            return ok, msg

        duration = 5
        target.status_effect["nightfall"] = duration


        return True, f"{caster.name} curses {target.name} with Nightfall!"

class Heavyshot(Spell):
    def __init__(self):
        super().__init__("Heavyshot", 16)

    def cast(self, caster, target):
        ok, msg =  super().cast(caster, target)

        if not ok:
            return ok, msg

        target.hp = caster.hp

        return True, f"{caster.name} casts heavyshot on {target.name} setting both players HP equal"


class ErdtreeBlessing(Spell):
    def __init__(self):
        super().__init__("Erdtree Blessing", 14)

    def cast(self, caster, target):
        ok, msg = super().cast(caster, target)

        if not ok:
            return ok, msg

        duration = 4
        caster.status_effect["largeheal"] = duration

        return True, f"{caster.name} casted The Blessing of Erdtree"

class FrostBite(Spell):
    def __init__(self):
        super().__init__("FrostBite", 6)

    def cast(self, caster, target):
        ok, msg =  super().cast(caster, target)

        if not ok:
            return ok, msg

        target.frost += 6
        target.speed -= 1

        return True, f"{caster.name} blew a chilly wind of ice {target.name} speed lowered coz of shivering cold and frost is building up"

class VeilOfDarkness(Spell):
    def __init__(self):
        super().__init__("VeilOfDarkness", 10)

    def cast(self, caster, target):
        ok, msg = super().cast(caster, target)

        if not ok:
            return ok, msg

        duration = 4
        target.status_effect["veilofdarkness"] = duration

        return True, f"{caster.name} Created a very dense veil Of darkness"
