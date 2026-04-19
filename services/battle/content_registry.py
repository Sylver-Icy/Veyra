from dataclasses import dataclass, field
from typing import Any, Callable

from services.battle.arena_class import FrozenArena, IrritationArena, LavaArena, NullArena
from services.battle.campaign.bardok_ai import BardokAI
from services.battle.spell_class import (
    Earthquake,
    ErdtreeBlessing,
    Fireball,
    FrostBite,
    Heavyshot,
    Nightfall,
    VeilOfDarkness,
)
from services.battle.veyra_ai import VeyraAI
from services.battle.weapon_class import (
    BardoksClaymore,
    DarkBlade,
    ElephantHammer,
    EternalTome,
    MoonSlasher,
    TrainingBlade,
    VeyrasGrimoire,
)


@dataclass(frozen=True)
class WeaponDefinition:
    key: str
    label: str
    unlock_stage: int
    factory: Callable[[], Any]
    tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SpellDefinition:
    key: str
    label: str
    unlock_stage: int
    factory: Callable[[], Any]
    tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ArenaDefinition:
    key: str
    label: str
    factory: Callable[[], Any]


@dataclass(frozen=True)
class NPCDefinition:
    key: str
    label: str
    ai_factory: Callable[..., Any]


class ContentRegistry:
    def __init__(self):
        self._weapons: dict[str, WeaponDefinition] = {}
        self._spells: dict[str, SpellDefinition] = {}
        self._arenas: dict[str, ArenaDefinition] = {}
        self._npcs: dict[str, NPCDefinition] = {}

    def register_weapon(
        self,
        key: str,
        label: str,
        factory: Callable[[], Any],
        unlock_stage: int = 0,
        tags: tuple[str, ...] = (),
    ) -> None:
        self._weapons[key] = WeaponDefinition(
            key=key,
            label=label,
            unlock_stage=unlock_stage,
            factory=factory,
            tags=frozenset(tags),
        )

    def register_spell(
        self,
        key: str,
        label: str,
        factory: Callable[[], Any],
        unlock_stage: int = 0,
        tags: tuple[str, ...] = (),
    ) -> None:
        self._spells[key] = SpellDefinition(
            key=key,
            label=label,
            unlock_stage=unlock_stage,
            factory=factory,
            tags=frozenset(tags),
        )

    def register_arena(self, key: str, label: str, factory: Callable[[], Any]) -> None:
        self._arenas[key] = ArenaDefinition(key=key, label=label, factory=factory)

    def register_npc(self, key: str, label: str, ai_factory: Callable[..., Any]) -> None:
        self._npcs[key] = NPCDefinition(key=key, label=label, ai_factory=ai_factory)

    def get_weapon(self, key: str) -> WeaponDefinition | None:
        return self._weapons.get(key)

    def get_spell(self, key: str) -> SpellDefinition | None:
        return self._spells.get(key)

    def get_arena(self, key: str) -> ArenaDefinition | None:
        return self._arenas.get(key)

    def get_npc(self, key: str) -> NPCDefinition | None:
        return self._npcs.get(key)

    def list_weapons(self) -> list[str]:
        return list(self._weapons.keys())

    def list_spells(self) -> list[str]:
        return list(self._spells.keys())

    def create_weapon(self, key: str):
        definition = self._weapons[key]
        weapon = definition.factory()
        weapon.content_key = key
        return weapon

    def create_spell(self, key: str):
        definition = self._spells[key]
        spell = definition.factory()
        spell.content_key = key
        return spell

    def create_arena(self, key: str):
        return self._arenas[key].factory()

    def create_npc_ai(self, key: str, **kwargs):
        return self._npcs[key].ai_factory(**kwargs)


CONTENT_REGISTRY = ContentRegistry()

CONTENT_REGISTRY.register_weapon("trainingblade", "Training Blade", TrainingBlade)
CONTENT_REGISTRY.register_weapon("moonslasher", "Moon Slasher", MoonSlasher)
CONTENT_REGISTRY.register_weapon("eternaltome", "Eternal Tome", EternalTome)
CONTENT_REGISTRY.register_weapon("elephanthammer", "Elephant Hammer", ElephantHammer)
CONTENT_REGISTRY.register_weapon("darkblade", "Dark Blade", DarkBlade)
CONTENT_REGISTRY.register_weapon("veyrasgrimoire", "Veyra's Grimoire", VeyrasGrimoire, unlock_stage=10)
CONTENT_REGISTRY.register_weapon("bardoksclaymore", "Bardok's Claymore", BardoksClaymore, unlock_stage=15)

CONTENT_REGISTRY.register_spell("fireball", "Fireball", Fireball)
CONTENT_REGISTRY.register_spell("nightfall", "Nightfall", Nightfall)
CONTENT_REGISTRY.register_spell("heavyshot", "Heavyshot", Heavyshot)
CONTENT_REGISTRY.register_spell("erdtreeblessing", "Erdtree Blessing", ErdtreeBlessing)
CONTENT_REGISTRY.register_spell("frostbite", "Frostbite", FrostBite)
CONTENT_REGISTRY.register_spell("veilofdarkness", "Veil of Darkness", VeilOfDarkness, unlock_stage=10)
CONTENT_REGISTRY.register_spell("earthquake", "Earthquake", Earthquake)

CONTENT_REGISTRY.register_arena("null", "Null Arena", NullArena)
CONTENT_REGISTRY.register_arena("lava", "Lava Arena", LavaArena)
CONTENT_REGISTRY.register_arena("frozen", "Frozen Arena", FrozenArena)
CONTENT_REGISTRY.register_arena("irritation", "Irritation Arena", IrritationArena)

CONTENT_REGISTRY.register_npc(
    "veyra",
    "Veyra",
    lambda **kwargs: VeyraAI(
        difficulty=kwargs.get("difficulty", "normal"),
        veyra=kwargs["fighter"],
        player=kwargs["opponent"],
    ),
)
CONTENT_REGISTRY.register_npc(
    "bardok",
    "Bardok",
    lambda **kwargs: BardokAI(
        bardok=kwargs["fighter"],
        player=kwargs["opponent"],
        stage=kwargs.get("stage", 11),
    ),
)

