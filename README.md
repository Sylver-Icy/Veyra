<img src="banner.png"  width="100%" />

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Status](https://img.shields.io/badge/Status-WIP-yellow)
![License](https://img.shields.io/badge/License-MIT-green)
![Built With Love](https://img.shields.io/badge/Built%20With-Love-purple)


# :gear: Veyra — The Discord Bot That Does It All (WIP)

> **Modular. Intelligent. Beautifully Over-engineered.**

Veyra isn’t *a* Discord bot — she’s an entire ecosystem.  
A self-learning, AI-integrated, event-driven framework that combines utility, RPG systems, social simulation, and procedural dialogue — all designed to feel alive inside your server.

---

## :rocket: Core Features

| Module | Status | Description |
|:--------|:--------:|:------------|
| :speech_balloon: **AI Chat & Companions** | :gear: WIP | GPT-based SFW chat + Kobold AI sandbox for uncensored fun. Each user builds a unique bond with Veyra. |
| :moneybag: **Economy & Marketplace** | :white_check_mark: | Dynamic economy with rarity tiers, player-driven trading, and fluctuating shop prices. |
| :video_game: **Mini-Games & Events** | :white_check_mark: | Wordle, delivery runs, reaction duels, and timed global events. Instant dopamine. |
| :school_satchel: **Inventory System** | :white_check_mark: | Track, trade, and flex hundreds of collectible items — all procedurally generated. |
| :person_standing: **Friendship System** | :white_check_mark: | Talk, gift, and level up your relationship with Veyra. Unlock new dialogue and perks. |
| :coin: **Work & Mining** | :white_check_mark: | Generate resources, find rare ores, and fuel the economy. |
| :jigsaw: **Gacha RPG** | :white_check_mark: | PvP arena, mana-based combat, spell mechanics, and base building. |
| :hammer: **Moderation Tools** | :gear: WIP | AI-powered NSFW classifier, auto-warns, and anti-spam — protects servers intelligently. |
| :brain: **Procedural Dialogue Engine** | :white_check_mark: | Slot-based response generator ensuring no two interactions feel the same. |

---

## :toolbox: Built With
- **Language:** Python 3.11  
- **Libraries:** Pycord, SQLAlchemy ORM  
- **Database:** PostgreSQL  
- **Extras:** Tenor API (GIFs), async event logic, full modular cog system  

---

## :bulb: Design Philosophy

Most bots are:
> :x: Bloated • :x: Shallow • :x: Boring

Veyra is:
> :white_check_mark: Alive • :white_check_mark: Modular • :white_check_mark: Smart 

She’s built like a **product**, not a script — architected for high uptime, plug-and-play features, and expandable AI logic.

---

## :brain: What Makes Veyra Special
- Dynamic dialogue system using weighted slot selection (no repetition, human-like variance)  
- Global economy loop balancing inflation + rarity  
- Real social systems (friendship XP, personality memory)  
- Codebase structured for scaling — new modules can be added without rewriting a line of core logic  
- 100% asynchronous, event-driven backend  

---

## :chart_with_upwards_trend: Vision

Veyra’s goal isn’t just to *automate Discord servers.*  
It’s to **simulate a living world inside one** — economy, relationships, stories, and personalities — all in one modular AI shell.

---

## :test_tube: Setup (for Developers)

```bash
git clone https://github.com/Sylver-Icy/Veyra.git
cd Veyra
pip install -r requirements.txt

# Add your Discord token + PostgreSQL credentials to .env and responses.txt
python veyra.py
