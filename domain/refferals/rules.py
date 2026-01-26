INVITE_REWARDS = {
    1:  {"type": "Iron Box", "amount": 1},
    3:  {"type": "Chips", "amount": 300},
    7:  {"type": "Platinum Box", "amount": 1},
    11: {"type": "role", "name": "Veyra Early Supporter"},
}

DEFAULT_REWARD = None

def get_reward_info_for_invites(num_of_invites: int):
    if num_of_invites <= 0:
        return DEFAULT_REWARD

    eligible_milestones = [
        milestone for milestone in INVITE_REWARDS.keys()
        if milestone <= num_of_invites
    ]

    if not eligible_milestones:
        return DEFAULT_REWARD

    highest_milestone = max(eligible_milestones)
    return INVITE_REWARDS[highest_milestone]