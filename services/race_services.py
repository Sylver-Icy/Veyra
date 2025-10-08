"""
This module handles the animal race game logic, including race progression, hype message generation,
betting system management, and reward distribution.
"""

import asyncio
import random
from utils.embeds.animalraceembed import create_race_embed, create_final_embed
from services.economy_services import add_gold
import time

async def start_race(ctx):
    """
    Starts and manages the animal race, updating positions, sending hype messages,
    and declaring the winner with reward distribution.

    Args:
        ctx: The context object for sending messages and embeds.
    """
    # Initialize animals and their positions
    animals = ["🐇", "🐢", "🦊"]
    emoji_to_name = {
        "🐇": "rabbit",
        "🐢": "turtle",
        "🦊": "fox"
    }
    positions = {a: 0 for a in animals}
    finish_line = 30

    # Send initial race embed message
    message = await ctx.send(embed=create_race_embed(positions))

    last_leader = None
    hype_set = set()

    while True:
        # Wait before next movement update
        await asyncio.sleep(4)

        # Random movement for each animal
        for a in animals:
            positions[a] += random.randint(1, 4)
            if positions[a] >= finish_line:
                break  # Stop if any animal reaches finish line

        # Update race embed with new positions
        await message.edit(embed=create_race_embed(positions))

        # Check if any animal has won the race
        for a in animals:
            if positions[a] >= finish_line:
                winner = emoji_to_name[a]
                # Show final embed with winner
                await message.edit(embed=create_final_embed(positions, winner))
                # Distribute rewards to bettors
                await distribute_rewards(ctx, winner)
                return

        # Determine current leader based on positions
        sorted_animals = sorted(positions.items(), key=lambda x: x[1], reverse=True)
        leader = sorted_animals[0][0]

        # Send hype message if leader changes or randomly with 25% chance
        if leader != last_leader or random.random() < 0.25:
            hype = generate_hype(positions)
            # Avoid repeating the same hype message consecutively
            if hype not in hype_set:
                hype_set.add(hype)
                await ctx.send(hype)
            last_leader = leader


def generate_hype(positions):
    """
    Generates a hype message based on current race positions and differences.

    Args:
        positions (dict): Current positions of each animal emoji.

    Returns:
        str: A hype message string.
    """
    sorted_animals = sorted(positions.items(), key=lambda x: x[1], reverse=True)
    leader, second, third = sorted_animals[0][0], sorted_animals[1][0], sorted_animals[2][0]
    diff = positions[leader] - positions[second]

    funny_lines = [
        f"{leader} going fast 💨",
        f"{second} is trying to drift into the lead 🚗💨",
        "A flying banana hits the track! 🍌 Chaos!",
        f"Can {third} make a comeback???",
        f"Hmm should we count {third} out of race?",
        f"{leader} just looked back and winked 😏",
        "Commentators are losing their minds right now 🎙️🫨",
        f"{leader} tripped but recovered like a pro 💥",
        "Someone’s grandma just shouted 'Run!' and they listened 🧓📢",
        "Is that... steroids?! 🚫🏃‍♂️ (jk, clean race)",
        f"{second} is drafting for that slingshot move 🚴‍♂️💨",
        "What in the Mario Kart is happening right now? 🎮🚀",
    ]

    # Competitive lines for close races
    close_lines = [
        f"It's neck and neck between {leader} and {second}! 😱",
        "This race is tighter than my jeans after pizza night😩",
        f"{leader} and {second} are giving us a show!",
        f"GOOO! {second} you can take the lead!!",
        f"Run faster {leader} don't let {second} take the spot",
        f"OMGGGGG its getting so close between {leader} and {second}"
    ]

    # Lines for dominant leader scenarios
    dominant_lines = [
        f"{leader} is dominating the track! 🏎️💨",
        f"{leader} said 'BYE 👋' and zoomed off!",
        f"{leader} is cooking🔥 — the others better wake up!"
    ]

    if diff > 5:
        return random.choice(dominant_lines)
    elif diff < 2:
        return random.choice(close_lines)
    else:
        return random.choice(funny_lines)


# ---------------------------------
# BETTING SYSTEM & REWARD LOGIC
# ---------------------------------

# Dictionary to hold bets per animal, mapping user_id to bet amount
bets = {
    "fox": {},
    "rabbit": {},
    "turtle": {}
}

def add_bets(user_id, animal, amount):
    """
    Adds a bet for a user on a specified animal if they haven't already bet.

    Args:
        user_id (int): The ID of the user placing the bet.
        animal (str): The animal to bet on ('fox', 'rabbit', or 'turtle').
        amount (int): The amount of gold being bet.

    Returns:
        bool: True if bet was successfully added, False if user already bet or animal unknown.
    """
    # Prevent duplicate bets by checking all animals
    for animal_bets in bets.values():
        if user_id in animal_bets:
            return False
    if animal in bets:
        bets[animal][user_id] = amount
        return True
    else:
        print("Unknown animal!")
        return False


def reset_bets():
    """
    Clears all bets from the betting pool.
    """
    for animal in bets:
        bets[animal].clear()


def get_total_prize(bets):
    """
    Calculates the total prize pool from all bets.

    Args:
        bets (dict): Dictionary of bets per animal.

    Returns:
        int: The sum of all bet amounts.
    """
    total = 0
    for animal_bets in bets.values():
        total += sum(animal_bets.values())
    return total


async def distribute_rewards(ctx, winning_animal):
    """
    Distributes rewards to users who bet on the winning animal.

    Args:
        ctx: The context object for sending messages.
        winning_animal (str): The animal that won the race.
    """
    total_prize_pool = get_total_prize(bets)
    effective_prize_pool = int(total_prize_pool * 0.9)  # 10% cut taken by system

    total_winning_animal_bets = sum(bets[winning_animal].values())
    if total_winning_animal_bets == 0:
        await ctx.send("No one bet on the winning animal this time lol lol")
        reset_bets()
        return

    users_payout = {}
    # Calculate payout proportionally based on bet amount
    for winner, bet_amount in bets[winning_animal].items():
        payout = int(effective_prize_pool * (bet_amount / total_winning_animal_bets))
        add_gold(winner, payout)
        users_payout[winner] = (int(bet_amount), payout)

    # Compose and send results message
    lines = [f"🏆 **Race Results - {winning_animal.capitalize()} Wins!** 🏆\n"]
    for user_id, (bet, payout) in users_payout.items():
        payout_percent = int((payout / bet) * 100) if bet > 0 else 0
        lines.append(f"<@{user_id}> bet **{bet}** gold and won **{payout}** gold (**{payout_percent}%** return!) 💰🔥")

    message = "\n".join(lines)
    await ctx.send(message)

    # Reset bets after payout
    reset_bets()
