from domain.shared.errors import InvalidAmountError, InvalidRecipeError

BAR_TO_ORE = {
    "copper bar": "copper ore",
    "iron bar": "iron ore",
    "silver bar": "silver ore",
}

ORE_PER_BAR = 5

def validate_smelt_amount(amount: int) -> int:
    if amount <= 0:
        raise InvalidAmountError()
    return amount

def get_required_ore(bar_name: str) -> str:
    try:
        return BAR_TO_ORE[bar_name]
    except KeyError:
        raise InvalidRecipeError(bar_name)


def required_ore_amount(amount: int) -> int:
    return ORE_PER_BAR * amount