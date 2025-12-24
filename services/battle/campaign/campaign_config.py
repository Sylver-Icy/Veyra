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
        "bonus_hp": 15,
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
        "bonus_hp": 20,
        "bonus_mana": 5
    },
    8: {
        # Healing denial check
        "weapon": "darkblade",
        "spell": "fireball",
        "bonus_hp": 25,
        "bonus_mana": 0
    },
    9: {
        # Final exam: frost + denial + pressure
        "weapon": "moonslasher",
        "spell": "frostbite",
        "bonus_hp": 15,
        "bonus_mana": 10
    },
    10: {
        "weapon": "veyrasgrimoire",
        "spell": "veilofdarkness",
        "bonus_hp": 0,
        "bonus_mana": 20
    }
}

REWARD_CHART = {
    1: {"Gold": 40}, #40X Gold
    2: {176: 1}, #key reperesets item_id and value is amount
    3: {"Gold": 100},
    4: {"Gold": 250},
    5: {177: 2},
    6: {183: 4},
    7: {180: 5},
    8:{178: 2},
    9: {179: 1},
    10: {"Unlock": 0} #Unlocks Veyra's sig weapon and spell
}