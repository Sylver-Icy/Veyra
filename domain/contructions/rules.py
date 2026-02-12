BUILDINGS = {
    "moonroot": {
        "name": "Moon Root",
        "description": "A magical tree that attracts fairies. More levels, more tiny freeloaders.",

        "levels": {
            1: {
                "work_required": 10,
                "space_required": 26,
                "description": "A young sapling. One lonely fairy shows up."
            },
            2: {
                "work_required": 20,
                "space_required": 26,
                "description": "Tree grows stronger. Fairies start noticing."
            },
            3: {
                "work_required": 35,
                "space_required": 26,
                "description": "Healthy magical tree. Fairy traffic increases."
            },
            4: {
                "work_required": 55,
                "space_required": 26,
                "description": "Radiating fairy energy. They practically move in."
            },
            5: {
                "work_required": 80,
                "space_required": 26,
                "description": "Peak fairy magnet. You're basically running a fairy hostel."
            },
        }
    },

    "feedbox": {
        "name": "Feedbox",
        "description": "Stores food so your fairies stop acting like starving toddlers.",

        "levels": {
            1: {
                "work_required": 8,
                "space_required": 4,
                "description": "Basic wooden box. Fairies eat... sometimes."
            },
            2: {
                "work_required": 16,
                "space_required": 4,
                "description": "Better storage. Less fairy whining."
            },
            3: {
                "work_required": 28,
                "space_required": 4,
                "description": "Organized feeding. Fairies slightly impressed."
            },
            4: {
                "work_required": 45,
                "space_required": 4,
                "description": "Efficient supply. Fairies now spoiled."
            },
            5: {
                "work_required": 70,
                "space_required": 4,
                "description": "Luxury buffet tier. Fairies living their best life."
            },
        }
    },

    "snowman": {
        "name": "Snowman",
        "description": "A cheerful snowman that boosts fairy happiness for reasons no one understands.",

        "levels": {
            1: {
                "work_required": 5,
                "space_required": 6,
                "description": "Tiny snow buddy. Mild fairy joy."
            },
            2: {
                "work_required": 12,
                "space_required": 6,
                "description": "Better snowman. Fairies vibe with it."
            },
            3: {
                "work_required": 22,
                "space_required": 6,
                "description": "Stylish snow icon. Fairies feel festive."
            },
            4: {
                "work_required": 38,
                "space_required": 6,
                "description": "Legendary snow presence. Happiness intensifies."
            },
            5: {
                "work_required": 60,
                "space_required": 6,
                "description": "Mythical snowman. Fairies emotionally attached."
            },
        }
    }
}


def get_space_required(building_key: str, level: int = 1) -> int:
    """
    Return the space required for a given building at a specific level.

    Args:
        building_key (str): Internal key of the building (e.g., "moonroot").
        level (int): Building level. Defaults to 1.

    Returns:
        int: Space required for the building level.

    Raises:
        KeyError: If the building or level does not exist.
    """

    building = BUILDINGS[building_key]
    return building["levels"][level]["space_required"]

