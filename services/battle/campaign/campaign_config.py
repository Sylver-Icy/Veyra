CAMPAIGN_LEVELS = {
    1: {
        "weapon": "trainingblade",
        "spell": "fireball",
        "bonus_hp": -25,
        "bonus_mana": -5
    },
    2: {
        "weapon": "moonslasher",
        "spell": "frostbite",
        "bonus_hp": -10,
        "bonus_mana": -2
    },
    3: {
        "weapon": "trainingblade",
        "spell": "erdtreeblessing",
        "bonus_hp": 0,
        "bonus_mana": 0
    },
    4: {
        # Frost introduction (soft)
        "weapon": "moonslasher",
        "spell": "frostbite",
        "bonus_hp": 5,
        "bonus_mana": 0
    },
    5: {
        # Sustain vs pressure
        "weapon": "elephanthammer",
        "spell": "erdtreeblessing",
        "bonus_hp": 5,
        "bonus_mana": 0
    },
    6: {
        # Spell control & debuff extension
        "weapon": "eternaltome",
        "spell": "nightfall",
        "bonus_hp": 10,
        "bonus_mana": 5
    },
    7: {
        # Risk–reward chaos
        "weapon": "trainingblade",
        "spell": "heavyshot",
        "bonus_hp": 15,
        "bonus_mana": 5
    },
    8: {
        # Healing denial check
        "weapon": "darkblade",
        "spell": "fireball",
        "bonus_hp": 15,
        "bonus_mana": 0
    },
    9: {
        # Final exam: frost + denial + pressure
        "weapon": "moonslasher",
        "spell": "frostbite",
        "bonus_hp": 22,
        "bonus_mana": 8
    },
    10: {
        "weapon": "veyrasgrimoire",
        "spell": "veilofdarkness",
        "bonus_hp": 25,
        "bonus_mana": 10
    },
    11: {
        # Bardok introduction – curse & pressure
        "weapon": "bardoksclaymore",
        "spell": "nightfall",
        "bonus_hp": 10,
        "bonus_mana": 5,
        "lore": "Veyra watches in silence... then steps forward. She places her Grimoire and forbidden spell into your hands. \"You have proven your strength.\" The guard snaps. You do not deserve her favor. Rage burns in his eyes as he steps into the arena to prove her wrong."
    },
    12: {
        # Earthquake control phase
        "weapon": "bardoksclaymore",
        "spell": "earthquake",
        "bonus_hp": 15,
        "bonus_mana": 15,
        "lore": "The guard slams his weapon into the ground. The earth itself answers his fury. Cracks spread beneath your feet as he learns the art of Earthquake."
    },
    13: {
        # Sustained earthquake pressure
        "weapon": "bardoksclaymore",
        "spell": "earthquake",
        "bonus_hp": 5,
        "bonus_mana": 5,
        "lore": "His fury sharpens into hatred. Every repeated move irritates him. If you use the same stance twice in a row, his attack will rise."
    },
    14: {
        # Peak Bardok rage
        "weapon": "bardoksclaymore",
        "spell": "earthquake",
        "bonus_hp": 5,
        "bonus_mana": 10,
        "lore": "His rage reaches its peak. Flames erupt across the battlefield. The arena becomes living lava. Heat and fire surround you."
    },
    15: {
        # Frozen judgment
        "weapon": "moonslasher",
        "spell": "fireball",
        "bonus_hp": 10,
        "bonus_mana": 15,
        "lore": "Suddenly... silence. The flames vanish. Ice spreads across the arena. The guard exhales slowly. He is calm now. The cold will not be merciful."
    }
}

REWARD_CHART = {
    1: {"Gold": 40}, #40X Gold
    2: {176: 1}, #key reperesets item_id and value is amount
    3: {"Gold": 100},
    4: {"Gold": 250},
    5: {177: 2},
    6: {170: 4},
    7: {180: 5},
    8:{178: 2},
    9: {179: 1},
    10: {"Unlock 1": 0}, #Unlocks Veyra's sig weapon and spell
    11: {193: 1}, #Potion of energy regen II
    12: {157: 5}, #Flasks
    13: {180: 3}, #Hint Key
    14: {197: 2}, #Potion of luck III
    15: {199: 1}, #Potion of hatred
}