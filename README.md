# ✨ Veyra — The Discord Bot That Does It All (WIP)

> Why settle for 10 bots... when you can have **one** that does it better?

Veyra’s a modular Discord bot I’m building with a bunch of fun, useful, and just plain chaotic features — like **moderation**, **economy**, **RPG**, and **mind-blowing minigames** — all running on a production-grade codebase.  
More features coming soon… because I can’t stop adding stuff T-T

---

## 🚀 What Can Veyra Do (as of now)?

| Feature        | Status   | Description                                                                 |
|----------------|----------|-----------------------------------------------------------------------------|
| 💬 AI Chat     | ⚙️ WIP    | NSFW-safe routing, GPT for SFW, Kobold AI for wild mode                     |
| 🎮 Mini-Games  | ✅        | Wordle Solver + Hinting, Reaction games, and more incoming                  |
| 📈 Leveling    | ✅        | EXP system with custom rewards, roles, gifs and progression tracking        |
| 💰 Economy     | ✅        | Gold system, shop, inventory, lootboxes, marketplace (soon™)                |
| 🧩 Gacha RPG    | ⚙️ Soon  | PvP battles, card placement mechanics, spells, and base building            |
| 🔨 Moderation  | ⚙️ WIP    | Custom NSFW classifier to auto mod creeps                                   |

---

## 🧠 Tech Stack

- **Python 3.11**
- **[Pycord](https://docs.pycord.dev/)** – latest build
- **PostgreSQL + SQLAlchemy ORM**
- **Tenor API (for gifs)** & custom async logic
- Full modular cog architecture – no spaghetti allowed

---

## 💡 Why Veyra Exists

Most bots are:
- ❌ Limited
- ❌ Ugly
- ❌ Dumb
- ❌ Overpriced
Veyra is:
- ✅ All-in-one
- ✅ Built like a real product
- ✅ Actually fun

She’s a **Discord-native experiment** in modular bot design, scalable AI integration, and unhinged creativity.  

Oh... and she roasts you if you mess up commands.

---

## 📸 Screenshots

> Coming soon

---

## 🧪 Wanna Help?

Pull requests? Ideas? Wanna test new chaos features?
> **DM me on Discord(`sylver.icy`)** or open an issue.

---

## ⭐ Show Some Love

If you like the idea,  
**star the repo**,  
share it with your server.


---

## 🛠️ Setup

> This ain’t plug-and-play (yet), but if you know your way around Python and Discord bots:

```bash
git clone https://github.com/YOUR_USERNAME/veyra
cd veyra
pip install -r requirements.txt
# Copy the sample env file and edit it with your credentials
cp veyra.env.example veyra.env
# Add your token, DB config, and start Veyra!
python veyra.py
```

You'll also need a `wordle.txt` word list in the project root. A small example is provided as `wordle.txt.example`.
