import os, json

RESPONSES = {}

def load_responses():
    folder = os.path.dirname(__file__)
    for file in os.listdir(folder):
        if file.endswith(".json"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                RESPONSES.update(data)  # merge into one big dict
    return RESPONSES

# preload once
RESPONSES = load_responses()